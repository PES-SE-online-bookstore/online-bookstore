from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


admin.site.unregister(User)


@admin.register(User)
class ManagedUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("is_active",)
    list_filter = UserAdmin.list_filter + ("is_active",)

    actions = [
        "deactivate_accounts",
        "activate_accounts",
    ]

    @admin.action(description="Deactivate selected accounts")
    def deactivate_accounts(self, request, queryset):
        # Prevent administrators from deactivating their own account.
        accounts_to_deactivate = queryset.exclude(
            pk=request.user.pk
        )

        deactivated_count = accounts_to_deactivate.update(
            is_active=False
        )

        skipped_count = queryset.filter(
            pk=request.user.pk
        ).count()

        message = (
            f"{deactivated_count} account(s) deactivated."
        )

        if skipped_count:
            message += " Your own account was not deactivated."

        self.message_user(
            request,
            message,
            level=messages.SUCCESS,
        )

    @admin.action(description="Reactivate selected accounts")
    def activate_accounts(self, request, queryset):
        activated_count = queryset.filter(
            is_active=False
        ).update(is_active=True)

        self.message_user(
            request,
            f"{activated_count} account(s) reactivated.",
            level=messages.SUCCESS,
        )