from settings import *


MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
) + MIDDLEWARE_CLASSES + (
    'mobileme.middleware.XFlavourMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)
