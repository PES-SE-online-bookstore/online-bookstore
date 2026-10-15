from django import forms

from .models import Book


class BookListingForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "isbn",
            "description",
            "category",
            "price",
            "stock_quantity",
            "cover_image_url",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Enter book title"}
            ),
            "author": forms.TextInput(
                attrs={"placeholder": "Enter author name"}
            ),
            "isbn": forms.TextInput(
                attrs={
                    "placeholder": "Enter ISBN",
                    "maxlength": "13",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Describe the book",
                    "rows": 5,
                }
            ),
            "category": forms.TextInput(
                attrs={"placeholder": "Enter category"}
            ),
            "price": forms.NumberInput(
                attrs={"min": "0.01", "step": "0.01"}
            ),
            "stock_quantity": forms.NumberInput(
                attrs={"min": "0", "step": "1"}
            ),
            "cover_image_url": forms.URLInput(
                attrs={"placeholder": "https://example.com/book.jpg"}
            ),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise forms.ValidationError("Book title is required.")
        return title

    def clean_author(self):
        author = self.cleaned_data["author"].strip()
        if not author:
            raise forms.ValidationError("Author name is required.")
        return author

    def clean_isbn(self):
        isbn = self.cleaned_data["isbn"].strip()

        if len(isbn) not in (10, 13) or not isbn.isdigit():
            raise forms.ValidationError(
                "Enter a valid ISBN containing 10 or 13 digits."
            )

        return isbn

    def clean_price(self):
        price = self.cleaned_data["price"]

        if price <= 0:
            raise forms.ValidationError(
                "Price must be greater than zero."
            )

        return price