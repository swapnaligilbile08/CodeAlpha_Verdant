from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import NewsletterSignup, Profile, Review


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["autocomplete"] = "off"
        self.fields["password"].widget.attrs["autocomplete"] = "off"


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = ["first_name", "username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs.update({
            "placeholder": "Your first name", "autocomplete": "given-name",
        })
        self.fields["username"].widget.attrs.update({
            "placeholder": "Pick a username", "autocomplete": "username",
        })
        self.fields["email"].widget.attrs.update({
            "placeholder": "you@example.com", "autocomplete": "email",
        })
        self.fields["password1"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password2"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password1"].help_text = "At least 8 characters, and not something too easy to guess."

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = Profile
        fields = [
            "phone", "address_line1", "address_line2", "city", "state",
            "postal_code", "country",
        ]

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.user.first_name = self.cleaned_data.get("first_name", profile.user.first_name)
            profile.user.last_name = self.cleaned_data.get("last_name", profile.user.last_name)
            profile.user.save()
            profile.save()
        return profile


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return qty


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=200)
    phone = forms.CharField(max_length=30)
    address_line1 = forms.CharField(max_length=255, label="Address line 1")
    address_line2 = forms.CharField(max_length=255, required=False, label="Address line 2")
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)
    country = forms.CharField(max_length=100, initial="India")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} star{'s' if i != 1 else ''}") for i in range(1, 6)]),
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "Share your experience with this plant..."}),
        }


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSignup
        fields = ["email"]
        widgets = {"email": forms.EmailInput(attrs={"placeholder": "you@example.com"})}
