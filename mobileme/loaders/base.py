from django.template.base import TemplateDoesNotExist
from django.template.loader import BaseLoader as DjangoBaseLoader, make_origin

from ..conf import settings
from ..utils import get_flavour


class BaseLoader(DjangoBaseLoader):
    def should_flavour(self, template_name):
        flavour = get_flavour()
        # Handle no mobile template according to the project settings
        if flavour == settings.DEFAULT_NOMOBILE_FLAVOUR:
            return settings.FLAVOURS_NOMOBILE_TEMPLATE
        # Ignore template that are already flavoured
        if template_name.startswith('%s/' % flavour):
            return False
        return True

    def prepare_template_name(self, template_name):
        template_name = u'%s/%s' % (get_flavour(), template_name)
        if settings.FLAVOURS_TEMPLATE_PREFIX:
            template_name = settings.FLAVOURS_TEMPLATE_PREFIX + template_name
        return template_name

    def find_template(self, name, dirs=None):
        for loader in self.loaders:
            try:
                template, display_name = loader(name, dirs)
                return (template, make_origin(display_name, loader, name,
                                              dirs))
            except TemplateDoesNotExist:
                pass
        raise TemplateDoesNotExist(name)
