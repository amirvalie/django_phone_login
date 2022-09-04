from django.shortcuts import redirect
import functools
from django.contrib.auth import get_user_model 
from django.conf import settings
User=get_user_model()
    
def password_login_decorator(func):
    functools.wraps(func)
    def wrapper(request):
            phone_number=request.session.get('phone_number')
            try:
                user=User.objects.get(phone=phone_number)
            except User.DoesNotExist:
                return redirect('phone_login:login')
            finally:
                if user.password:
                    return func(request)    
                else:
                    return redirect('phone_login:login')
    return wrapper


def phone_number_require(redirect_to,session_name):
    def method_wrapper(func):
        def arguments_wrapper(request, *args, **kwargs) :
            phone_number=request.session.get(session_name)
            if phone_number:
                return func(request)    
            return redirect('phone_login:%s'%redirect_to)
        return arguments_wrapper
    return method_wrapper


def anonymous_required(func):
    def as_view(request, *args, **kwargs):
        redirect_to = kwargs.get('next', settings.LOGIN_REDIRECT_URL )
        if request.user.is_authenticated:
            return redirect(redirect_to)
        response = func(request, *args, **kwargs)
        return response
    return as_view