
import middleware

def detect_mobile(view):
    """View Decorator that adds a "mobile" attribute to the request which is True or False depending
       on whether the request should be considered form a mobile phone."""
       
    def detected(request, *args, **kwargs):
        middleware.process_request(request)
        return view(request, *args, **kwargs)
    detected.__doc__ = "%s\n[Wrapped by detect_mobile which detects if the request is from a phone]" % view.__doc__
    return detected


__all__ = ['middleware', 'detect_mobile']