"""
Wrapper class that takes a list of template loaders as an argument and attempts
to load templates from them in order, flavouring and caching the result.
"""

from django.template.base import TemplateDoesNotExist
from django.template.loader import (get_template_from_string,
                                    find_template_loader)
from django.utils.hashcompat import sha_constructor

from .base import BaseLoader


class Loader(BaseLoader):
    is_usable = True

    def __init__(self, loaders):
        self.template_cache = {}
        self._loaders = loaders
        self._cached_loaders = []

    @property
    def loaders(self):
        # Resolve loaders on demand to avoid circular imports
        if not self._cached_loaders:
            for loader in self._loaders:
                if isinstance(loader, tuple) or isinstance(loader, list) \
                    and loader[0] == 'mobileme.loaders.mobile.Loader':
                    # If we've found the mobile template loader, append all
                    # related loaders to the cached list.
                    _loader = find_template_loader(loader)
                    self._cached_loaders.extend(_loader.loaders)
                else:
                    self._cached_loaders.append(find_template_loader(loader))
        return self._cached_loaders

    def _load_template(self, template_name, template_dirs=None):
        key = template_name
        if template_dirs:
            # If template directories were specified, use a hash to
            # differentiate
            hsh = sha_constructor('|'.join(template_dirs)).hexdigest()
            key = '-'.join([template_name, hsh])

        if key not in self.template_cache:
            template, origin = self.find_template(template_name, template_dirs)
            if not hasattr(template, 'render'):
                try:
                    template = get_template_from_string(template, origin,
                                                        template_name)
                except TemplateDoesNotExist:
                    # If compiling the template we found
                    # raisesTemplateDoesNotExist, back off to returning the
                    # source and display name for the template we were asked
                    # to load. This allows for correct identification (later)
                    # of the actual template that does not exist.
                    return template, origin
            self.template_cache[key] = template
        return self.template_cache[key], None

    def load_template(self, template_name, template_dirs=None):
        if self.should_flavour(template_name):
            _template_name = self.prepare_template_name(template_name)
            try:
                return self._load_template(_template_name, template_dirs)
            except TemplateDoesNotExist:
                pass
        return self._load_template(template_name, template_dirs)

    def reset(self):
        "Empty the template cache."
        self.template_cache.clear()
