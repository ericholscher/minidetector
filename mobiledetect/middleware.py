#coding: utf8

from useragents import search_strings

def process_request(request):
    """Adds a "mobile" attribute to the request which is True or False depending
       on whether the request should be considered form a mobile phone."""

    if request.META.has_key("HTTP_X_OPERAMINI_FEATURES"):
        #Then it's running opera mini. 'Nuff said.
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