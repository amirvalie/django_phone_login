from django import forms
from .models import PhoneToken
from django.contrib.auth import get_user_model

User = get_user_model()
from django.core.exceptions import ValidationError
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.utils.translation import gettext, gettext_lazy as _
import re
from django_phone_login.models import PhoneToken
from django.conf import settings
from .limit_request import GenerateLimitation


def regex_phone_number(value):
    phone_number = value
    regex = '09(\d{9})$'
    if re.match(regex, phone_number):
        return True
    return False


class PhoneTokenForm(forms.Form):
    phone_number = forms.CharField()
    error_massages = {
        'invalid_phone': _('Phone number is not valid'),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.phone_token = None
        super().__init__(*args, **kwargs)

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if regex_phone_number(phone_number):
            self.phone_token = PhoneToken.objects.get_or_create(
                phone_number=phone_number,
            )[0]
            return phone_number
        else:
            raise ValidationError(
                self.error_massages['invalid_phone'],
            )


class PhoneTokenConfirmForm(forms.Form):
    otp = forms.IntegerField()
    error_massages = {
        'invalid_otp': _('OTP code is not valid'),
        'inactive': _('Your account is inactive'),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean_otp(self):
        print('form request:', self.request)
        GenerateLimitation(self.request)
        otp = self.cleaned_data['otp']
        self.user_cache = authenticate(
            self.request,
            otp=otp,
            phone_number=self.request.session['phone_number'],
        )
        if self.user_cache is None:
            raise ValidationError(
                self.error_massages['invalid_otp'],
            )
        else:
            self.inactive_user(self.user_cache)
        return str(otp)

    def inactive_user(self, user):
        if user.is_active == False:
            raise ValidationError(
                self.error_massages['inactive'],
            )


class PasswordLoginForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    error_massages = {
        "invalid_login": "Please enter a correct username and password. Note that both "
                         "fields may be case-sensitive.",
        'inactive': _('Your account is inactive'),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        self.user_cache = authenticate(
            username=self.request.session['phone_number'],
            password=password,
        )
        if self.user_cache is None:
            raise ValidationError(
                self.error_massages['invalid_login'],
            )
        elif self.user_cache.is_active == False:
            raise ValidationError(
                self.error_massages['inactive'],
            )
        return password


class ForgetPasswordForm(forms.Form):
    phone_number = forms.CharField()
    error_massages = {
        'phone_token_does_not_exist': _('There is not account with this phone number'),
        'invalid_phone': _('Phone number is not valid'),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.phone_token = None
        super().__init__(*args, **kwargs)

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if regex_phone_number(phone_number):
            try:
                self.phone_token = PhoneToken.objects.get(
                    phone_number=phone_number,
                )
            except:
                raise ValidationError(
                    self.error_massages['phone_token_does_not_exist'],
                )
        else:
            raise ValidationError(
                self.error_massages['invalid_phone'],
            )


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
