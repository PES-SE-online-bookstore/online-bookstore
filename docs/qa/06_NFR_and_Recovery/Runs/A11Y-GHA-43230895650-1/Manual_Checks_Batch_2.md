# Manual accessibility batch 2 — remaining checks

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

The admin breadcrumb finding remains unresolved per user instruction. Do not repeat batch 1 or the unchanged automated workflow.

Record the current full deployed SHA and exact Firefox version (Help → About Firefox) if available. Record only facts you actually observed. Pass, Fail, Not verified and Not tested are valid outcomes.

## 1. Native validation and accessible form names

In a signed-out/private window, open `/accounts/register/`. Submit the empty form once. Verify that the browser identifies a required field and moves focus to it, and that the field's label identifies what must be entered. No valid account is submitted.

Use Firefox's Accessibility inspector (right-click a field → Inspect Accessibility Properties). Check that Username, Email, Password, Confirm password and Role have meaningful accessible names. Do not expose real credentials in a screenshot or report.

## 2. Server-side validation error

On registration, use an unused QA username, an address ending `@example.invalid`, Buyer role and two different strong temporary passwords. Submit once. The server should reject the mismatch and show a clear correction message; no account-creation success should appear. Do not reuse real passwords or send temporary values in the report.

Inspect Confirm password in the accessibility tree: record its accessible name, whether invalid state is exposed, and whether the mismatch message is associated as a description/relation. Merely seeing red text is not enough to establish an accessible association. If uncertain, report Not verified.

If you already use a screen reader, record its name/version and whether the error is announced or can be found by navigating the form. If you do not have/use one, report this part Not tested; do not infer speech behavior from the accessibility tree.

## 3. Contrast review queue

Firefox DevTools → Accessibility → Check for issues → Contrast can assist the review. Inspect/scroll the flagged content into view. Keep the 390px mobile layout distinct from desktop; responsive design mode can set 390px without repeating zoom tests.

| Page/state | Content needing review |
|---|---|
| Buyer `/orders/`, 390px | Order links, including below-the-fold rows |
| Buyer `/orders/9/`, desktop | Tracking markers; determine whether markers are decorative and equivalent visible status text conveys the same information |
| Admin `/admin/`, desktop and 390px | Add/Change and recent-action links/text |
| Admin `/admin/books/book/`, desktop and 390px | Sort/header, Add/View and sidebar links |
| Admin `/admin/orders/order/`, desktop and 390px | Sort/header, Add/View and sidebar links |
| Admin `/admin/orders/order/9/change/`, desktop and 390px | Flagged links; retain breadcrumb finding separately |

Record the actual ratios/Firefox findings where available. Normal text requires >=4.5:1 against its background; large text >=3:1. Purely decorative, inactive or genuinely invisible text may have applicable exceptions, but note the reason. `aria-hidden` alone is not sufficient to exempt meaningful visible text. A clean additional automated check is supporting evidence; it does not automatically resolve every original incomplete node. Leave uncertain items Not verified rather than judging by eye.

## 4. Admin table/sidebar relationships

At desktop width, inspect the model-navigation tables in the sidebar on the Books list, Orders list and Order #9 edit pages. Expand the Firefox accessibility tree. Check whether row headings/model names and the associated Add/Change links are exposed in coherent rows with meaningful names. Also inspect the actual data-list table headings on Books/Orders: headings should identify the corresponding row data.

Record the table/header/cell roles and any missing or misleading association. If the navigation is a layout table instead of a data table, record why that classification applies; do not dismiss it simply because it is Django admin. If the relationship cannot be established, report Not verified.

## Return format

```text
Current deployed SHA:
Firefox exact version:
Empty-form required-field focus and labels: Pass/Fail/Not tested
Registration field accessible names: Pass/Fail/Not verified
Password-mismatch message shown; no success: Yes/No/Not tested
Confirm-password invalid state exposed: Yes/No/Not verified
Mismatch error associated with field: Yes/No/Not verified
Screen-reader error behavior: Result + reader/version, or Not tested
Contrast: Per queue row result + actual ratios/findings, or Not verified
Admin table/header relationships: Per page result + observed roles/relationships, or Not verified
Any other issue:
```

These checks support the declared sampled audit. Remaining untested applicable WCAG criteria must remain explicit; this batch does not silently establish a complete WCAG 2.1 AA conformance claim.

References: https://firefox-source-docs.mozilla.org/devtools-user/accessibility_inspector/index.html and https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
