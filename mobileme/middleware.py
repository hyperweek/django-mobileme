from django.utils.cache import patch_vary_headers

from .conf import settings
from .utils import get_flavour_from_request, set_flavour


class DetectMobileMiddleware(object):
    def process_request(self, request):
        flavour = get_flavour_from_request(request)
        set_flavour(flavour, request)

    def process_response(self, request, response):
        patch_vary_headers(response, ['User-Agent'])
        return response


class XFlavourMiddleware(object):
    def process_response(self, request, response):
        patch_vary_headers(response, ['X-Flavour'])
        if 'X-Flavour' not in response:
            response['X-Flavour'] = get_flavour_from_request(request)
        return response


class SetResponseTemplate(object):
    """
    Adds flavoured template when the new SimpleTemplateResponse or
    TemplateResponse is used (new in 1.3)
    https://docs.djangoproject.com/en/1.3/ref/template-response/
    """
    def prepare_template_name(self, flavour, template_name):
        template_name = u'%s/%s' % (flavour, template_name)
        if settings.FLAVOURS_TEMPLATE_PREFIX:
            template_name = settings.FLAVOURS_TEMPLATE_PREFIX + template_name
        return template_name

    def process_template_response(self, request, response):
        if not response.is_rendered:
            template_name = response.template_name
            flavour = get_flavour_from_request(request)
            flavoured_template = self.prepare_template_name(flavour, template_name)
            response.template_name = [flavoured_template, template_name]
        return response
