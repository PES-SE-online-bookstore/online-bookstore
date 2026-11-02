"""Reviewed scope of legacy tests. Mapping means partial evidence, not acceptance."""

# All existing classes exercise database-backed models/services or Django's
# request/response stack. None establish a deployed browser/system result.
LEGACY_CLASSES = {
    "accounts.tests.AdminAccountManagementTests": ("BOOK-F-017",),
    "books.tests.BookCatalogueTests": ("BOOK-F-005", "BOOK-F-006"),
    "books.tests.BookDetailTests": ("BOOK-F-007",),
    "books.tests.SellerCreateListingTests": ("BOOK-F-014",),
    "books.tests.SellerMyListingsTests": ("BOOK-F-015",),
    "books.tests.SellerEditListingTests": ("BOOK-F-015", "BOOK-F-016"),
    "books.tests.SellerDeleteListingTests": ("BOOK-F-015",),
    "books.tests.AdminListingApprovalTests": ("BOOK-F-016",),
    "books.tests.AdminInventoryManagementTests": ("BOOK-F-017",),
    "books.tests.BookReviewTests": ("BOOK-F-018",),
    "books.test_rbac.ReviewRolePermissionTests": ("BOOK-F-018", "BOOK-SR-004"),
    "cart.tests.CartTests": ("BOOK-F-008",),
    "cart.tests.CheckoutTests": ("BOOK-F-009",),
    "orders.tests.CreateOrderFromCartTests": (),
    "orders.tests.OrderHistoryAndDetailTests": ("BOOK-F-011",),
    "orders.test_tracking.ShipmentTrackingTests": ("BOOK-F-012",),
    "orders.test_cancellation_return.OrderCancellationReturnTests": ("BOOK-F-013",),
    "orders.test_notifications.OrderEmailNotificationTests": ("BOOK-F-020",),
    "config.tests_health.HealthCheckTests": (),
}


def describe_test(test):
    method = getattr(test, getattr(test, "_testMethodName", ""), None)
    class_id = f"{type(test).__module__}.{type(test).__qualname__}"
    legacy = class_id in LEGACY_CLASSES
    level = getattr(method, "qa_level", getattr(test, "qa_level", "Integration" if legacy else "Unclassified"))
    explicit = getattr(method, "qa_requirements", getattr(test, "qa_requirements", None))
    requirements = list(explicit if explicit is not None else LEGACY_CLASSES.get(class_id, ()))
    basis = "Explicit test metadata" if explicit is not None else "Reviewed class scope; partial evidence only"
    if legacy and explicit is None:
        name = getattr(test, "_testMethodName", "")
        if class_id.endswith(".BookCatalogueTests"):
            requirements = ["BOOK-F-006" if any(word in name for word in ("search", "filter", "price")) else "BOOK-F-005"]
        elif class_id.endswith(".CreateOrderFromCartTests"):
            requirements = ["BOOK-F-009" if "address" in name or "method" in name else "BOOK-F-010"]
            basis = "Mock/order-creation characterization only; does not verify gateway payment acceptance"
        elif class_id.endswith(".HealthCheckTests"):
            requirements = ["BOOK-NF-003"]
            basis = "Health endpoint support only; does not establish monthly availability"
        if any(word in name for word in ("cannot_access", "cannot_edit", "cannot_delete", "another_buyer", "another_seller", "only", "non_staff", "anonymous", "without_profile", "seller_cannot", "buyer_cannot")):
            requirements.append("BOOK-SR-004")
        if "escaped" in name or "javascript" in name:
            requirements.append("BOOK-SR-005")
    return level, sorted(set(requirements)), basis


def requirement(*ids):
    def decorate(method):
        method.qa_requirements = ids
        return method
    return decorate
