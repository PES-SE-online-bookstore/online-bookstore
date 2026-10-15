from django import forms

from .models import ShippingAddress


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = [
            "full_name",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "postal_code",
            "country",
            "phone_number",
            "is_default",
        ]

        labels = {
            "full_name": "Full Name",
            "address_line_1": "Address Line 1",
            "address_line_2": "Address Line 2 (Optional)",
            "city": "City",
            "state": "State / Province",
            "postal_code": "Postal / ZIP Code",
            "country": "Country",
            "phone_number": "Phone Number",
            "is_default": "Save as my default shipping address",
        }

        widgets = {
            "full_name": forms.TextInput(
                attrs={"autocomplete": "name"}
            ),
            "address_line_1": forms.TextInput(
                attrs={"autocomplete": "address-line1"}
            ),
            "address_line_2": forms.TextInput(
                attrs={"autocomplete": "address-line2"}
            ),
            "city": forms.TextInput(
                attrs={"autocomplete": "address-level2"}
            ),
            "state": forms.TextInput(
                attrs={"autocomplete": "address-level1"}
            ),
            "postal_code": forms.TextInput(
                attrs={"autocomplete": "postal-code"}
            ),
            "country": forms.TextInput(
                attrs={"autocomplete": "country-name"}
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "autocomplete": "tel",
                    "type": "tel",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

        for field_name in [
            "address_line_1",
            "city",
            "state",
            "postal_code",
            "country",
            "phone_number",
        ]:
            self.fields[field_name].widget.attrs["required"] = True

    def clean_full_name(self):
        value = self.cleaned_data["full_name"].strip()

        if not value:
            raise forms.ValidationError(
                "Please enter the recipient's full name."
            )

        return value

    def clean_postal_code(self):
        value = self.cleaned_data["postal_code"].strip()

        if not value:
            raise forms.ValidationError(
                "Please enter a postal or ZIP code."
            )

        return value

    def clean_phone_number(self):
        value = self.cleaned_data["phone_number"].strip()

        if not value:
            raise forms.ValidationError(
                "Please enter a phone number."
            )

        return value


class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = [
        ("TEST_CARD", "Credit / Debit Card (Sandbox)"),
        ("TEST_UPI", "UPI (Test Mode)"),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        label="Payment Method",
        widget=forms.RadioSelect,
    )