"""DRAFT: private snapshot -> isolated restore -> matching application HTTP probe.

Run from the application root. Requires PG18 clients and project dependencies.
No source INSERT/UPDATE/DELETE; the source connection is READ ONLY. Never prints
connection strings, row contents, credentials or server tracebacks. No dump is
uploaded. Review and run in the proposed disposable GitHub Actions job first.
"""
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import psycopg
from psycopg import sql
import requests

REPORT = Path(os.environ["QA_EVIDENCE_DIR"]).resolve()
REPORT.mkdir(parents=True, exist_ok=True)
started = time.monotonic()
result = {"status": "Not completed", "started_at_utc": datetime.now(timezone.utc).isoformat(),
          "source_commit": os.environ.get("QA_APP_SHA"),
          "scope": "Disposable PostgreSQL restore and local matching-app recovery rehearsal",
          "limitations": ["Does not prove historical backup intervals or month availability",
                          "Timed boundary excludes runner provisioning and production Render redeployment",
                          "No external email or real payment verification in this isolated rehearsal"]}

def require(condition, name):
    if not condition:
        raise RuntimeError(name)

def verify_source_identity(connection, expected_name, report):
    """Record only database names; keep the exact-match guard before pg_dump."""
    connected_name = connection.execute("SELECT current_database()").fetchone()[0]
    report["database_identity"] = {
        "expected_name": expected_name,
        "connected_name": connected_name,
    }
    report["source_identity_match"] = connected_name == expected_name
    require(report["source_identity_match"],
            "Source database identity does not match approved expected name")

def fingerprint(connection, key):
    """HMAC complete rows, keeping PII/hash values only in process memory."""
    tables = connection.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename").fetchall()
    output = {}
    for (table,) in tables:
        rows = connection.execute(sql.SQL("SELECT * FROM public.{}").format(sql.Identifier(table)))
        columns = [column.name for column in rows.description]
        encoded = sorted(json.dumps(row, default=str, separators=(",", ":"), ensure_ascii=False)
                         for row in rows)
        digest = hmac.new(key, digestmod=hashlib.sha256)
        digest.update(json.dumps(columns).encode())
        for row in encoded:
            digest.update(row.encode()); digest.update(b"\n")
        output[table] = {"rows": len(encoded), "hmac_sha256": digest.hexdigest()}
    return output

def pg_error_category(stderr):
    """Classify errors without publishing raw stderr, SQL rows or credentials."""
    message = stderr.decode("utf-8", errors="replace").lower()
    patterns = [
        ("server version mismatch", "client_server_version_mismatch"),
        ("unsupported version", "unsupported_archive_version"),
        ("password authentication failed", "authentication_failed"),
        ("no password supplied", "authentication_failed"),
        ("no pg_hba.conf entry", "connection_access_policy"),
        ("permission denied", "permission_denied"),
        ("invalid snapshot", "snapshot_import_failed"),
        ("snapshot identifier", "snapshot_import_failed"),
        ("set transaction snapshot", "snapshot_import_failed"),
        ("ssl", "tls_connection_failed"),
        ("could not connect", "connection_failed"),
        ("connection to server", "connection_failed"),
        ("could not translate host name", "connection_failed"),
        ("could not open output file", "backup_output_failed"),
        ("no space left", "backup_output_failed"),
        ("does not appear to be a valid archive", "invalid_backup_archive"),
        ("duplicate key", "restored_data_constraint_failed"),
        ("violates foreign key", "restored_data_constraint_failed"),
    ]
    return next((category for marker, category in patterns if marker in message),
                "unclassified_postgresql_error")

