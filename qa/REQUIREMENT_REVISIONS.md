# Requirement and scope revisions (against SRS v1.0, 06-08-2025)

These record decisions made by QA and relayed to development in the OBP-47
handoff on 2026-11-09. Original SRS wording is quoted so the change is traceable.

## R-001 — BOOK-F-002 login identifier

- **Original SRS text:** "The system shall authenticate users via email and
  password, and issue a session/JWT token on success." AC-BOOK-F-002.
- **Revised requirement:** The system shall authenticate users via **username
  and password** and establish an authenticated Django session on success.
  Incorrect credentials are rejected. Email addresses are not accepted as login
  identifiers.
- **Reason:** The implemented login form and Django authentication backend use
  usernames; email remains a unique registered attribute (BOOK-F-001) and the
  password-reset identifier (BOOK-F-004).
- **Evidence trail:** The original email-login assertion failed in run
  20261103T063353040577Z (`qa/history/2026-11-03_run_29049b0.md`, QA-AUTH-001).
  It was replaced by
  `LoginIntegrationTests.test_revised_username_and_password_establish_session`
  and `test_email_identifier_is_not_accepted_under_revised_requirement`, which
  keep the revised behaviour explicit.
- **Status:** Decided
- **Decision authority:** Abdullah Faruqui (QA Lead); Deepthi A E (Test Engineer)
- **Decision date:** 2026-11-09
- **Source:** OBP-47 handoff message from the QA Lead to development

## R-002 — BOOK-F-010 / BOOK-SR-003 payment scope

- **Original SRS text:** BOOK-F-010 requires payment "through the payment
  gateway"; §3.3 names a Razorpay/Stripe sandbox; §2.5 constrains payments to
  sandbox/test mode.
- **Revised scope:** For this release, payment is the in-process
  `orders.services.MockPaymentGateway`. It simulates initiation only; no gateway
  call is made, no money moves, and no card data is collected or stored.
- **QA consequence:** Tests in `orders.tests.CreateOrderFromCartTests` are
  characterization of order creation with the mock (already labelled so in
  `qa/catalog.py`). They do **not** verify gateway acceptance, tokenisation
  (BOOK-SR-003) or payment-confirmation email for BOOK-F-010. Those remain
  "Not verified" until a sandbox gateway is integrated.
- **Status:** Decided
- **Decision authority:** Abdullah Faruqui (QA Lead); Deepthi A E (Test Engineer)
- **Decision date:** 2026-11-09
- **Source:** OBP-47 handoff message from the QA Lead to development
