from django.views.decorators.cache import cache_page as _cache_page
from django.utils.decorators import decorator_from_middleware

from .middleware import XFlavourMiddleware


vary_on_flavour = decorator_from_middleware(XFlavourMiddleware)


def cache_page(*args, **kwargs):
    """
    Same as django's ``cache_page`` decorator, but wraps the view into
    ``vary_on_flavour`` decorator before. Makes it possible to serve multiple
    flavours without getting into trouble with django's caching that doesn't
    know about flavours.
    """
    decorator = _cache_page(*args, **kwargs)

    def flavoured_decorator(func):
        return decorator(vary_on_flavour(func))
    return flavoured_decorator
