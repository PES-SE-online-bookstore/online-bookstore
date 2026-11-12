# Registration accessibility — reported form results

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

Reported 12 November 2026. Browser: Firefox 159 as supplied; exact patch version, live SHA and execution timestamp were not supplied.

| Check | Result/evidence |
|---|---|
| Empty-form message and focus | Passed, user reported |
| Password mismatch rejected | User reports `Passwords do not match` and creation failed due to mismatch |
| Accessible name | Passed: `Confirm password` |
| Invalid state | Passed: supplied states explicitly include `invalid` |
| Error associated with field on live page | Follow-up screenshot confirms aria-describedby; matching target existence is user-reported. Target content/announcement not independently verified |
| Screen-reader announcement | Not tested/reported |

## Additional local finding

An actual local Django registration POST with mismatching synthetic passwords reproduced `aria-invalid="true"` and `aria-describedby="id_confirm_password_error"` on the confirm-password input. No element with that referenced ID exists. The template renders `<ul class="field-errors" role="alert">` without its corresponding ID. No account was created in the isolated test; no production database or live app was accessed.

This is a confirmed local broken reference on source 89c2168406ae355c082d143e775548bd726dfcee. It is consistent with the supplied Firefox properties, but those properties alone do not independently prove the current deployed DOM. A later user follow-up reports that the matching target exists and supplies a screenshot of the aria-describedby reference. The screenshot does not itself show the target element or message text. Preserve both evidence scopes; do not report a confirmed deployed missing-ID defect. An alert role does not prove whether a specific screen reader announces the message in this navigation; no speech result was supplied.

Follow-up recorded: `aria-describedby="id_confirm_password_error"`; `aria-errormessage` not present; target existence reported Yes. The absence of aria-errormessage alone is not a defect when aria-describedby supplies the error association. No further registration submission or product change is requested here.

The breadcrumb finding remains unresolved per the user's decision. The 13 contrast/table incomplete checks remain pending. No product code, Git state or Jira item was changed. Aggregate workbook/report updates remain pending.
