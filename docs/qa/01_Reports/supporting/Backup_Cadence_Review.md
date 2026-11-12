# Backup cadence evidence review

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

The complete public workflow history returned 28 runs: 24 successful scheduled runs (one UTC date each, 19 October–11 November), two successful manual runs and two initial manual failures. Recent 9/10/11 November jobs have successful backup and temporary restore steps plus artifact metadata. No database dump was downloaded or inspected in this review.

The configured daily schedule is evidenced. However, strict <=24h recovery-point spacing is not established: the 9 November backup step was 09:58:12–09:58:18 UTC, and the 10 November step was 10:06:42–10:06:49 UTC. Assuming each dump snapshot falls within its corresponding backup step, the interval is bounded by **24h 8m 24s to 24h 8m 37s**. No run of this workflow occurred between those two. This is a cadence finding for the configured GitHub backup mechanism; other recovery points were not supplied.

BOOK-NF-006 remains partial. Daily operation and temporary restore support are evidenced; the separate matching-application recovery rehearsal Passed within its stated CI boundary. Overall production RPO <=24h and full production outage RTO are not proven. A daily cron declaration alone cannot establish strict recovery-point age.

Operational follow-up: monitor actual completed snapshot age, alert on missing/failed backups, and choose a schedule with headroom below 24h if this mechanism must support the original strict RPO. No schedule, retention, deployment or workflow was changed by this review.

Latest inspected successful backup: https://github.com/PES-SE-online-bookstore/online-bookstore/actions/runs/42996728403. Original metadata and initial failures are retained alongside this review.
