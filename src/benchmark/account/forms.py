from django import forms
from django.contrib.auth import authenticate
from django.utils.crypto import get_random_string

from crispy_forms.helper import FormHelper

from benchmark.account.models import Account, Agency
from benchmark.utils.various import User

import re

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.EmailInput, label='Username')
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    next_ = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_errors = True
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if not user or not user.is_active or not getattr(user, 'account', None):
            raise forms.ValidationError(
                "Authentication failed. Please try again."
            )

        return self.cleaned_data


class AccountUserCreationForm(forms.ModelForm):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=Account.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ('email', )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with this email already exists."
            )
        return email

    def save(self, commit=True):
        user = super(AccountUserCreationForm, self).save(commit=False)

        # Just in case, let's not allow empty password
        user.set_password(get_random_string(length=8))
        user.username = self.cleaned_data['email']
        user.is_active = False

        user.save()

        # Create account and send activation email
        account = Account.objects.create(
            user=user,
            role=self.cleaned_data['role']
        )

        account.send_activation_email(self.request)

        return user


class AccountActivationForm(forms.Form):
    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
        'validate': "Password must include at least one digit, both Upper case and Lower case, special character(@, #, $ ...) and 10 characters",
    }

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="Enter the same password as before, for verification."
    )

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        password_letters = set(password1)

        if any([not re.match('.*\d+.*', password1), re.match('^[a-zA-Z0-9_-]+$', password1), len(password1) < 10]):
            raise forms.ValidationError(
                self.error_messages['validate'],
                code='validate',
            )

        mixed = any(letter.islower() for letter in password_letters) and any(letter.isupper() for letter in password_letters)
        if not mixed:
            raise forms.ValidationError(
                self.error_messages['validate'],
                code='validate',
            )

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        return password2


class ChangePasswordForm(AccountActivationForm):
    pass


class PasswordForgotRequestForm(forms.Form):
    email = forms.CharField(
        label="Confirm Email",
        widget=forms.EmailInput
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = User.objects.filter(email=email)
        if not user.exists():
            raise forms.ValidationError(
                "A user with this email does not exists."
            )
        else:
            is_active = User.objects.get(email=email).is_active
            if not is_active:
                raise forms.ValidationError(
                    "A user with this email does not exists."
                )
        user = User.objects.get(email=email)
        account = Account.objects.get(user=user)
        account.send_confirmation_email(user)
        return email


class AgencyForm(forms.ModelForm):
    class Meta:
        model = Agency
        fields = (
            'name',
            'code',
            'description'
        )