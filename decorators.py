from django.shortcuts import redirect
import functools
from django.contrib.auth import get_user_model 
from django.conf import settings
User=get_user_model()
    
def password_require(func):
    """
    If a user wants to log in with a password, she/He must already have a password.
    """
    functools.wraps(func)
    def wrapper(request):
            phone_number=request.session.get('phone_number')
            try:
                user=User.objects.get(phone=phone_number)
            except User.DoesNotExist:
                return redirect('phone_login:login')
            else:
                if user.password:
                    return func(request)    
                else:
                    return redirect('phone_login:login')
    return wrapper


def phone_number_require(redirect_to,session_name):
    """
    This decorator checks if there is a phone number in the session or not.
    Note 
    Note that the phone numbers entered by the user are saved in the sessions.
    """
    def method_wrapper(func):
        def arguments_wrapper(request, *args, **kwargs) :
            phone_number=request.session.get(session_name)
            if phone_number:
                return func(request)    
            return redirect('phone_login:%s'%redirect_to)
        return arguments_wrapper
    return method_wrapper


def anonymous_required(func):
    """
    If the users want to login they should be anonymous user.
    """
    def as_view(request, *args, **kwargs):
        redirect_to = kwargs.get('next', settings.LOGIN_REDIRECT_URL )
        if request.user.is_authenticated:
            return redirect(redirect_to)
        response = func(request, *args, **kwargs)
        return response
    return as_view