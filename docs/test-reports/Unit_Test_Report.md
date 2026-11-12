# Unit Test Report

Source commit: `f6d7d85eb6c93599c5e0bd05f6b6560aa1e88da3`

Tracked changes: None

Run: `20261112T072332130989Z`; started: 2026-11-12T07:23:32.130978+00:00

Environment: Linux-7.0.0-1019-azure-x86_64-with-glibc2.43; Python 3.11.18

Settings: `config.settings`

Test process exit code: 0

Evidence applies to this source and test environment. The deployed version is unverified.

Executed test methods: 294; failures: 0; errors: 0; skipped: 0; expected failures: 0; unexpected successes: 0.

Only explicitly classified tests count as unit tests. Existing unclassified tests need review; request/database tests must not automatically be called unit tests.

## Unit test outcomes

| Test | Result | Seconds | Requirement IDs |
|---|---|---:|---|
| accounts.test_authentication.RegistrationValidationUnitTests.test_admin_role_cannot_be_selected | Passed | 0.001174 | BOOK-F-001, BOOK-SR-004 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_duplicate_email_is_rejected | Passed | 0.000914 | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_duplicate_username_is_rejected | Passed | 0.001195 | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_email_is_normalized | Passed | 0.000903 | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_invalid_email_is_rejected | Passed | 0.000792 | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_mismatched_password_is_rejected | Passed | 0.000903 | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_numeric_password_is_rejected | Passed | 0.000856 | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_short_password_is_rejected | Passed | 0.001105 | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_username_is_trimmed | Passed | 0.000812 | BOOK-F-001 |
| accounts.test_authentication.RegistrationValidationUnitTests.test_valid_registration_passes_validation | Passed | 0.000861 | BOOK-F-001 |
| accounts.test_database_tls.VerifyPostgresTlsCommandTests.test_fails_when_connection_is_not_encrypted | Passed | 0.004516 | BOOK-SR-001 |
| accounts.test_database_tls.VerifyPostgresTlsCommandTests.test_rejects_non_postgresql_database | Passed | 0.001268 | BOOK-SR-001 |
| accounts.test_database_tls.VerifyPostgresTlsCommandTests.test_reports_tls_version_and_cipher | Passed | 0.003515 | BOOK-SR-001 |
| config.test_email_backend.GmailAPIEmailBackendTests.test_api_failures_raise_sanitized_backend_error | Passed | 0.001977 | BOOK-F-020 |
| config.test_email_backend.GmailAPIEmailBackendTests.test_empty_message_list_does_not_make_api_requests | Passed | 0.00156 | BOOK-F-020 |
| config.test_email_backend.GmailAPIEmailBackendTests.test_fail_silently_returns_zero_on_api_failure | Passed | 0.001815 | BOOK-F-020 |
| config.test_email_backend.GmailAPIEmailBackendTests.test_missing_oauth_credentials_raise_configuration_error | Passed | 0.00156 | BOOK-F-020 |
| config.test_email_backend.GmailAPIEmailBackendTests.test_sends_email_through_gmail_https_api | Passed | 0.004123 | BOOK-F-020, BOOK-SR-001 |

## Integration test outcomes

