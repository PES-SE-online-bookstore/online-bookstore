"""Controlled anonymous GET-only Locust run with stage gates and stop control.

Usage: python controlled_load.py --check (offline) or --run (declared window).
The public load run is not a checkout/full-system capacity test.
"""
import os
from pathlib import Path
import site
import sys

PROJECT = Path(os.environ.get("QA_PROJECT_ROOT", Path(__file__).resolve().parents[3])).resolve()
site.addsitedir(str(PROJECT / "SE MP Git/online-bookstore/qa-results/tools/locust-libs"))
import locust  # Monkey-patch before requests/socket imports.
from locust import HttpUser, between, task
from locust.env import Environment
from locust.event import Events
import gevent
import csv
from datetime import datetime, timezone
import importlib.metadata
import json
import math
import psutil
import re
import requests
import subprocess
import time
from urllib.parse import urlparse

HOST = "https://online-bookstore-10nn.onrender.com"
RUN_ID = os.environ.get("QA_LOAD_RUN_ID", "LOAD-001")
OUT = Path(os.environ.get("QA_LOAD_OUTPUT", PROJECT / "deliverables/06_NFR_and_Recovery/Runs" / RUN_ID)).resolve()
PROFILES = [(1, 1, 60), (10, 1, 300), (50, 5, 120), (100, 10, 120), (250, 10, 120), (500, 10, 600)]
ACTIVE = None
REPORT = None
WRITER = None
CSV_FILE = None

def now():
    return datetime.now(timezone.utc).isoformat()

def p90(values):
    return sorted(values)[math.ceil(len(values) * .90)-1] if values else None

def correctness(status, url, text):
    target = urlparse(url)
    if status != 200:
        return "Expected HTTP 200; got " + str(status)
    if target.hostname != urlparse(HOST).hostname or target.path != "/books/":
        return "Unexpected destination"
    if not re.search(r"<h1[^>]*>\s*Book Catalogue\s*</h1>", text, re.I):
        return "Expected catalogue heading missing"
    return None

class ReadOnlyBuyer(HttpUser):
    host = HOST
    wait_time = between(1, 3)

    def on_start(self):
        if os.environ.get("QA_PUBLIC_LOAD_WINDOW_CONFIRMED") != "YES":
            raise RuntimeError("Public test window not confirmed")

    def checked_get(self, path, name):
        ACTIVE["requests_started"] += 1
        context = {"phase": ACTIVE["phase"], "started_users": self.environment.runner.user_count}
        with self.client.get(path, name=name, timeout=15, allow_redirects=False,
                             catch_response=True, context=context) as response:
            error = correctness(response.status_code, response.url, response.text)
            if error:
                response.failure(error)

    @task(3)
    def catalogue(self):
        self.checked_get("/books/", "catalogue_http")

    @task(2)
    def search(self):
        self.checked_get("/books/?q=QA", "search_http")

def aggregates(samples):
    output = {}
    for name in ["catalogue_http", "search_http"]:
        matching = [sample for sample in samples if sample[1] == name]
        values = [sample[2] for sample in matching if not sample[3]]
        output[name] = {"attempts": len(matching), "failures": sum(sample[3] for sample in matching),
                        "p90_ms": round(p90(values), 3) if values else None,
                        "max_ms": round(max(values), 3) if values else None,
                        "at_or_below_3000ms": sum(value <= 3000 for value in values)}
    return output

def stage_gate(stage, steady):
    metrics = aggregates(steady)
    minimum = 5 if stage["users"] == 1 else 20
    passed = (not stage.get("abort_reason") and stage.get("steady_complete", False)
              and stage.get("requests_started") == stage.get("requests_completed")
              and all(row["attempts"] >= minimum and row["failures"] == 0
                      and row["p90_ms"] is not None and row["p90_ms"] <= 3000
                      for row in metrics.values()))
    return passed, metrics

def save():
    payload = dict(REPORT)
    payload["stages"] = [{key: value for key, value in stage.items() if not key.startswith("_")}
                         for stage in REPORT["stages"]]
    temporary = OUT / "summary.tmp"
    temporary.write_text(json.dumps(payload, indent=2)+"\n", encoding="utf-8")
    temporary.replace(OUT / "summary.json")
    if CSV_FILE:
        CSV_FILE.flush()

