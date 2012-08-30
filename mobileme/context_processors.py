from .conf import settings
from .utils import get_flavour


def flavour(request):
    return {
        'flavour': get_flavour(request),
    }


def is_mobile(request):
    return {
        'is_mobile': get_flavour(request) == settings.DEFAULT_MOBILE_FLAVOUR,
    }