def pg_command(arguments, connection_url, report):
    tool = arguments[0]
    require(tool in {"pg_dump", "pg_restore"}, "Unexpected PostgreSQL tool")
    if tool == "pg_restore":
        target = urlparse(connection_url)
        require(target.hostname in {"localhost", "127.0.0.1"} and target.path == "/qa_recovery_test",
                "Refusing non-local PostgreSQL restore")
    env = dict(os.environ, PGCONNECT_TIMEOUT="20")
    env.pop("PGDATABASE", None)
    entry = {"tool": tool}
    report.setdefault("postgres_commands", []).append(entry)
    try:
        version = subprocess.run([tool, "--version"], capture_output=True, timeout=10)
        match = re.search(rb"\(PostgreSQL\)\s+([0-9.]+)", version.stdout)
        entry["client_version"] = match.group(1).decode() if match else "not identified"
        # Explicit --dbname also selects pg_restore's direct database-restore mode.
        # No shell is used, and the private command/connection URL is never logged.
        command = [tool, "--dbname", connection_url, "--no-password", *arguments[1:]]
        completed = subprocess.run(command, env=env, capture_output=True, timeout=600)
        entry["exit_code"] = completed.returncode
        if completed.returncode:
            entry["error_category"] = pg_error_category(completed.stderr)
            raise RuntimeError(tool + " failed (" + entry["error_category"] + "); raw diagnostics not published")
        entry["status"] = "Passed"
    except subprocess.TimeoutExpired:
        entry["error_category"] = "command_timeout"
        raise RuntimeError(tool + " timed out; private command not published") from None
    except OSError:
        entry["error_category"] = "tool_could_not_start"
        raise RuntimeError(tool + " could not start") from None

