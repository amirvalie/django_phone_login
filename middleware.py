class IpAddressMiddleware:
    '''
    To access the IP address more easily, we give the IP address as an attribute to the Use object.
    '''
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]        
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        request.user.ip_address=ip

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response