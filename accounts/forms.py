from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from .models import Profile


class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
    )

    email = forms.EmailField(
        required=True,
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
    )

    role = forms.ChoiceField(
        choices=Profile.Role.choices,
        required=True,
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error(
                "confirm_password",
                "The passwords do not match.",
            )

        if password:
            try:
                validate_password(password)
            except forms.ValidationError as error:
                self.add_error("password", error)

        return cleaned_data

    @transaction.atomic
    def save(self):
        if not self.is_valid():
            raise ValueError(
                "Cannot save an invalid registration form."
            )

        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
        )

        Profile.objects.create(
            user=user,
            role=self.cleaned_data["role"],
        )

        return user