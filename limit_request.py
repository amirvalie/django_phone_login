from django.conf import settings
from django.core.cache import cache


class GenerateLimitation(object):
    """
    We use cache to limit user requests.
    The user limit is based on the IP address.
    In the first part, we store the IP address of the user and the number of requests in the cache.
    and in the next part, which is a decorator,we check whether the number of user requests is valid or not.
    This method allows us to use this class wherever we want.
    """
    expire_cache=getattr(settings,'EXPIRE_CACHE',20)
    def __init__(self,request):
        self.ip_address=request.user.ip_address
        self.get_or_set()

    def get_or_set(self):
        obj=cache.get_or_set(self.ip_address,0,self.expire_after())
        self.inc_cache()
    
    def inc_cache(self):
        cache.incr(self.ip_address)

    def expire_after(self):
        return GenerateLimitation.expire_cache * 60
        
def check_limitation(func):
    """
    in this decorator we check whether the number of user requests is valid or not
    """
    def wrapper(request):
        from .views import invalid_attempts_func
        attempts=cache.get(request.user.ip_address)
        if attempts is None or attempts < getattr(settings,'PHONE_LOGIN_ATTEMPTS',10):
            return func(request)
        return invalid_attempts_func(request)
    return wrapper

