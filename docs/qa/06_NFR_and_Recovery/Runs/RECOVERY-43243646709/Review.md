# Current-build backup and scoped recovery review

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Result: **Passed within the isolated rehearsal scope.** Application source: `92247d31739eed30e0d769865869869b384a2ba6`.

| Check | Verified result |
|---|---|
| Fresh backup workflow | Run 43243243463 succeeded, including temporary PostgreSQL restore; job/step metadata verified |
| Recovery workflow | Run 43243646709 succeeded |
| Source database identity | Matched expected online_bookstore_uav4 |
| PostgreSQL commands | pg_dump/pg_restore 18.6, both exit 0 |
| Restored source integrity | All 22 tables and 258 source rows exactly matched the exported source snapshot |
| Restored application | Health, static build and all seven HTTP-flow checks Passed |
| Restore to usable buyer flow | 2.675 seconds |
| Complete probe | 15.056 seconds |
| Complete recovery CI job | 53 seconds, a separate CI observation |
| Archive provenance | ZIP CRC checked; SHA-256 matches GitHub artifact digest |

The recovery snapshot was created at 2026-11-12T15:04:06.607339+00:00. Its age at probe completion was 14.018 seconds. This is a fresh on-demand snapshot observation, not evidence about the age of every scheduled backup. The rehearsal makes its own snapshot; it does not restore the separate scheduled-backup ZIP supplied by the user.

Synthetic Order #29 was created only in the disposable restored database. No real payment or external email acceptance is claimed. Production data was not overwritten. The supplied database-backup ZIP was left unopened and was not copied into deliverables.

## Remaining limits

The twice-daily backup schedule is published (08:00/20:00 IST nominal). Actual future successful cadence still needs operational monitoring. The historical >=24h8m24s interval remains a finding. Neither fresh run establishes a historical strict RPO <=24h or the complete production outage RTO <=4h. The 2.675-second timer excludes runner provisioning and live Render redeployment; even the whole CI job is an isolated environment, not a measured production outage.

OBP48-OPS-010 is Passed in this current-build isolated scope. Other scoped NFR evidence is retained: checkout Passed; accessibility sampled assessment complete with unresolved breadcrumb; 250-user timing Failed; 500-user capacity and monthly availability Not tested. Do not label every original requirement Passed.

The remaining input for final documentation is the main CI artifact `qa-results-92247d31739eed30e0d769865869869b384a2ba6-1` from run 43241415099. It has not been inspected locally yet. No further unchanged live test is requested by this review.

Backup workflow: https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/43243243463

Recovery workflow: https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/43243646709

Artifact SHA-256: `efed1f25fcf8ddf64c2e5a108658a0ec75dad0cbd3450cc948fdd816e18d24dc`.
