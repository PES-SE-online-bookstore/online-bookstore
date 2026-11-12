# Backup/recovery — next execution step

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Status: twice-daily schedule prepared locally, not published or executed by the agent. Existing snapshot cadence finding remains preserved.

The sole source change is `.github/workflows/database-backup.yml`: cron `30 2 * * *` becomes `30 2,14 * * *` (02:30/14:30 UTC, 08:00/20:00 IST). The jobs, secrets, restore procedure, artifact retention and manual dispatch are unchanged. Twelve-hour nominal spacing adds headroom; it does not guarantee successful backup delivery. GitHub can delay/drop scheduled runs. Actual snapshot age must still be reviewed.

1. User publishes this one-file change through a new branch/PR and waits for CI. Final plans/reports should describe the new schedule only after publication is confirmed.
2. User manually runs **Daily Database Backup** on main once, preserving the successful backup and temporary restore steps. Share its workflow URL only; do not download or send the database dump.
3. User runs **QA Isolated Recovery Rehearsal** on main, with `application_sha` set to the full SHA actually live on Render and `expected_database_name` set to the actual Render database name. Last verified name was `online_bookstore_uav4`; if the database changed, read its actual database name rather than its service display name. Do not send connection URLs or credentials.
4. Download only `qa-recovery-summary-<run>.zip` and supply its path, recovery workflow URL and application SHA used.
5. Review snapshot identity, pg_dump/restore result, exact table/row integrity, restored application health/flows, recorded snapshot time and recovery timing. Compare within the stated isolated boundary. Preserve failed attempts if any; do not retry blindly.

The prior passing rehearsal used source afdb5b14 and restored to a usable buyer flow in 2.371 seconds. A fresh rehearsal attributes evidence to the current application build and current data. Neither run proves a full production outage RTO: runner provisioning, live Render redeployment and other excluded steps must not be silently included in a claim. Likewise, a fresh on-demand snapshot does not establish the historical age of every scheduled recovery point.

Final results must distinguish successful current backup/recovery checks, the schedule improvement, the historical >24h gap and any still-unverified full-production targets. No production database overwrite or live outage is required by this isolated drill.

Reference: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
