from .conf import settings


def flavour(request):
    return {
        'flavour': request.flavour,
    }


def is_mobile(request):
    return {
        'is_mobile': request.flavour == settings.DEFAULT_MOBILE_FLAVOUR,
    }
