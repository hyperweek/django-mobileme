from django import http

from .conf import settings


def set_flavour(request, flavour=None, **kwargs):
    """
    Redirect to a given url while setting the chosen flavour in the
    session or cookie. The url and the flavour code need to be
    specified in the request parameters.
    """
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = http.HttpResponseRedirect(next)
    if request.method == 'POST':
        flavour = request.POST.get('flavour', None)
    if flavour and flavour in settings.FLAVOURS:
        if hasattr(request, 'session'):
            request.session[settings.FLAVOURS_SESSION_NAME] = flavour
        else:
            response.set_cookie(settings.FLAVOURS_COOKIE_NAME, flavour)
    return response