def observe(request_type, name, response_time, response_length, response=None,
            context=None, exception=None, **kwargs):
    stage = ACTIVE
    context = context or {}
    phase = context.get("phase", stage["phase"])
    failed = exception is not None
    timestamp = time.monotonic()
    stage["_samples"].append((timestamp, name, response_time, failed, phase))
    stage["requests_completed"] += 1
    status = response.status_code if response is not None else 0
    WRITER.writerow([stage["users"], phase, now(), context.get("started_users"), request_type,
                     name, round(response_time, 3), status, failed,
                     type(exception).__name__ if exception is not None else ""])
    if failed and not stage.get("abort_reason"):
        stage["abort_reason"] = f"HTTP/correctness failure at {name}; status {status}; {type(exception).__name__}"
        stage["first_failure"] = {"endpoint": name, "status": status, "exception_type": type(exception).__name__}

def preflight():
    for endpoint in ["/health/", "/books/"]:
        item = {"path": endpoint, "started_at_utc": now()}
        started = time.monotonic()
        print("Preflight " + endpoint, flush=True)
        try:
            response = requests.get(HOST + endpoint, timeout=60 if endpoint == "/health/" else 20,
                                    allow_redirects=False)
            item.update(status=response.status_code, elapsed_ms=round((time.monotonic()-started)*1000,3),
                        server=response.headers.get("Server"), render_origin=response.headers.get("x-render-origin-server"))
            if endpoint == "/health/":
                item["healthy"] = response.status_code == 200 and response.json().get("database") == "available"
            else:
                item["healthy"] = correctness(response.status_code, response.url, response.text) is None
        except Exception as error:
            item.update(healthy=False, exception_type=type(error).__name__, elapsed_ms=round((time.monotonic()-started)*1000,3))
        REPORT["preflight"].append(item)
        save()
        if not item["healthy"]:
            return False
    return True

