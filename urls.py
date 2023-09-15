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
from .api.phone_login_apis import GenerateTokenApi, ConfirmTokenApi, PasswordLoginApi

app_name = 'phone_login'

drf_urlpatterns = [
    path('api/login/', GenerateTokenApi.as_view(), name='login_api'),
    path('api/confirm-otp/', ConfirmTokenApi.as_view(), name='confirm_otp_api'),
    path('api/password-login/', PasswordLoginApi.as_view(), name='password_login_api'),
]

urlpatterns = [
    path("login/", GenerateToken.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("confirm-otp/", ConfirmToken.as_view(), name="confirm_otp"),
    path("password-login/", PasswordLogin.as_view(), name="password_login"),
    path("forget-password/", ForgetPassword.as_view(), name="forget_password"),
    path("confirm-password_otp/", ConfirmPasswordToken.as_view(), name="confirm_password_otp"),
    path("change-password/<uidb64>/<token>/", ChangePassword.as_view(), name="change_password"),
    *drf_urlpatterns
]
