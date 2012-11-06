"""
Credits: https://github.com/stephenmcd/mezzanine/blob/master/mezzanine/template/__init__.py
"""
from functools import wraps

from django import template
from django.template.context import Context
from django.template.loader import get_template, select_template

from .utils import templates_for_flavour


class Library(template.Library):
    def inclusion_tag(self, name, context_class=Context, takes_context=False):
        """
        Replacement for Django's ``inclusion_tag`` which looks up device
        specific templates at render time.
        """
        def tag_decorator(tag_func):
            @wraps(tag_func)
            def tag_wrapper(parser, token):
                class InclusionTagNode(template.Node):
                    def render(self, context):
                        # Never cache the template so we can render it when
                        # switching from desktop to mobile version
                        try:
                            request = context['request']
                        except KeyError:
                            t = get_template(name)
                        else:
                            ts = templates_for_flavour(request, name)
                            t = select_template(ts)
                        self.nodelist = t.nodelist
                        # --//--
                        parts = [template.Variable(part).resolve(context)
                                 for part in token.split_contents()[1:]]
                        if takes_context:
                            parts.insert(0, context)
                        result = tag_func(*parts)
                        autoescape = context.autoescape
                        context = context_class(result, autoescape=autoescape)
                        return self.nodelist.render(context)
                return InclusionTagNode()
            return self.tag(tag_wrapper)
        return tag_decorator
