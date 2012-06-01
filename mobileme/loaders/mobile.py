"""
Wrapper class that takes a list of template loaders as an argument and attempts
to load templates from them in order, flavouring the result.
"""

from django.template import TemplateDoesNotExist
from django.template.loader import find_template_loader

from .base import BaseLoader


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

    def load_template(self, template_name, template_dirs=None):
        if self.should_flavour(template_name):
            _template_name = self.prepare_template_name(template_name)
            try:
                return self.find_template(_template_name, template_dirs)
            except TemplateDoesNotExist:
                pass
        return self.find_template(template_name, template_dirs)
