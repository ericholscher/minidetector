
from useragents import search_strings

class Middleware(object):
    @staticmethod
    def process_request(request):
        """Adds a "mobile" attribute to the request which is True or False depending
           on whether the request should be considered form a mobile phone."""

        if request.META.has_key("HTTP_X_OPERAMINI_FEATURES"):
            #Then it's running opera mini. 'Nuff said.
            request.mobile = True
            return None

        if request.META.has_key("HTTP_ACCEPT"):
            s = request.META["HTTP_ACCEPT"].lower()
            if 'application/vnd.wap.xhtml+xml' in s:
                # Then it's a wap browser
                request.mobile = True
                return None

        if request.META.has_key("HTTP_USER_AGENT"):
            for ua in search_strings:
                s = request.META["HTTP_USER_AGENT"].lower()
                if ua in s:
                    request.mobile = True
                    return None

        #Otherwise it's not a mobile
        request.mobile = False
        return None

def detect_mobile(view):
    """View Decorator that adds a "mobile" attribute to the request which is True or False depending
       on whether the request should be considered form a mobile phone."""
       
    def detected(request, *args, **kwargs):
        middleware.process_request(request)
        return view(request, *args, **kwargs)
    detected.__doc__ = "%s\n[Wrapped by detect_mobile which detects if the request is from a phone]" % view.__doc__
    return detected


__all__ = ['Middleware', 'detect_mobile']