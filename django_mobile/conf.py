# -*- coding: utf-8 -*-
from django.conf import settings as django_settings


class SettingsProxy(object):
    def __init__(self, settings, defaults):
        self.settings = settings
        self.defaults = defaults

    def __getattr__(self, attr):
        try:
            return getattr(self.settings, attr)
        except AttributeError:
            try:
                return getattr(self.defaults, attr)
            except AttributeError:
                raise AttributeError(u'settings object has no attribute "%s"' % attr)


class defaults(object):
    FLAVOURS = ('full', 'mobile',)
    DEFAULT_MOBILE_FLAVOUR = 'mobile'
    FLAVOURS_TEMPLATE_PREFIX = ''
    FLAVOURS_COOKIE_NAME = 'flavour'
    FLAVOURS_SESSION_NAME = 'flavour'


settings = SettingsProxy(django_settings, defaults)
