# Publication notes

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Update the existing [documentation PR #6](https://github.com/PES-SE-online-bookstore/online-bookstore/pull/6), branch `docs/final-deliverables`. This documentation tree reconciles the developer's 12-deviation register and 32 scenario summaries with the final detailed QA packet. Keep the developer's root README links.

1. Review the reconciled deviation register and Test Plan addendum. The 32 summaries cross-reference the detailed register; they do not replace its 373 records.
2. Publish the four reports and raw CI support under `docs/test-reports/`, the complete sanitized QA packet under `docs/qa/`, and the reconciled `docs/README.md` and addenda in the same PR.
3. Review the staged diff, commit and push to that branch. Check the PR workflow results and merge when ready. Preserve historical failures and outstanding findings.
4. Reconcile the original SRS, SAD and Test Plan PDF contents/statuses with the actual implementation. Record actual decisions; do not invent approval records or convert untested targets to Passed.
5. Complete the separate final report and working demo/15-minute presentation. The handoff lists additional video/board items whose source is not in the available guideline; see the [reference cross-check](Original_Reference_Crosscheck.md).

Reports pin tested source `92247d31739eed30e0d769865869869b384a2ba6`; deployed/operational runs retain their individual builds. A later documentation-only commit does not create new test evidence. No database dumps, credentials or raw request logs belong in this documentation tree.
