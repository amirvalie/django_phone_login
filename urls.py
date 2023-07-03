from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    GenerateToken,
    ConfirmToken,
    PasswordLogin,
    ForgetPassword,
    ConfirmPasswordToken,
    ChangePassword,
)
from .api.phone_login_apis import GenerateTokenApi, ConfirmTokenApi

app_name = 'phone_login'

drf_urlpatterns = [
    path('api/login/', GenerateTokenApi.as_view(), name='login-api'),
    path('api/confirm_otp/', ConfirmTokenApi.as_view(), name='confirm-otp-api'),
]

urlpatterns = [
    path("login/", GenerateToken.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("confirm_otp/", ConfirmToken.as_view(), name="confirm_otp"),
    path("password_login/", PasswordLogin.as_view(), name="password_login"),
    path("forget_password/", ForgetPassword.as_view(), name="forget_password"),
    path("confirm_password_otp/", ConfirmPasswordToken.as_view(), name="confirm_password_otp"),
    path("change_password/<uidb64>/<token>/", ChangePassword.as_view(), name="change_password"),
    *drf_urlpatterns
]
