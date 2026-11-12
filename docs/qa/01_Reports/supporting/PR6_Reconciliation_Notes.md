# Documentation PR reconciliation

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

The following changes reconcile the developer's documentation PR with the final QA packet; no application change or fresh test execution is included.

| Item | Disposition |
|---|---|
| Four reports/raw CI support | Refreshed consistently to final run 43241415099 and source 92247d3; curated reports labelled as compilations |
| Detailed cases/RTM | Existing 373-row workbook and 31-requirement mappings copied unchanged;368 Passed, 2 Failed, 3 Not run |
| Developer 32 scenarios | Preserved as summary rows with a new detailed-register crosswalk |
| Developer 12 deviations | IDs/reasons and outstanding decision statuses retained; D-09–D-12/current evidence reconciled |
| Seller decision notification (D-07) | Developer-documented unimplemented gap. Approval/visibility passes do not establish the missing notification criterion |
| Application request throttling (D-08) | Developer-documented unimplemented gap; account lockout is separate evidence |
| PDF reconciliation | Original PDFs unchanged. Team must apply actual revisions/status/decision records if required by evaluation; no approval/signature is invented |
| Videos | Required1- and 2-minute videos are not supplied by this QA update |
| Demo/presentation | Working demo and 15-minute presentation remain separate project deliverables |
| Board | README links Jira. Evaluation checklist's GitHub Project requirement remains to be reconciled; Jira use is not automatically equivalent |
| Publication | User must apply, commit/push to existing PR #6, verify CI and merge |

Scoped QA execution completion is distinct from satisfying every original acceptance criterion or completing all evaluation artifacts. The local registration error-reference reproduction is not a confirmed deployed defect; live target existence is user-reported and speech remains unverified.

No database dump, credentials, raw request logs, application source changes or Git mutations are included. Original case outcomes are not changed to hide findings. The developer's root README changes remain untouched.