| Test | Result | Seconds | Requirement IDs |
|---|---|---:|---|
| accounts.test_authentication.LockoutIntegrationTests.test_another_account_is_not_locked | Passed | 1.239743 | BOOK-F-003, BOOK-SR-005 |
| accounts.test_authentication.LockoutIntegrationTests.test_correct_password_is_blocked_during_lockout | Passed | 0.890803 | BOOK-F-003, BOOK-SR-005 |
| accounts.test_authentication.LockoutIntegrationTests.test_correct_password_works_after_expiry | Passed | 1.064923 | BOOK-F-003, BOOK-SR-005 |
| accounts.test_authentication.LockoutIntegrationTests.test_fifth_failure_locks_for_fifteen_minutes | Passed | 0.893857 | BOOK-F-003, BOOK-SR-005 |
| accounts.test_authentication.LockoutIntegrationTests.test_first_failure_is_counted | Passed | 0.193627 | BOOK-F-003, BOOK-SR-005 |
| accounts.test_authentication.LockoutIntegrationTests.test_four_failures_do_not_lock_account | Passed | 0.724939 | BOOK-F-003, BOOK-SR-005 |
| accounts.test_authentication.LockoutIntegrationTests.test_sixth_attempt_shows_lockout_message | Passed | 0.905741 | BOOK-F-003, BOOK-SR-005 |
| accounts.test_authentication.LockoutIntegrationTests.test_success_between_failures_resets_consecutive_count | Passed | 1.075537 | BOOK-F-003, BOOK-SR-005 |
| accounts.test_authentication.LockoutIntegrationTests.test_wrong_password_after_expiry_starts_new_count | Passed | 1.067029 | BOOK-F-003, BOOK-SR-005 |
| accounts.test_authentication.LoginIntegrationTests.test_email_identifier_is_not_accepted_under_revised_requirement | Passed | 0.191776 | BOOK-F-002 |
| accounts.test_authentication.LoginIntegrationTests.test_inactive_account_cannot_log_in | Passed | 0.203199 | BOOK-F-002, BOOK-F-017 |
| accounts.test_authentication.LoginIntegrationTests.test_login_page_loads | Passed | 0.023944 | BOOK-F-002 |
| accounts.test_authentication.LoginIntegrationTests.test_missing_credentials_are_rejected | Passed | 0.188378 | BOOK-F-002 |
| accounts.test_authentication.LoginIntegrationTests.test_revised_username_and_password_establish_session | Passed | 0.194121 | BOOK-F-002 |
| accounts.test_authentication.LoginIntegrationTests.test_unknown_account_does_not_create_attempt_record | Passed | 0.19033 | BOOK-F-002 |
| accounts.test_authentication.LoginIntegrationTests.test_wrong_password_can_be_followed_by_successful_login | Passed | 0.36735 | BOOK-F-002 |
| accounts.test_authentication.LoginIntegrationTests.test_wrong_password_does_not_establish_session | Passed | 0.198876 | BOOK-F-002 |
| accounts.test_authentication.PasswordResetIntegrationTests.test_inactive_account_receives_no_reset_message | Passed | 0.076768 | BOOK-F-004 |
| accounts.test_authentication.PasswordResetIntegrationTests.test_link_is_valid_before_thirty_minutes | Passed | 0.051851 | BOOK-F-004 |
| accounts.test_authentication.PasswordResetIntegrationTests.test_mismatched_reset_passwords_do_not_change_password | Passed | 0.20269 | BOOK-F-004 |
| accounts.test_authentication.PasswordResetIntegrationTests.test_new_password_logs_in_and_old_password_does_not | Passed | 0.557961 | BOOK-F-002, BOOK-F-004 |
| accounts.test_authentication.PasswordResetIntegrationTests.test_registered_account_receives_reset_message | Passed | 0.024119 | BOOK-F-004 |
| accounts.test_authentication.PasswordResetIntegrationTests.test_reset_request_page_loads | Passed | 0.023744 | BOOK-F-004 |
| accounts.test_authentication.PasswordResetIntegrationTests.test_srs_link_expires_after_thirty_minutes | Passed | 0.02738 | BOOK-F-004 |
| accounts.test_authentication.PasswordResetIntegrationTests.test_successful_reset_changes_password | Passed | 0.527427 | BOOK-F-004 |
| accounts.test_authentication.PasswordResetIntegrationTests.test_tampered_token_is_rejected | Passed | 0.029243 | BOOK-F-004 |
| accounts.test_authentication.PasswordResetIntegrationTests.test_unknown_email_discloses_no_account_and_sends_no_message | Passed | 0.022709 | BOOK-F-004 |
| accounts.test_authentication.PasswordResetIntegrationTests.test_used_link_cannot_be_reused | Passed | 0.206843 | BOOK-F-004 |
| accounts.test_authentication.RegistrationIntegrationTests.test_buyer_account_and_profile_are_created | Passed | 0.190152 | BOOK-F-001 |
| accounts.test_authentication.RegistrationIntegrationTests.test_duplicate_email_does_not_create_another_account | Passed | 0.201004 | BOOK-F-001 |
| accounts.test_authentication.RegistrationIntegrationTests.test_duplicate_username_does_not_create_another_account | Passed | 0.200083 | BOOK-F-001 |
| accounts.test_authentication.RegistrationIntegrationTests.test_mismatched_password_creates_no_account_or_profile | Passed | 0.030143 | BOOK-F-001 |
| accounts.test_authentication.RegistrationIntegrationTests.test_missing_required_data_creates_no_account | Passed | 0.028955 | BOOK-F-001 |
| accounts.test_authentication.RegistrationIntegrationTests.test_registration_cannot_create_an_admin | Passed | 0.029427 | BOOK-F-001, BOOK-SR-004 |
| accounts.test_authentication.RegistrationIntegrationTests.test_registration_page_loads | Passed | 0.026847 | BOOK-F-001 |
| accounts.test_authentication.RegistrationIntegrationTests.test_registration_stores_verifiable_hash_not_plaintext | Passed | 0.507665 | BOOK-F-001, BOOK-SR-002 |
| accounts.test_authentication.RegistrationIntegrationTests.test_seller_account_and_profile_are_created | Passed | 0.188607 | BOOK-F-001 |
| accounts.test_authentication.SessionAccessIntegrationTests.test_anonymous_cart_access_redirects_to_login | Passed | 0.022376 | BOOK-F-002, BOOK-SR-004 |
| accounts.test_authentication.SessionAccessIntegrationTests.test_get_logout_does_not_change_session | Passed | 0.194804 | BOOK-F-002, BOOK-SR-004 |
| accounts.test_authentication.SessionAccessIntegrationTests.test_independent_client_has_no_authenticated_session | Passed | 0.24982 | BOOK-F-002, BOOK-SR-004 |
| accounts.test_authentication.SessionAccessIntegrationTests.test_logged_in_buyer_can_access_cart | Passed | 0.210574 | BOOK-F-002, BOOK-SR-004 |
| accounts.test_authentication.SessionAccessIntegrationTests.test_login_post_without_csrf_token_is_rejected | Passed | 0.101949 | BOOK-SR-005 |
| accounts.test_authentication.SessionAccessIntegrationTests.test_logout_post_without_csrf_token_is_rejected | Passed | 0.033197 | BOOK-SR-005 |
| accounts.test_authentication.SessionAccessIntegrationTests.test_post_logout_removes_authentication | Passed | 0.204989 | BOOK-F-002, BOOK-SR-004 |
| accounts.test_authentication.SessionAccessIntegrationTests.test_protected_access_after_logout_is_denied | Passed | 0.197416 | BOOK-F-002, BOOK-SR-004 |
| accounts.tests.AdminAccountManagementTests.test_account_admin_is_registered_with_custom_admin | Passed | 0.018859 | BOOK-F-017 |
| accounts.tests.AdminAccountManagementTests.test_admin_can_deactivate_account | Passed | 0.094277 | BOOK-F-017 |
| accounts.tests.AdminAccountManagementTests.test_admin_can_deactivate_other_account_without_deactivating_self | Passed | 0.067922 | BOOK-F-017 |
| accounts.tests.AdminAccountManagementTests.test_admin_can_reactivate_account | Passed | 0.066032 | BOOK-F-017 |
| accounts.tests.AdminAccountManagementTests.test_admin_cannot_deactivate_own_account | Passed | 0.066366 | BOOK-F-017 |
| accounts.tests.AdminAccountManagementTests.test_deactivated_user_cannot_authenticate | Passed | 0.178437 | BOOK-F-017 |
| accounts.tests.AdminAccountManagementTests.test_deactivated_user_cannot_log_in | Passed | 0.212433 | BOOK-F-017 |
| accounts.tests.AdminAccountManagementTests.test_non_staff_user_cannot_access_user_admin | Passed | 0.038332 | BOOK-F-017, BOOK-SR-004 |
| books.test_catalogue_cache.CacheCspTests.test_each_cached_response_has_its_own_matching_nonce | Passed | 0.041529 | BOOK-NF-002, BOOK-SR-005 |
| books.test_catalogue_cache.CacheCspTests.test_response_is_not_marked_publicly_cacheable | Passed | 0.031507 | BOOK-NF-002, BOOK-SR-005 |
| books.test_catalogue_cache.CacheExpiryTests.test_entry_is_rebuilt_after_timeout | Passed | 0.039475 | BOOK-F-005, BOOK-NF-002 |
| books.test_catalogue_cache.CacheExpiryTests.test_entry_is_still_served_just_before_timeout | Passed | 0.030798 | BOOK-F-005, BOOK-NF-002 |
| books.test_catalogue_cache.CacheExpiryTests.test_first_request_misses_and_repeat_hits | Passed | 0.029902 | BOOK-F-005, BOOK-NF-002 |
| books.test_catalogue_cache.CacheExpiryTests.test_hit_runs_no_queries_and_miss_runs_three | Passed | 0.030587 | BOOK-F-005, BOOK-NF-002 |
| books.test_catalogue_cache.CacheExpiryTests.test_zero_seconds_disables_the_cache | Passed | 0.032195 | BOOK-F-005, BOOK-NF-002 |
| books.test_catalogue_cache.CacheInvalidationTests.test_admin_bulk_deactivate_invalidates_despite_bypassing_save | Passed | 0.217245 | BOOK-F-017, BOOK-NF-002 |
| books.test_catalogue_cache.CacheInvalidationTests.test_approving_a_pending_book_publishes_it | Passed | 0.0418 | BOOK-F-005, BOOK-NF-002 |
| books.test_catalogue_cache.CacheInvalidationTests.test_category_list_follows_new_category | Passed | 0.03453 | BOOK-F-005, BOOK-NF-002 |
| books.test_catalogue_cache.CacheInvalidationTests.test_deleting_a_book_removes_it | Passed | 0.037681 | BOOK-F-005, BOOK-NF-002 |
| books.test_catalogue_cache.CacheInvalidationTests.test_edited_title_and_price_appear_immediately | Passed | 0.03371 | BOOK-F-005, BOOK-NF-002 |
| books.test_catalogue_cache.CacheInvalidationTests.test_new_approved_book_appears_immediately | Passed | 0.035177 | BOOK-F-005, BOOK-NF-002 |
| books.test_catalogue_cache.CacheInvalidationTests.test_rejecting_a_book_removes_it_and_its_category | Passed | 0.033244 | BOOK-F-016, BOOK-NF-002 |
| books.test_catalogue_cache.CacheQuerySeparationTests.test_categories_do_not_share_entries | Passed | 0.047463 | BOOK-F-005, BOOK-F-006, BOOK-NF-002 |
| books.test_catalogue_cache.CacheQuerySeparationTests.test_different_searches_get_different_results | Passed | 0.048385 | BOOK-F-005, BOOK-F-006, BOOK-NF-002 |
| books.test_catalogue_cache.CacheQuerySeparationTests.test_invalid_and_out_of_range_pages_resolve_like_before | Passed | 0.054765 | BOOK-F-005, BOOK-F-006, BOOK-NF-002 |
| books.test_catalogue_cache.CacheQuerySeparationTests.test_pages_do_not_share_entries | Passed | 0.051935 | BOOK-F-005, BOOK-F-006, BOOK-NF-002 |
| books.test_catalogue_cache.CacheQuerySeparationTests.test_price_ranges_do_not_share_entries | Passed | 0.044978 | BOOK-F-005, BOOK-F-006, BOOK-NF-002 |
| books.test_catalogue_cache.CacheQuerySeparationTests.test_search_box_echoes_this_request_not_a_cached_one | Passed | 0.043278 | BOOK-F-005, BOOK-F-006, BOOK-NF-002 |
| books.test_catalogue_cache.CacheSessionSeparationTests.test_anonymous_hit_after_logged_in_miss_shows_no_user | Passed | 0.374814 | BOOK-NF-002, BOOK-SR-004 |
| books.test_catalogue_cache.CacheSessionSeparationTests.test_anonymous_hit_does_not_create_a_session | Passed | 0.353641 | BOOK-NF-002, BOOK-SR-004 |
| books.test_catalogue_cache.CacheSessionSeparationTests.test_cache_stores_no_user_or_session_data | Passed | 0.363654 | BOOK-NF-002, BOOK-SR-004 |
| books.test_catalogue_cache.CacheSessionSeparationTests.test_each_user_sees_own_navigation_on_shared_entry | Passed | 0.376302 | BOOK-NF-002, BOOK-SR-004 |
| books.test_catalogue_cache.CatalogueDiagnosticsTests.test_log_line_records_cache_status_and_queries_without_search_text | Passed | 0.058064 | BOOK-NF-002 |
| books.test_catalogue_cache.CatalogueDiagnosticsTests.test_server_timing_header_reports_durations | Passed | 0.027719 | BOOK-NF-002 |
| books.test_catalogue_validation.CataloguePaginationIntegrationTests.test_first_page_contains_twelve_books | Passed | 0.030589 | BOOK-F-005 |
| books.test_catalogue_validation.CataloguePaginationIntegrationTests.test_invalid_page_input_falls_back_without_error | Passed | 0.031999 | BOOK-F-005 |
| books.test_catalogue_validation.CataloguePaginationIntegrationTests.test_out_of_range_page_resolves_to_last_page | Passed | 0.02697 | BOOK-F-005 |
| books.test_catalogue_validation.CataloguePaginationIntegrationTests.test_pagination_links_preserve_encoded_search_and_filters | Passed | 0.036739 | BOOK-F-005, BOOK-F-006 |
| books.test_catalogue_validation.CataloguePaginationIntegrationTests.test_three_pages_do_not_omit_or_repeat_books | Passed | 0.045208 | BOOK-F-005 |
| books.test_catalogue_validation.CatalogueRequiredFieldsIntegrationTests.test_book_detail_displays_computed_average_rating | Passed | 0.037815 | BOOK-F-007 |
| books.test_catalogue_validation.CatalogueRequiredFieldsIntegrationTests.test_srs_book_detail_identifies_seller | Passed | 0.029085 | BOOK-F-007 |
| books.test_catalogue_validation.CatalogueRequiredFieldsIntegrationTests.test_srs_catalogue_renders_book_cover_image | Passed | 0.02838 | BOOK-F-005 |
| books.test_catalogue_validation.CatalogueVisibilityIntegrationTests.test_pending_book_is_inaccessible_by_direct_url | Passed | 0.059698 | BOOK-F-007, BOOK-F-016 |
| books.test_catalogue_validation.CatalogueVisibilityIntegrationTests.test_rejected_book_is_inaccessible_by_direct_url | Passed | 0.023041 | BOOK-F-007, BOOK-F-016 |
| books.test_catalogue_validation.CatalogueVisibilityIntegrationTests.test_unapproved_books_and_their_categories_are_hidden | Passed | 0.02722 | BOOK-F-005, BOOK-F-016 |
| books.test_rbac.ReviewRolePermissionTests.test_anonymous_user_must_log_in_to_submit_review | Passed | 0.51138 | BOOK-F-018, BOOK-SR-004 |
| books.test_rbac.ReviewRolePermissionTests.test_buyer_with_purchase_can_submit_review | Passed | 0.561261 | BOOK-F-018, BOOK-SR-004 |
| books.test_rbac.ReviewRolePermissionTests.test_buyer_with_purchase_sees_review_form | Passed | 0.534789 | BOOK-F-018, BOOK-SR-004 |
| books.test_rbac.ReviewRolePermissionTests.test_seller_cannot_submit_review_even_after_purchase | Passed | 0.536421 | BOOK-F-018, BOOK-SR-004 |
| books.test_rbac.ReviewRolePermissionTests.test_seller_does_not_see_review_form_on_book_details | Passed | 0.560582 | BOOK-F-018, BOOK-SR-004 |
| books.test_rbac.ReviewRolePermissionTests.test_user_without_profile_cannot_submit_review | Passed | 0.532806 | BOOK-F-018, BOOK-SR-004 |
| books.test_security.SecurityRequestIntegrationTests.test_anonymous_wishlist_access_requires_login | Passed | 0.021474 | BOOK-F-019, BOOK-SR-004 |
| books.test_security.SecurityRequestIntegrationTests.test_get_requests_cannot_add_or_remove_wishlist_entries | Passed | 0.038884 | BOOK-F-019, BOOK-SR-005 |
| books.test_security.SecurityRequestIntegrationTests.test_login_post_with_valid_csrf_authenticates | Passed | 0.201847 | BOOK-SR-005 |
| books.test_security.SecurityRequestIntegrationTests.test_login_post_without_csrf_is_rejected | Passed | 0.02644 | BOOK-SR-005 |
| books.test_security.SecurityRequestIntegrationTests.test_login_rotates_pre_authentication_session | Passed | 0.198876 | BOOK-F-002, BOOK-SR-004 |
| books.test_security.SecurityRequestIntegrationTests.test_logout_invalidates_copied_authenticated_cookie | Passed | 0.063406 | BOOK-F-002, BOOK-SR-004 |
| books.test_security.SecurityRequestIntegrationTests.test_other_buyer_cannot_view_or_remove_saved_item | Passed | 0.049181 | BOOK-F-019, BOOK-SR-004 |
| books.test_security.SecurityRequestIntegrationTests.test_registered_passwords_are_verifiable_salted_hashes | Passed | 0.97607 | BOOK-F-001, BOOK-SR-002 |
| books.test_security.SecurityRequestIntegrationTests.test_search_reflection_escapes_html_attribute_payload | Passed | 0.026765 | BOOK-SR-005 |
| books.test_security.SecurityRequestIntegrationTests.test_seller_cannot_add_or_remove_buyer_wishlist_item | Passed | 0.046794 | BOOK-F-019, BOOK-SR-004 |
| books.test_security.SecurityRequestIntegrationTests.test_sql_like_login_identifier_does_not_bypass_authentication | Passed | 0.192451 | BOOK-SR-005 |
| books.test_security.SecurityRequestIntegrationTests.test_sql_like_search_is_literal_and_does_not_broaden_results | Passed | 0.034362 | BOOK-SR-005 |
| books.test_security.SecurityRequestIntegrationTests.test_stored_book_title_is_escaped_in_catalogue_and_detail | Passed | 0.037359 | BOOK-SR-005 |
| books.test_security.SecurityRequestIntegrationTests.test_valid_csrf_wishlist_add_is_idempotent | Passed | 0.049208 | BOOK-F-019, BOOK-SR-005 |
| books.test_security.SecurityRequestIntegrationTests.test_wishlist_post_without_csrf_creates_nothing | Passed | 0.037271 | BOOK-F-019, BOOK-SR-005 |
| books.tests.AdminInventoryManagementTests.test_admin_can_deactivate_listing | Passed | 0.084795 | BOOK-F-017 |
| books.tests.AdminInventoryManagementTests.test_admin_can_reactivate_approved_listing_with_stock | Passed | 0.088082 | BOOK-F-017 |
| books.tests.AdminInventoryManagementTests.test_admin_can_update_stock_quantity | Passed | 0.075278 | BOOK-F-017 |
| books.tests.AdminInventoryManagementTests.test_deactivated_listing_is_hidden_from_catalogue | Passed | 0.071486 | BOOK-F-017 |
| books.tests.AdminInventoryManagementTests.test_non_staff_user_cannot_manage_inventory | Passed | 0.206434 | BOOK-F-017, BOOK-SR-004 |
| books.tests.AdminInventoryManagementTests.test_out_of_stock_listing_cannot_be_activated | Passed | 0.073104 | BOOK-F-017 |
| books.tests.AdminInventoryManagementTests.test_pending_listing_cannot_be_activated | Passed | 0.066623 | BOOK-F-017 |
| books.tests.AdminListingApprovalTests.test_admin_can_approve_pending_listing | Passed | 0.069174 | BOOK-F-016 |
| books.tests.AdminListingApprovalTests.test_admin_can_open_book_listing_management | Passed | 0.054868 | BOOK-F-016 |
| books.tests.AdminListingApprovalTests.test_admin_can_reject_pending_listing | Passed | 0.067989 | BOOK-F-016 |
| books.tests.AdminListingApprovalTests.test_anonymous_user_cannot_access_admin_listing_management | Passed | 0.032774 | BOOK-F-016, BOOK-SR-004 |
| books.tests.AdminListingApprovalTests.test_approved_listing_appears_in_public_catalogue | Passed | 0.074854 | BOOK-F-016 |
| books.tests.AdminListingApprovalTests.test_approved_listing_without_stock_remains_unavailable | Passed | 0.065942 | BOOK-F-016 |
| books.tests.AdminListingApprovalTests.test_non_staff_user_cannot_access_admin_listing_management | Passed | 0.202022 | BOOK-F-016, BOOK-SR-004 |
| books.tests.AdminListingApprovalTests.test_rejected_listing_does_not_appear_in_public_catalogue | Passed | 0.07372 | BOOK-F-016 |
| books.tests.BookCatalogueTests.test_available_books_are_displayed | Passed | 0.027745 | BOOK-F-005 |
| books.tests.BookCatalogueTests.test_catalogue_page_loads | Passed | 0.025888 | BOOK-F-005 |
| books.tests.BookCatalogueTests.test_category_filter_excludes_unavailable_books | Passed | 0.027099 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_category_filter_is_case_insensitive | Passed | 0.026517 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_empty_catalogue_displays_message | Passed | 0.031238 | BOOK-F-005 |
| books.tests.BookCatalogueTests.test_filter_by_category | Passed | 0.026387 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_filter_by_category_and_price_together | Passed | 0.026909 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_filter_by_maximum_price | Passed | 0.027392 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_filter_by_minimum_price | Passed | 0.025897 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_filter_by_price_range | Passed | 0.025919 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_invalid_maximum_price_does_not_crash | Passed | 0.02565 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_invalid_minimum_price_does_not_crash | Passed | 0.026149 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_minimum_price_greater_than_maximum_is_rejected | Passed | 0.026391 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_negative_minimum_price_is_rejected | Passed | 0.026974 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_non_finite_price_is_rejected | Passed | 0.025976 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_price_boundaries_are_inclusive | Passed | 0.025718 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_results_are_ordered_by_title | Passed | 0.025687 | BOOK-F-005 |
| books.tests.BookCatalogueTests.test_search_and_filters_work_together | Passed | 0.026598 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_search_by_author | Passed | 0.028616 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_search_by_description_keyword | Passed | 0.025409 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_search_by_isbn | Passed | 0.026145 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_search_by_title | Passed | 0.026703 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_search_is_case_insensitive | Passed | 0.026551 | BOOK-F-006 |
| books.tests.BookCatalogueTests.test_unavailable_books_are_excluded | Passed | 0.027067 | BOOK-F-005 |
| books.tests.BookCatalogueTests.test_unmatched_search_displays_message | Passed | 0.025789 | BOOK-F-006 |
| books.tests.BookDetailTests.test_book_detail_displays_book_information | Passed | 0.028713 | BOOK-F-007 |
| books.tests.BookDetailTests.test_book_detail_displays_cover_image | Passed | 0.026372 | BOOK-F-007 |
| books.tests.BookDetailTests.test_book_detail_page_loads | Passed | 0.026199 | BOOK-F-007 |
| books.tests.BookDetailTests.test_book_detail_returns_404_for_nonexistent_book | Passed | 0.022186 | BOOK-F-007 |
| books.tests.BookDetailTests.test_book_detail_shows_placeholder_without_cover_image | Passed | 0.02788 | BOOK-F-007 |
| books.tests.BookDetailTests.test_catalogue_links_to_book_details | Passed | 0.026158 | BOOK-F-007 |
| books.tests.BookDetailTests.test_unavailable_book_detail_returns_404 | Passed | 0.021979 | BOOK-F-007 |
| books.tests.BookReviewTests.test_anonymous_user_is_redirected_to_login | Passed | 0.021622 | BOOK-F-018, BOOK-SR-004 |
| books.tests.BookReviewTests.test_blank_comment_is_rejected | Passed | 0.002545 | BOOK-F-018 |
| books.tests.BookReviewTests.test_buyer_cannot_submit_duplicate_review | Passed | 0.056153 | BOOK-F-018, BOOK-SR-004 |
| books.tests.BookReviewTests.test_buyer_without_purchase_cannot_submit_review | Passed | 0.051148 | BOOK-F-018 |
| books.tests.BookReviewTests.test_cancelled_order_does_not_qualify_for_review | Passed | 0.05074 | BOOK-F-018 |
| books.tests.BookReviewTests.test_comment_over_2000_characters_is_rejected | Passed | 0.002362 | BOOK-F-018 |
| books.tests.BookReviewTests.test_invalid_rating_is_rejected | Passed | 0.002053 | BOOK-F-018 |
| books.tests.BookReviewTests.test_purchasing_buyer_can_submit_review | Passed | 0.055702 | BOOK-F-018 |
| books.tests.BookReviewTests.test_review_comment_html_is_escaped_on_book_detail_page | Passed | 0.028226 | BOOK-F-018, BOOK-SR-005 |
| books.tests.BookReviewTests.test_review_does_not_allow_another_buyer_to_review | Passed | 0.052867 | BOOK-F-018, BOOK-SR-004 |
| books.tests.BookReviewTests.test_review_is_displayed_on_book_detail_page | Passed | 0.027962 | BOOK-F-018 |
| books.tests.SellerCreateListingTests.test_anonymous_user_is_redirected_to_login | Passed | 0.02117 | BOOK-F-014, BOOK-SR-004 |
| books.tests.SellerCreateListingTests.test_buyer_cannot_access_listing_form | Passed | 0.042516 | BOOK-F-014, BOOK-SR-004 |
| books.tests.SellerCreateListingTests.test_buyer_cannot_create_listing | Passed | 0.041824 | BOOK-F-014, BOOK-SR-004 |
| books.tests.SellerCreateListingTests.test_duplicate_isbn_is_rejected | Passed | 0.100416 | BOOK-F-014 |
| books.tests.SellerCreateListingTests.test_invalid_isbn_is_rejected | Passed | 0.042039 | BOOK-F-014 |
| books.tests.SellerCreateListingTests.test_javascript_cover_image_url_is_rejected | Passed | 0.001469 | BOOK-F-014, BOOK-SR-005 |
| books.tests.SellerCreateListingTests.test_seller_can_access_listing_form | Passed | 0.039743 | BOOK-F-014 |
| books.tests.SellerCreateListingTests.test_seller_can_create_pending_listing | Passed | 0.046077 | BOOK-F-014 |
| books.tests.SellerCreateListingTests.test_zero_price_is_rejected | Passed | 0.04572 | BOOK-F-014 |
| books.tests.SellerDeleteListingTests.test_anonymous_user_is_redirected_to_login | Passed | 0.51482 | BOOK-F-015, BOOK-SR-004 |
| books.tests.SellerDeleteListingTests.test_buyer_cannot_delete_listing | Passed | 0.699092 | BOOK-F-015, BOOK-SR-004 |
| books.tests.SellerDeleteListingTests.test_ordered_book_cannot_be_deleted | Passed | 0.710495 | BOOK-F-015 |
| books.tests.SellerDeleteListingTests.test_seller_can_delete_own_listing | Passed | 0.702303 | BOOK-F-015 |
| books.tests.SellerDeleteListingTests.test_seller_can_open_delete_confirmation | Passed | 0.696316 | BOOK-F-015 |
| books.tests.SellerDeleteListingTests.test_seller_cannot_delete_another_sellers_listing | Passed | 0.729043 | BOOK-F-015, BOOK-SR-004 |
| books.tests.SellerEditListingTests.test_anonymous_user_is_redirected_to_login | Passed | 0.510599 | BOOK-F-015, BOOK-F-016, BOOK-SR-004 |
| books.tests.SellerEditListingTests.test_buyer_cannot_edit_listing | Passed | 0.68973 | BOOK-F-015, BOOK-F-016, BOOK-SR-004 |
| books.tests.SellerEditListingTests.test_invalid_edit_does_not_change_listing | Passed | 0.695672 | BOOK-F-015, BOOK-F-016 |
| books.tests.SellerEditListingTests.test_seller_can_edit_own_listing | Passed | 0.706639 | BOOK-F-015, BOOK-F-016 |
| books.tests.SellerEditListingTests.test_seller_can_open_edit_page | Passed | 0.686951 | BOOK-F-015, BOOK-F-016 |
| books.tests.SellerEditListingTests.test_seller_cannot_edit_another_sellers_listing | Passed | 0.679494 | BOOK-F-015, BOOK-F-016, BOOK-SR-004 |
| books.tests.SellerMyListingsTests.test_anonymous_user_is_redirected_to_login | Passed | 0.349811 | BOOK-F-015, BOOK-SR-004 |
| books.tests.SellerMyListingsTests.test_buyer_cannot_view_seller_listings | Passed | 0.534694 | BOOK-F-015, BOOK-SR-004 |
| books.tests.SellerMyListingsTests.test_seller_can_view_own_listings | Passed | 0.528334 | BOOK-F-015 |
| books.tests.SellerMyListingsTests.test_seller_sees_approval_statuses | Passed | 0.531852 | BOOK-F-015 |
| books.tests.SellerMyListingsTests.test_seller_with_no_listings_sees_empty_state | Passed | 0.693023 | BOOK-F-015 |
| cart.tests.CartTests.test_adding_same_book_increases_quantity | Passed | 0.053751 | BOOK-F-008 |
| cart.tests.CartTests.test_buyer_can_add_book_to_cart | Passed | 0.051232 | BOOK-F-008 |
| cart.tests.CartTests.test_buyer_can_remove_item | Passed | 0.045368 | BOOK-F-008 |
| cart.tests.CartTests.test_buyer_can_update_quantity | Passed | 0.050401 | BOOK-F-008 |
| cart.tests.CartTests.test_buyer_can_view_empty_cart | Passed | 0.036663 | BOOK-F-008 |
| cart.tests.CartTests.test_cannot_add_more_than_available_stock | Passed | 0.052178 | BOOK-F-008 |
| cart.tests.CartTests.test_cannot_add_unavailable_book | Passed | 0.036346 | BOOK-F-008 |
| cart.tests.CartTests.test_cannot_increase_existing_quantity_beyond_stock | Passed | 0.038958 | BOOK-F-008 |
| cart.tests.CartTests.test_cannot_update_quantity_beyond_stock | Passed | 0.039932 | BOOK-F-008 |
| cart.tests.CartTests.test_cart_totals_are_calculated_correctly | Passed | 0.013066 | BOOK-F-008 |
| cart.tests.CartTests.test_extremely_long_quantity_is_rejected | Passed | 0.066352 | BOOK-F-008 |
| cart.tests.CartTests.test_invalid_quantity_is_rejected | Passed | 0.086123 | BOOK-F-008 |
| cart.tests.CartTests.test_seller_cannot_access_cart | Passed | 0.047747 | BOOK-F-008, BOOK-SR-004 |
| cart.tests.CartTests.test_seller_cannot_add_book_to_cart | Passed | 0.048444 | BOOK-F-008, BOOK-SR-004 |
| cart.tests.CheckoutTests.test_address_belonging_to_another_buyer_is_rejected | Passed | 0.067371 | BOOK-F-009, BOOK-SR-004 |
| cart.tests.CheckoutTests.test_buyer_can_view_checkout | Passed | 0.055075 | BOOK-F-009 |
| cart.tests.CheckoutTests.test_checkout_displays_saved_shipping_address | Passed | 0.054837 | BOOK-F-009 |
| cart.tests.CheckoutTests.test_checkout_requires_login | Passed | 0.035632 | BOOK-F-009 |
| cart.tests.CheckoutTests.test_empty_cart_cannot_proceed_to_checkout | Passed | 0.047068 | BOOK-F-009 |
| cart.tests.CheckoutTests.test_invalid_new_shipping_address_is_not_saved | Passed | 0.058298 | BOOK-F-009 |
| cart.tests.CheckoutTests.test_invalid_payment_method_is_rejected | Passed | 0.060195 | BOOK-F-009 |
| cart.tests.CheckoutTests.test_new_address_with_invalid_payment_method_is_not_saved | Passed | 0.060881 | BOOK-F-009 |
| cart.tests.CheckoutTests.test_new_shipping_address_can_be_saved | Passed | 0.058428 | BOOK-F-009 |
| cart.tests.CheckoutTests.test_seller_cannot_access_checkout | Passed | 0.051168 | BOOK-F-009, BOOK-SR-004 |
| cart.tests.CheckoutTests.test_valid_saved_address_and_payment_method_are_accepted | Passed | 0.050067 | BOOK-F-009 |
| config.tests_health.HealthCheckTests.test_health_check_rejects_post_requests | Passed | 0.02151 | BOOK-NF-003 |
| config.tests_health.HealthCheckTests.test_health_check_returns_200_when_database_is_available | Passed | 0.022471 | BOOK-NF-003 |
| config.tests_health.HealthCheckTests.test_health_check_returns_503_when_database_fails | Passed | 0.022711 | BOOK-NF-003 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_anonymous_user_cannot_cancel_order | Passed | 0.361562 | BOOK-F-013, BOOK-SR-004 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_anonymous_user_cannot_request_return | Passed | 0.360565 | BOOK-F-013, BOOK-SR-004 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_buyer_can_cancel_confirmed_order | Passed | 0.362265 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_buyer_can_cancel_pending_order | Passed | 0.36152 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_buyer_can_request_return_for_delivered_order | Passed | 0.363563 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_buyer_cannot_cancel_another_buyers_order | Passed | 0.360129 | BOOK-F-013, BOOK-SR-004 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_buyer_cannot_request_return_for_another_buyers_order | Passed | 0.363144 | BOOK-F-013, BOOK-SR-004 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_cancellation_endpoint_rejects_get | Passed | 0.357309 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_cancellation_is_rejected_after_policy_window | Passed | 0.361283 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_delivered_order_cannot_be_cancelled | Passed | 0.359316 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_duplicate_return_request_is_rejected | Passed | 0.369217 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_order_detail_shows_cancellation_option_for_eligible_order | Passed | 0.369367 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_order_detail_shows_return_request_status | Passed | 0.367485 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_return_endpoint_rejects_get | Passed | 0.358506 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_return_reason_html_is_escaped_on_order_detail_page | Passed | 0.366938 | BOOK-F-013, BOOK-SR-005 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_return_request_rejected_after_policy_window | Passed | 0.361637 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_return_request_rejected_for_undelivered_order | Passed | 0.358637 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_return_request_rejected_without_delivery_timestamp | Passed | 0.360964 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_return_request_rejects_reason_over_2000_characters | Passed | 0.368182 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_return_request_requires_a_reason | Passed | 0.360185 | BOOK-F-013 |
| orders.test_cancellation_return.OrderCancellationReturnTests.test_shipped_order_cannot_be_cancelled | Passed | 0.361373 | BOOK-F-013 |
| orders.test_notifications.OrderEmailNotificationTests.test_cancelled_status_does_not_send_email | Passed | 0.16877 | BOOK-F-020 |
| orders.test_notifications.OrderEmailNotificationTests.test_confirmed_status_sends_email | Passed | 0.168591 | BOOK-F-020 |
| orders.test_notifications.OrderEmailNotificationTests.test_creating_pending_order_does_not_send_email | Passed | 0.163613 | BOOK-F-020 |
| orders.test_notifications.OrderEmailNotificationTests.test_delivered_status_sends_email | Passed | 0.169312 | BOOK-F-020 |
| orders.test_notifications.OrderEmailNotificationTests.test_email_contains_order_and_item_details | Passed | 0.169175 | BOOK-F-020 |
| orders.test_notifications.OrderEmailNotificationTests.test_email_failure_does_not_prevent_status_update | Passed | 0.170194 | BOOK-F-020 |
| orders.test_notifications.OrderEmailNotificationTests.test_saving_without_status_change_does_not_send_email | Passed | 0.165058 | BOOK-F-020 |
| orders.test_notifications.OrderEmailNotificationTests.test_shipped_status_sends_email | Passed | 0.168752 | BOOK-F-020 |
| orders.test_notifications.OrderEmailNotificationTests.test_transition_from_confirmed_to_shipped_sends_new_email | Passed | 0.172698 | BOOK-F-020 |
| orders.test_tracking.ShipmentTrackingTests.test_cancelled_order_shows_cancellation_message | Passed | 0.205501 | BOOK-F-012 |
| orders.test_tracking.ShipmentTrackingTests.test_confirmed_order_shows_confirmed_status | Passed | 0.203259 | BOOK-F-012 |
| orders.test_tracking.ShipmentTrackingTests.test_delivered_order_shows_delivered_status | Passed | 0.207583 | BOOK-F-012 |
| orders.test_tracking.ShipmentTrackingTests.test_pending_order_shows_order_received_as_current | Passed | 0.235444 | BOOK-F-012 |
| orders.test_tracking.ShipmentTrackingTests.test_processing_order_shows_processing_status | Passed | 0.204672 | BOOK-F-012 |
| orders.test_tracking.ShipmentTrackingTests.test_shipped_order_shows_shipped_status | Passed | 0.203742 | BOOK-F-012 |
| orders.test_tracking.ShipmentTrackingTests.test_tracking_page_explains_live_courier_tracking_is_unavailable | Passed | 0.202032 | BOOK-F-012 |
| orders.tests.CreateOrderFromCartTests.test_creates_order_items_and_pending_payment | Passed | 0.1825 | BOOK-F-010 |
| orders.tests.CreateOrderFromCartTests.test_failed_initiation_marks_payment_failed | Passed | 0.174392 | BOOK-F-010 |
| orders.tests.CreateOrderFromCartTests.test_order_creation_does_not_clear_cart | Passed | 0.1729 | BOOK-F-010 |
| orders.tests.CreateOrderFromCartTests.test_order_creation_does_not_reduce_inventory | Passed | 0.17365 | BOOK-F-010 |
| orders.tests.CreateOrderFromCartTests.test_order_preserves_shipping_address_snapshot | Passed | 0.173087 | BOOK-F-009 |
| orders.tests.CreateOrderFromCartTests.test_rejects_deleted_book | Passed | 0.172809 | BOOK-F-010 |
| orders.tests.CreateOrderFromCartTests.test_rejects_insufficient_stock | Passed | 0.171566 | BOOK-F-010 |
| orders.tests.CreateOrderFromCartTests.test_rejects_invalid_payment_method | Passed | 0.167882 | BOOK-F-009 |
| orders.tests.CreateOrderFromCartTests.test_rejects_unavailable_book | Passed | 0.171581 | BOOK-F-010 |
| orders.tests.CreateOrderFromCartTests.test_successful_initiation_keeps_payment_pending | Passed | 0.17444 | BOOK-F-010 |
| orders.tests.OrderHistoryAndDetailTests.test_buyer_can_view_order_history | Passed | 0.372679 | BOOK-F-011 |
| orders.tests.OrderHistoryAndDetailTests.test_buyer_can_view_own_order_details | Passed | 0.368913 | BOOK-F-011 |
| orders.tests.OrderHistoryAndDetailTests.test_buyer_cannot_view_another_buyers_order | Passed | 0.360969 | BOOK-F-011, BOOK-SR-004 |
| orders.tests.OrderHistoryAndDetailTests.test_order_details_require_login | Passed | 0.353917 | BOOK-F-011 |
| orders.tests.OrderHistoryAndDetailTests.test_order_history_does_not_show_other_buyers_orders | Passed | 0.367389 | BOOK-F-011 |
| orders.tests.OrderHistoryAndDetailTests.test_order_history_requires_login | Passed | 0.347026 | BOOK-F-011 |

## System test outcomes

No outcomes recorded in this category.

## Unclassified test outcomes

No outcomes recorded in this category.

Failure details: ../test-results.json and ../tests.log. Open defects and retests require review.
