from django.shortcuts import redirect, render
from .models import PhoneToken
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from .limit_request import GenerateLimitation, check_limitation
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect

User = get_user_model()
from .decorators import (
    password_require,
    phone_number_require,
    anonymous_required,
)
from .forms import (
    PhoneTokenForm,
    PhoneTokenConfirmForm,
    PasswordLoginForm,
    SetPasswordForm,
    ForgetPasswordForm,
)


def invalid_attempts_massage_view(request):
    """ 
    This function is executed when the number of user attempts to login 
    or enter the code exceeds the allowed limit
    """
    return render(request, 'registration/invalid_attempts.html')


class GenerateToken(FormView):
    """
    Create or get PhoneToken object and send a SMS OTP
    """
    form_class = PhoneTokenForm
    template_name = 'registration/generate_token.html'
    success_url = reverse_lazy('phone_login:confirm_otp')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request=request, data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        GenerateLimitation(self.request)
        self.request.session['phone_number'] = form.phone_token.phone_number
        PhoneToken.send_otp(form.phone_token)
        return super().form_valid(form)

    @method_decorator(anonymous_required)
    @method_decorator(check_limitation)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ConfirmToken(FormView):
    form_class = PhoneTokenConfirmForm
    template_name = 'registration/confirm_phone.html'
    success_url = '/'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request=request, data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        login(self.request, form.user_cache, backend='django.contrib.auth.backends.ModelBackend')
        del self.request.session['phone_number']
        return super().form_valid(form)

    @method_decorator(phone_number_require('login', 'phone_number'))
    @method_decorator(check_limitation)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PasswordLogin(FormView):
    form_class = PasswordLoginForm
    template_name = 'registration/password_login.html'
    success_url = '/'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request=request, data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        login(
            self.request, form.user_cache,
            backend='django.contrib.auth.backends.ModelBackend'
        )
        del self.request.session['phone_number']
        return super().form_valid(form)

    @method_decorator(phone_number_require('login', 'phone_number'))
    @method_decorator(check_limitation)
    @method_decorator(password_require)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ForgetPassword(FormView):
    form_class = ForgetPasswordForm
    template_name = 'registration/forget_password.html'
    success_url = reverse_lazy('phone_login:confirm_password_otp')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request=request, data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        GenerateLimitation(self.request)
        generate_token = PhoneToken.send_otp(form.phone_token)
        self.request.session['phone_number_for_password'] = form.phone_token.phone_number
        return super().form_valid(form)

    @method_decorator(check_limitation)
    @method_decorator(anonymous_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ConfirmPasswordToken(FormView):
    form_class = PhoneTokenConfirmForm
    template_name = 'registration/confirm_phone.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request=request, data=request.POST)
        if form.is_valid():
            print('form is valid')
            return self.form_valid(form)
        else:
            print('form is not valid')
            return self.form_invalid(form)

    def form_valid(self, form):
        phone_number = self.request.session.get('phone_number_for_password')
        user = get_object_or_404(User, phone=phone_number)
        uid = urlsafe_base64_encode(force_bytes(user))
        token = default_token_generator.make_token(user)
        del self.request.session['phone_number_for_password']
        return redirect(reverse('phone_login:change_password', kwargs={'uidb64': uid, 'token': token}))

    @method_decorator(phone_number_require('forget_password', 'phone_number_for_password'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ChangePassword(FormView):
    form_class = SetPasswordForm
    template_name = 'registration/change_password.html'
    success_url = '/'

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(phone=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user

    def get(self, request, *args, **kwargs):
        user = self.get_user(kwargs['uidb64'])
        if user is not None and default_token_generator.check_token(user, self.kwargs.get('token')):
            return super().get(request, *args, **kwargs)
        return HttpResponse('Invalid Link')

    def post(self, request, *args, **kwargs):
        user = self.get_user(kwargs['uidb64'])
        form = self.form_class(user=user, data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        user = form.save()
        auth = authenticate(username=user.phone, password=form.cleaned_data['new_password2'])
        if auth:
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super().form_valid(form)
