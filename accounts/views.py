from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import RegistrationForm
from .models import LoginAttempt


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Your account has been created successfully. You can now log in.",
            )

            return redirect("login")

    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})
    

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # Find the user without revealing whether the account exists.
        user_record = User.objects.filter(
            username__iexact=username
        ).first()

        # Check whether this account is currently locked.
        if user_record is not None:
            attempt = LoginAttempt.objects.filter(
                user=user_record
            ).first()

            if attempt and attempt.locked_until:
                if timezone.now() < attempt.locked_until:
                    messages.error(
                        request,
                        "Invalid username or password, or the account "
                        "is temporarily unavailable. Please try again later.",
                    )
                    return render(request, "accounts/login.html")

                # The lockout has expired.
                attempt.failed_attempts = 0
                attempt.locked_until = None
                attempt.save(
                    update_fields=[
                        "failed_attempts",
                        "locked_until",
                        "updated_at",
                    ]
                )

        # Check the supplied credentials.
        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            # A successful login resets the failed-attempt counter.
            LoginAttempt.objects.filter(user=user).delete()

            login(request, user)
            messages.success(
                request,
                "You have logged in successfully.",
            )
            return redirect("books:book_catalogue")

        # Record failed attempts for an existing account.
        if user_record is not None:
            with transaction.atomic():
                # Create the record if this is the first failed attempt.
                LoginAttempt.objects.get_or_create(user=user_record)

                # Lock the row while reading and updating the counter.
                attempt = LoginAttempt.objects.select_for_update().get(
                    user=user_record
                )       

                # Increase the failed-attempt count.
                attempt.failed_attempts += 1

                # Lock the account after five failed attempts.
                if attempt.failed_attempts >= 5:
                    attempt.locked_until = (
                        timezone.now() + timedelta(minutes=15)
                    )

            attempt.save(
                update_fields=[
                    "failed_attempts",
                    "locked_until",
                    "updated_at",
                ]
            )

        messages.error(
            request,
            "Invalid username or password.",
        )

    return render(request, "accounts/login.html")


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have logged out successfully.")
        return redirect("login")

    return redirect("login")