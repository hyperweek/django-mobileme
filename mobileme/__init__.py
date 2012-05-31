import threading

from .conf import settings

_local = threading.local()


def get_flavour(request=None, default=None):
    if request is not None:
        if hasattr(request, 'flavour'):
            flavour = request.flavour

        if flavour and flavour in settings.FLAVOURS:
            return flavour

        if hasattr(request, 'session'):
            flavour = request.session.get(settings.FLAVOURS_SESSION_NAME, None)

        if flavour and flavour in settings.FLAVOURS:
            return flavour

        flavour = request.COOKIES.get(settings.FLAVOURS_COOKIE_NAME)

        if flavour and flavour in settings.FLAVOURS:
            return flavour

    flavour = getattr(_local, 'flavour', default)
    if flavour and flavour in settings.FLAVOURS:
        return flavour

    return settings.FLAVOURS[0]


def set_flavour(flavour, request=None):
    if flavour not in settings.FLAVOURS:
        raise ValueError(
            u"'%r' is no valid flavour. Allowed flavours are: %s" % (
                flavour,
                ', '.join(settings.FLAVOURS),))
    if request:
        request.flavour = flavour
    _local.flavour = flavour
