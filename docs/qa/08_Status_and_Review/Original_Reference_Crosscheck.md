# Original reference cross-check

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

This is a read-only comparison with the supplied SRS, SAD, Test Plan and JACKFRUIT course guideline. The original files remain unchanged. Documentation reconciliation does not supply missing acceptance evidence or signatures.

| Reference | Confirmed content | Reconciliation/action |
|---|---|---|
| SRS v1.0 | Under Review; approval row blank; email login, real payment scope, 500-user target and seller decision notifications appear in the original | Preserve recorded R-001/R-002 decisions and D-01/D-02. Keep D-07 visible. Record 500-user capacity as Not tested; a reduced execution scope does not demonstrate the original target. |
| SAD v1.0 | Draft; blank approval; REST/JWT design, seller decision notifications and request limits | D-03/D-06/D-07/D-08 retain the implementation differences and their actual decision statuses. Lockout does not establish request throttling. |
| Test Plan v1.0 | Draft; Pending approval rows; REST/JWT and Jenkins/Docker/SonarQube assumptions; cache initially excluded; core coverage target >=70% | Use the reconciled Test Plan addendum and D-09/D-10/D-12. The defined core result is 92.68%; record actual scope/tool changes and decisions. |
| Course guideline: testing | 8–10 cases per implemented functional use case; Unit/Integration/System levels; manual execution wording | Report actual hybrid execution. Mapped requirement counts alone do not establish every use case's manual execution or every acceptance criterion. No instructor waiver is supplied. |
| Course guideline: final submission | Final report sections include proposal, SRS, project plan, design diagrams, test cases and output screenshots; working demo and 15-minute presentation | QA packet supplies the testing material. Other report sections, assembled final report and delivered demo/presentation remain separate project work. |
| Course guideline: board | “Github (Jira or similar tool)” for backlog/user stories; Jira or similar for collaboration | Jira is permitted by the supplied guideline. A GitHub Project-only rule is not established by this file. |
| Additional handoff checklist | User handoff mentions 1-minute and 2-minute videos and a GitHub Project requirement | Those specific requirements were not found in the available guideline text. Treat them as additional user-reported checklist items; obtain the applicable rubric/source before claiming they are course requirements or that Jira is insufficient. No videos or extra board are claimed complete. |

Original source dates are preserved as provenance. Current report headings omit editorial cutoff dates. Update source-document content/revision records only with the actual decisions; do not mark draft sources approved merely because the QA packet is ready.

The developer's 12 deviation IDs and 32 scenario summaries remain intact. D-07 and D-08 are developer-documented implementation gaps, not new independently executed defect results. TC-Cov-01 in the scenario crosswalk points to coverage evidence and intentionally adds no fabricated case-register row.
