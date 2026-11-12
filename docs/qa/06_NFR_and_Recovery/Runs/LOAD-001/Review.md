# LOAD-001 local browsing smoke — stopped

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

11 November 2026. Readiness checks returned HTTP 200. The monitored one-user stage ran 04:30:10–04:31:22 UTC (10:00:10–10:01:22 IST), including ramp/warm-up and a 60-second steady sample. The operator reported no Render errors or restarts.

| Measurement | Catalogue | Search |
|---|---|---|
| Steady requests | 7 | 6 |
| Steady p90 HTTP response | 3.731 s | 4.191 s |
| Within 3 seconds | 6/7 | 3/6 |
| HTTP errors | 0 | 0 |

All fourteen load requests (including ramp/warm-up) returned HTTP 200. The original timing gate was not met, so no 10/50/100/250/500-user stage ran. Peak generator CPU was 3.1%, memory 64.72 MiB; generator saturation was not observed. These results do not demonstrate failure at 500 users or establish full normal-load acceptance.

## Independent low-rate diagnostics after stopping

Five measured browser navigations per endpoint gave p90 2.254s catalogue and 2.563s search, all below 3s. This was one browser after the load run, not a browser under 10 VUs.

Six native curl GETs returned HTTP 200. Cumulative DNS/TCP/TLS setup completion was 2.321–4.718s; TLS handshake alone (time_appconnect minus time_connect) was 1.329–2.963s. Curl was HTTP/1.1, used fresh processes, and did not reproduce the browser's connection/cache behavior. Those differences and sampling times prevent attributing the full delay to app code. A different generator network path is needed before drawing a server-capacity conclusion.

The failed gate and all raw measurements remain preserved. No threshold was relaxed. The original local process returned exit code 0 despite its Stopped summary; the future generator now propagates a nonzero result for failed/stopped gates and drains all started requests. No raw response bodies, cookies or credentials are recorded.

Next execution is the prepared QA Controlled Browsing Load workflow on a GitHub-hosted Ubuntu runner, against the same Render target. It retains the same 3-second browsing gate, request correctness checks, 1–3s think time, staged user counts, stop controls and full raw evidence. It includes a browser during the 10-VU stage. This browsing profile does not cover authenticated checkout or whole-system capacity by itself.

BOOK-NF-001 remains partial; BOOK-NF-002 remains unexecuted at 500. The case workbook's seven full NFR follow-ups remain Not run. The successful recovery rehearsal is unaffected.