def run_stage(users, rate, hold):
    global ACTIVE
    stage = {"users": users, "spawn_rate_per_second": rate, "steady_target_seconds": hold,
             "warmup_seconds_after_target_reached": 10, "started_at_utc": now(), "phase": "ramp",
             "requests_started": 0, "requests_completed": 0, "max_actual_users": 0, "max_generator_cpu_percent": 0,
             "max_generator_rss_mb": 0, "_samples": [], "_steady_users": []}
    ACTIVE = stage
    REPORT["stages"].append(stage)
    environment = Environment(user_classes=[ReadOnlyBuyer], host=HOST, events=Events(), stop_timeout=17)
    environment.events.request.add_listener(observe)
    runner = environment.create_local_runner()
    environment.events.init.fire(environment=environment, runner=runner, web_ui=None)
    process = psutil.Process()
    process.cpu_percent()
    started = time.monotonic()
    target_reached = None
    steady_start = None
    last_latency_check = started
    latency_breaches = 0
    cpu_breaches = 0
    browser = None
    browser_log = None
    print(f"Starting stage {users} users; {hold}s steady sample", flush=True)
    runner.start(users, spawn_rate=rate)
    try:
        while True:
            gevent.sleep(1)
            clock = time.monotonic()
            actual = runner.user_count
            stage["current_actual_users"] = actual
            cpu = process.cpu_percent()
            rss = process.memory_info().rss / 1024**2
            stage["max_actual_users"] = max(stage["max_actual_users"], actual)
            stage["max_generator_cpu_percent"] = max(stage["max_generator_cpu_percent"], cpu)
            stage["max_generator_rss_mb"] = round(max(stage["max_generator_rss_mb"], rss),2)
            if target_reached is None and actual == users:
                target_reached = clock
                stage["target_reached_at_utc"] = now()
                stage["phase"] = "warmup"
            if target_reached is not None and steady_start is None and clock-target_reached >= 10:
                steady_start = clock
                stage["phase"] = "steady"
                stage["steady_started_at_utc"] = now()
                if users == 10 and os.environ.get("QA_LOAD_BROWSER_SCRIPT"):
                    save()
                    browser_log = (OUT / "browser-process.log").open("w",encoding="utf-8")
                    browser = subprocess.Popen([os.environ["QA_NODE_EXECUTABLE"], os.environ["QA_LOAD_BROWSER_SCRIPT"]],
                                               stdout=browser_log, stderr=browser_log)
                    stage["measurement_browser_started"] = True
            if steady_start is not None:
                stage["steady_elapsed_seconds"] = round(clock-steady_start,3)
                stage["_steady_users"].append(actual)
                if actual != users:
                    stage["abort_reason"] = "Target active-user count was not sustained"
            if (OUT / "STOP").exists():
                stage["abort_reason"] = "Operator stop requested"
            if browser is not None:
                browser_result = OUT / "browser/results.json"
                if browser_result.exists():
                    try:
                        browser_status = json.loads(browser_result.read_text(encoding="utf-8"))
                        if browser_status.get("errors") or browser_status.get("status", "").startswith(("Stopped", "Failed")):
                            stage["abort_reason"] = "Measurement browser reported navigation/timing failure; see browser evidence"
                    except (ValueError, OSError):
                        pass
                if browser.poll() is not None and browser.returncode != 0:
                    stage["abort_reason"] = "Measurement browser failed; see browser evidence"
            cpu_breaches = cpu_breaches+1 if cpu >= 90 else 0
            if cpu_breaches >= 5 or rss > 1024:
                stage["abort_reason"] = "Load generator resource limit reached; capacity evidence inconclusive"
            if target_reached is None and clock-started > users/rate + 30:
                stage["abort_reason"] = "Target users not reached within ramp limit"
            if clock-last_latency_check >= 10 and stage["phase"] == "steady":
                recent = aggregates([sample for sample in stage["_samples"] if sample[0] >= clock-30])
                breached = any(row["attempts"] >= 20 and row["p90_ms"] is not None and row["p90_ms"] > 3000
                               for row in recent.values())
                latency_breaches = latency_breaches+1 if breached else 0
                if latency_breaches >= 3:
                    stage["abort_reason"] = "Sustained HTTP p90 above 3000ms"
                last_latency_check = clock
            stage["elapsed_seconds"] = round(clock-started,3)
            save()
            if stage.get("abort_reason"):
                break
            if steady_start is not None and clock-steady_start >= hold:
                stage["steady_complete"] = True
                break
    finally:
        stage["phase"] = "stopping"
        runner.quit()
        if stage["requests_started"] != stage["requests_completed"]:
            stage["abort_reason"] = "Some started requests did not complete; results inconclusive"
        if browser is not None:
            if browser.poll() is None:
                browser.terminate()
                try: browser.wait(timeout=10)
                except subprocess.TimeoutExpired: browser.kill(); browser.wait(timeout=10)
            browser_log.close()
            browser_result = OUT / "browser/results.json"
            if browser_result.exists():
                stage["measurement_browser"] = json.loads(browser_result.read_text(encoding="utf-8"))
                summaries = stage["measurement_browser"].get("summaries", [])
                if (stage["measurement_browser"].get("status") != "Passed declared normal-load browser sample"
                        or len(summaries) != 2
                        or not all(row.get("samples") == 20 and row.get("sample_target_met")
                                   and row.get("p90_load_ms", 1e9) <= 3000 for row in summaries)):
                    stage["abort_reason"] = "Normal-load browser measurement did not pass"
            else:
                stage["abort_reason"] = "Normal-load browser measurement produced no result"
        steady = [sample for sample in stage["_samples"] if sample[4] == "steady"]
        passed, metrics = stage_gate(stage, steady)
        stage["steady_metrics"] = metrics
        stage["all_phase_metrics"] = aggregates(stage["_samples"])
        stage["steady_min_actual_users"] = min(stage["_steady_users"]) if stage["_steady_users"] else None
        stage["status"] = "Passed scoped browsing stage" if passed else "Stopped / target not demonstrated"
        stage["finished_at_utc"] = now()
        stage["phase"] = "finished"
        save()
        print(json.dumps({key: value for key,value in stage.items() if not key.startswith("_")}), flush=True)
    return passed

def check():
    assert correctness(200, HOST+"/books/", "<h1>Book Catalogue</h1>") is None
    assert correctness(503, HOST+"/books/", "<h1>Book Catalogue</h1>")
    assert correctness(200, HOST+"/accounts/login/", "<h1>Book Catalogue</h1>")
    assert correctness(200, HOST+"/books/", "<html>Loading</html>")
    stage = {"users":10,"steady_complete":True,"requests_started":40,"requests_completed":40}
    samples = [(0,name,250,False,"steady") for name in ["catalogue_http","search_http"] for _ in range(20)]
    assert stage_gate(stage,samples)[0]
    assert not stage_gate(dict(stage,abort_reason="HTTP error"),samples)[0]
    assert not stage_gate(dict(stage,steady_complete=False),samples)[0]
    assert not stage_gate(dict(stage,requests_started=41),samples)[0]
    bad=[(0,name,4000,False,"steady") for name in ["catalogue_http","search_http"] for _ in range(20)]
    assert not stage_gate(stage,bad)[0]
    assert p90([1,2,3,4,5,6,7,8,9,100]) == 9
    print("Offline correctness/abort/incomplete-duration/latency gates Passed; zero network calls")

