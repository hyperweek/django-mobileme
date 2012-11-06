from django.utils.cache import patch_vary_headers

from .utils import (flavour_from_request, check_for_flavour,
                    templates_for_flavour)


class DetectMobileMiddleware(object):
    def process_request(self, request):
        flavour = flavour_from_request(request)
        request.flavour = flavour

    def process_response(self, request, response):
        patch_vary_headers(response, ['User-Agent'])
        return response


class XFlavourMiddleware(object):
    def process_request(self, request):
        flavour = request.META.get('HTTP_X_FLAVOUR', None)
        if not (flavour and check_for_flavour(flavour)):
            flavour = flavour_from_request(request)
        request.META['HTTP_X_FLAVOUR'] = flavour
        request.flavour = flavour

    def process_response(self, request, response):
        if 'X-Flavour' not in response:
            response['X-Flavour'] = request.flavour
        patch_vary_headers(response, ['X-Flavour'])
        return response


class TemplateForFlavourMiddleware(object):
    """
    Inserts flavour-specific templates to the template list.
    """
    def process_template_response(self, request, response):
        if hasattr(response, 'template_name') and not response.is_rendered:
            templates = templates_for_flavour(request, response.template_name)
            response.template_name = templates
        return response