server = None
try:
    source_url, target_url = os.environ["DATABASE_URL"], os.environ["QA_RESTORE_URL"]
    target = urlparse(target_url)
    require(target.hostname in {"localhost", "127.0.0.1"} and target.path == "/qa_recovery_test",
            "Restore target guard failed")
    require(urlparse(source_url).hostname not in {"localhost", "127.0.0.1"}, "Source must be the approved remote database")
    key = secrets.token_bytes(32)
    with tempfile.TemporaryDirectory(prefix="bookstore-recovery-") as private_dir:
        dump = Path(private_dir) / "snapshot.dump"
        with psycopg.connect(target_url, autocommit=True) as restored:
            restored.execute("SET TIME ZONE 'UTC'")
            require(restored.execute("SELECT count(*) FROM pg_tables WHERE schemaname='public'").fetchone()[0] == 0,
                    "Restore target is not empty; refusing to modify it")
        with psycopg.connect(source_url, autocommit=True) as source:
            source.execute("SET TIME ZONE 'UTC'")
            source.execute("BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY")
            verify_source_identity(source, os.environ["QA_EXPECTED_DB_NAME"], result)
            result["source_postgresql_version_num"] = source.info.server_version
            snapshot = source.execute("SELECT pg_export_snapshot()").fetchone()[0]
            result["snapshot_at_utc"] = datetime.now(timezone.utc).isoformat()
            baseline = fingerprint(source, key)
            require(all(name in baseline for name in ("orders_order", "orders_orderitem", "orders_payment", "books_book")),
                    "Expected application tables missing")
            require(baseline["orders_order"]["rows"] > 0 and baseline["orders_payment"]["rows"] > 0,
                    "No baseline orders/payments; cannot establish recovery integrity")
            pg_command(["pg_dump", "--format=custom", "--no-owner", "--no-acl",
                        "--snapshot=" + snapshot, "--file=" + str(dump)], source_url, result)
            source.execute("ROLLBACK")
        require(dump.stat().st_size > 0, "Backup empty")
        result["backup_bytes"] = dump.stat().st_size
        result["backup_sha256"] = hashlib.sha256(dump.read_bytes()).hexdigest()
        result["restore_started_at_utc"] = datetime.now(timezone.utc).isoformat()
        restore_start = time.monotonic()
        pg_command(["pg_restore", "--no-owner", "--no-acl", "--exit-on-error", str(dump)], target_url, result)
        with psycopg.connect(target_url, autocommit=True) as restored:
            restored.execute("SET TIME ZONE 'UTC'")
            actual = fingerprint(restored, key)
        result["table_comparison"] = {table: {"rows": info["rows"], "exact_match": actual.get(table) == info}
                                      for table, info in baseline.items()}
        require(actual == baseline, "Snapshot/restore data mismatch")
        result["snapshot_integrity_match"] = True
        os.environ["DJANGO_SETTINGS_MODULE"] = "qa_recovery_settings"
        sys.path.insert(0, str(Path.cwd()))
        import django
        django.setup()
        from django.contrib.auth import get_user_model
        from django.test import Client
        from accounts.models import Profile
        from books.models import Book
        from orders.models import Order, Payment

        # This account, password and listing exist only in the restored disposable DB.
        password = secrets.token_urlsafe(32)
        user = get_user_model().objects.create_user("qa_recovery_" + secrets.token_hex(5), password=password)
        Profile.objects.update_or_create(user=user, defaults={"role": Profile.Role.BUYER})
        book = Book.objects.create(title="Isolated QA recovery fixture", author="QA", isbn="999"+str(time.time_ns())[-10:],
                                   price="1.00", stock_quantity=2, is_available=True,
                                   approval_status=Book.ApprovalStatus.APPROVED)
        server_env = dict(os.environ)
        # Never pass the remote URL or provider credentials to the recovered web server.
        for name in list(server_env):
            if name == "DATABASE_URL" or any(part in name for part in ("GMAIL", "SMTP", "EMAIL_API", "OAUTH")):
                server_env.pop(name, None)
        with (Path(private_dir) / "server.log").open("w") as log:
            server = subprocess.Popen([sys.executable, "manage.py", "runserver", "127.0.0.1:8765", "--noreload"],
                                      env=server_env, stdout=log, stderr=log)
            session = requests.Session()
            origin = "http://127.0.0.1:8765"
            for _ in range(60):
                try:
                    response = session.get(origin + "/health/", timeout=2)
                    if response.status_code == 200 and response.json().get("database") == "available":
                        break
                except (requests.RequestException, ValueError):
                    pass
                require(server.poll() is None, "Recovered application exited")
                time.sleep(1)
            else:
                raise RuntimeError("Recovered application not healthy within 60 seconds")
            result["restored_http_health"] = True
            def get(url):
                response = session.get(origin + url, timeout=20)
                require(response.status_code == 200, "Recovered GET failed")
                return response
            def post(url, values):
                values = dict(values, csrfmiddlewaretoken=session.cookies.get("csrftoken"))
                response = session.post(origin + url, data=values, headers={"Referer": origin + url}, timeout=20)
                require(response.status_code == 200, "Recovered POST failed")
                return response
            get("/accounts/login/")
            post("/accounts/login/", {"username": user.username, "password": password})
            require("sessionid" in session.cookies, "Recovered login failed")
            get("/books/")
            post(f"/cart/add/{book.pk}/", {"quantity": "1"})
            get("/cart/checkout/")
            post("/cart/checkout/", {"use_new_address": "yes", "payment_method": "TEST_CARD",
                 "full_name": "Recovery QA", "address_line_1": "Isolated test", "city": "Test",
                 "state": "Test", "postal_code": "000000", "country": "Test", "phone_number": "0000000000"})
            order = Order.objects.get(user=user)
            require(order.total_amount == 1 and order.items.get().quantity == 1, "Recovered checkout order incorrect")
            require(Payment.objects.filter(order=order, amount=1, status="PENDING").exists(), "Recovered mock payment incorrect")
            get(f"/orders/{order.pk}/")
            result["recovered_buyer_login_cart_mock_checkout_history"] = True
            result["rehearsal_restore_to_usable_seconds"] = round(time.monotonic() - restore_start, 3)
            require(result["rehearsal_restore_to_usable_seconds"] <= 14400, "Recovery exceeded four hours")
            result["status"] = "Passed scoped recovery rehearsal"
except Exception as error:
    # Print only our controlled check messages, never third-party exception strings.
    result["status"] = "Failed"
    result["failure"] = str(error) if type(error) is RuntimeError else type(error).__name__
finally:
    if server is not None:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill(); server.wait(timeout=10)
    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    (REPORT / "recovery-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
sys.exit(0 if result["status"].startswith("Passed") else 1)