def main():
    global REPORT, CSV_FILE, WRITER
    if "--check" in sys.argv:
        check(); return
    if "--run" not in sys.argv or os.environ.get("QA_PUBLIC_LOAD_WINDOW_CONFIRMED") != "YES":
        raise SystemExit("Use --run only during the declared monitored test window")
    if (OUT / "summary.json").exists():
        raise SystemExit("Run output exists; preserve results rather than overwrite")
    OUT.mkdir(parents=True,exist_ok=True)
    reported_sha = os.environ.get("QA_REPORTED_DEPLOYED_SHA")
    if reported_sha and not re.fullmatch(r"[0-9a-fA-F]{40}", reported_sha):
        raise SystemExit("Reported deployed SHA must be a full 40-character commit")
    REPORT = {"run_id":RUN_ID, "started_at_utc":now(), "target":HOST,
       "status":"Running", "locust_version":locust.__version__, "python":sys.version,
       "package_versions":{name:importlib.metadata.version(name) for name in ["locust","gevent","requests","psutil"]},
       "readiness":"User reports Render logs open and ready; permissions assumed per user instruction",
       "reported_deployed_sha":reported_sha,
       "harness_commit":os.environ.get("GITHUB_SHA"),
       "github_run_id":os.environ.get("GITHUB_RUN_ID"),
       "runtime_sha_verification":"Deployment SHA is operator supplied; the application does not expose a build identifier",
       "workload":"Anonymous catalogue/search HTML GET only; 3:2 random task weighting; 1-3s think time",
       "measurement":"HTTP request timing, not rendered browser page timing; independent sessions per virtual user",
       "instrumentation_browser":"Up to one additional sequential browser may measure page loads during the 10-VU stage; report its traffic separately (10 VUs plus one measurement browser).",
       "latency_gate":"p90 <=3000ms per browsing endpoint; comparison to one-user baseline will also be reported. This is an operational stop/acceptance threshold, not proof of every interpretation of no degradation.",
       "profiles":[{"users":u,"spawn_rate":r,"steady_seconds":s} for u,r,s in PROFILES],
       "stop_conditions":["Any HTTP/timeout/correctness error","Sustained p90>3000ms","Generator saturation","Operator STOP file"],
       "limitations":["No authenticated checkout workload","Not a full-system 500-user acceptance test",
                       "Current public deployed SHA not exposed by app; last reviewed application baseline afdb5b14",
                       "Warmup/ramp excluded only from steady metrics; all requests retained in CSV",
                       "Generator resources are measured; Render resources/log observations come from operator"],
       "preflight":[], "stages":[]}
    CSV_FILE = (OUT / "requests.csv").open("w",newline="",encoding="utf-8")
    WRITER = csv.writer(CSV_FILE)
    WRITER.writerow(["stage_users","phase","utc","active_users_at_request_start","method","endpoint","response_ms","status","failed","error_type"])
    try:
        save()
        if not preflight():
            REPORT["status"] = "Stopped: readiness failed before load"
            return
        for profile in PROFILES:
            if not run_stage(*profile):
                REPORT["status"] = "Stopped: stage gate failed; higher stages not run"
                return
            gevent.sleep(5)
        REPORT["status"] = f"Passed declared {PROFILES[-1][0]}-user browsing sample; full-system capacity still unverified"
    except BaseException as error:
        REPORT["status"] = "Stopped: generator exception"
        REPORT["generator_exception_type"] = type(error).__name__
        raise
    finally:
        REPORT["finished_at_utc"] = now()
        save()
        CSV_FILE.close()
        print(REPORT["status"],flush=True)

if __name__ == "__main__":
    main()
    if REPORT is not None:
        raise SystemExit(0 if REPORT["status"].startswith("Passed declared") else 1)
