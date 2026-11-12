# Read only load test starter

Preparation only. This starter exercises catalogue/search HTTP responses. It does not log in, submit checkout, render pages or establish whole-app capacity by itself.

Use a separate tooling virtual environment; do not change project requirements. Tool version should be recorded. Locust's current stable documentation reviewed here is 2.47.0. From this folder, the operator can prepare tooling:

```powershell
py -3.11 -m venv .venv-nfr
.\.venv-nfr\Scripts\python.exe -m pip install locust==2.47.0
```

For the current public app, the script requires an explicit operator test-window flag before sending requests. Set it only after the developer/owner agrees the window and backup/monitoring are ready:

```powershell
$env:QA_PUBLIC_LOAD_WINDOW_CONFIRMED = 'YES'
.\.venv-nfr\Scripts\locust.exe -f locustfile_readonly.py --host https://online-bookstore-10nn.onrender.com --headless --users 1 --spawn-rate 1 --run-time 1m --csv smoke --html smoke.html
```

Review smoke results before proceeding. Run 10, then 50, 100 and 250 as separate declared stages, monitoring service and generator; do not jump to 500. Use --reset-stats for a declared steady-load sample and record that warm-up/ramp metrics were excluded. Example read-only final-stage command, only after earlier stages are healthy:

```powershell
.\.venv-nfr\Scripts\locust.exe -f locustfile_readonly.py --host https://online-bookstore-10nn.onrender.com --headless --users 500 --spawn-rate 10 --run-time 11m --reset-stats --csv browse500 --html browse500.html
```

At that spawn rate the nominal ramp takes about 50 seconds, leaving about ten minutes at 500 if reached; verify actual counts/timestamps. Retain stats/failures/history files, HTML, tool version, source SHA, resource profile, window, workload and generator logs. Stop on degradation or generator saturation. A real app failure remains a failure; do not alter thresholds/results to hide it.

The above is a catalogue/search capacity sample. Complete the reviewed authenticated/mock-checkout workload and relevant browser timing before claiming the full NFR scope. No command in this document has been executed by the agent.
