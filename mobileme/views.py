from django import http

from .conf import settings
from .utils import check_for_flavour


def set_flavour(request, **kwargs):
    """
    Redirect to a given url while setting the chosen flavour in the
    session or cookie. The url and the flavour code need to be
    specified in the request parameters.

    Since this view changes how the user will see the rest of the site, it must
    only be accessed as a POST request. If called as a GET request, it will
    redirect to the page in the request (the 'next' parameter) without changing
    any state.
    """
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = http.HttpResponseRedirect(next)
    if request.method == 'POST':
        flavour = request.POST.get('flavour', None)
        if flavour and check_for_flavour(flavour):
            if hasattr(request, 'session'):
                request.session[settings.FLAVOURS_SESSION_NAME] = flavour
            else:
                response.set_cookie(settings.FLAVOURS_COOKIE_NAME, flavour)
    return response
