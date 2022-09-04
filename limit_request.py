from django.conf import settings
from django.core.cache import cache


class GenerateLimitation(object):
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
        "Used for setting the memcached cache expiry"
        return GenerateLimitation.expire_cache * 60
        
def check_limitation(func):
    def wrapper(request):
        from .views import invalid_attempts_func
        attempts=cache.get(request.user.ip_address)
        if attempts is None or attempts < getattr(settings,'PHONE_LOGIN_ATTEMPTS',10):
            return func(request)
        return invalid_attempts_func(request)
    return wrapper

