from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    generate_token,
    confirm_token,
    password_login,
    change_password,
    forget_password,
    confirm_password_token,
)
app_name='phone_login'
urlpatterns=[
    path("login/",generate_token,name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("confirm_otp/",confirm_token,name="confirm_otp"),
    path("password_login/",password_login,name="password_login"),
    path("forget_password/",forget_password,name="forget_password"),
    path("confirm_password_otp/",confirm_password_token,name="confirm_password_otp"),
    path("change_password/<uidb64>/<token>/",change_password,name="change_password"),
]   
