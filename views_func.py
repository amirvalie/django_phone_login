from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic.edit import CreateView,UpdateView
from .models import PhoneToken
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from .limit_request import GenerateLimitation,check_limitation
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
User=get_user_model()

def invalid_attempts_func(request):
    """ 
    This function is executed when the number of user attempts to login 
    or enter the code exceeds the allowed limit
    """
    return render(request,'registration/invalid_attempts_func.html')
    
@anonymous_required
@check_limitation
def generate_token(request):
    """
    Create or get PhoneToken object and send a SMS OTP
    """
    if request.method=='POST':
        form=PhoneTokenForm(data=request.POST,request=request)
        if form.is_valid():
            PhoneToken.send_otp(form.phone_token)
            GenerateLimitation(request)
            request.session['phone_number']=form.phone_token.phone_number
            return redirect('phone_login:confirm_otp')
    else:
        form=PhoneTokenForm
    return render(request,'registration/generate_token.html',{'form':form})

@phone_number_require('login','phone_number')
@check_limitation
def confirm_token(request):
    if request.method=='POST':
        form=PhoneTokenConfirmForm(request=request,data=request.POST)
        if form.is_valid():
            login(request,form.user_cache,backend='django.contrib.auth.backends.ModelBackend')
            del request.session['phone_number']
            return redirect('/')
    else:
        form=PhoneTokenConfirmForm()
    return render(request,'registration/confirm_phone.html',{'form':form})
    
@phone_number_require('login','phone_number')
@password_require
@check_limitation
def password_login(request):
    if request.method=="POST":
        form=PasswordLoginForm(data=request.POST,request=request)
        if form.is_valid():
            login(
                    request,form.user_cache,
                    backend='django.contrib.auth.backends.ModelBackend'
                )
            del request.session['phone_number']
            return redirect('/')
    else:
        form=PasswordLoginForm()
    return render(request,'registration/password_login.html',{'form':form})
    
@anonymous_required
@check_limitation
@password_require
def forget_password(request):
    if request.method=='POST':
        form=ForgetPasswordForm(data=request.POST,request=request)
        if form.is_valid():
            generate_token=PhoneToken.send_otp(form.phone_token)
            GenerateLimitation(request)
            request.session['phone_number_for_password']=form.phone_token.phone_number
            return redirect('phone_login:confirm_password_otp')
    else:
        form=ForgetPasswordForm()
    return render(request,'registration/forget_password.html',{'form':form})


@phone_number_require('forget_password','phone_number_for_password')    
def confirm_password_token(request):
    if request.method=='POST':
        form=PhoneTokenConfirmForm(data=request.POST,request=request)
        if form.is_valid():
            phone_number=request.session.get('phone_number_for_password')
            user=get_object_or_404(User,phone=phone_number)
            uid=urlsafe_base64_encode(force_bytes(user))
            token=default_token_generator.make_token(user)
            del request.session['phone_number']
            return redirect(reverse('phone_login:change_password',kwargs={'uidb64':uid,'token':token}))
    else:
        form=PhoneTokenConfirmForm()
    return render(request,'registration/confirm_phone.html',{'form':form})

def change_password(request,uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(phone=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form=SetPasswordForm(request.POST,user=user)
            if form.is_valid():
                user=form.save()
                auth=authenticate(username=user.phone,password=form.cleaned_data['new_password2'])
                if auth:
                    login(request,user,backend='django.contrib.auth.backends.ModelBackend')
                return redirect('/')
        else:
            form=SetPasswordForm()
        return render(request,'registration/change_password.html',{'form':form})
    else:
        return HttpResponse('Link is not valid!')
