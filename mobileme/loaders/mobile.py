"""
Wrapper class that takes a list of template loaders as an argument and attempts
to load templates from them in order, flavouring the result.
"""

from django.template import TemplateDoesNotExist
from django.template.loader import find_template_loader, make_origin, BaseLoader

from .. import get_flavour
from ..conf import settings


class Loader(BaseLoader):
    is_usable = True

    def __init__(self, loaders):
        self._loaders = loaders
        self._cached_loaders = []

    @property
    def loaders(self):
        # Resolve loaders on demand to avoid circular imports
        if not self._cached_loaders:
            for loader in self._loaders:
                self._cached_loaders.append(find_template_loader(loader))
        return self._cached_loaders

    def prepare_template_name(self, template_name):
        template_name = u'%s/%s' % (get_flavour(), template_name)
        if settings.FLAVOURS_TEMPLATE_PREFIX:
            template_name = settings.FLAVOURS_TEMPLATE_PREFIX + template_name
        return template_name

    def find_template(self, name, dirs=None):
        for loader in self.loaders:
            try:
                template, display_name = loader(name, dirs)
                return (template, make_origin(display_name, loader, name, dirs))
            except TemplateDoesNotExist:
                pass
        raise TemplateDoesNotExist(name)

    def load_template(self, template_name, template_dirs=None):
        flavoured_template_name = self.prepare_template_name(template_name)
        try:
            template, origin = self.find_template(flavoured_template_name,
                                                  template_dirs)
        except TemplateDoesNotExist:
            template, origin = self.find_template(template_name, template_dirs)
        return template, None
