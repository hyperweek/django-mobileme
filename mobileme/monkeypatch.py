from inspect import getargspec

import django
from django import template
from django.template.base import Library, generic_tag_compiler
from django.template.context import Context
from django.utils.itercompat import is_iterable

if django.VERSION < (1, 4):
    from django.template.base import Variable, Node, TemplateSyntaxError
    from django.utils.functional import curry

    class _Library(Library):
        def inclusion_tag(self, file_name, context_class=Context, takes_context=False):
            def dec(func):
                params, xx, xxx, defaults = getargspec(func)
                if takes_context:
                    if params[0] == 'context':
                        params = params[1:]
                    else:
                        raise TemplateSyntaxError("Any tag function decorated with takes_context=True must have a first argument of 'context'")

                class InclusionNode(Node):
                    def __init__(self, vars_to_resolve):
                        self.vars_to_resolve = map(Variable, vars_to_resolve)

                    def render(self, context):
                        resolved_vars = [var.resolve(context) for var in self.vars_to_resolve]
                        if takes_context:
                            args = [context] + resolved_vars
                        else:
                            args = resolved_vars

                        dict = func(*args)

                        # Never cache the template so we can render it when
                        # switching from desktop to mobile version
                        from django.template.loader import get_template, select_template
                        if not isinstance(file_name, basestring) and is_iterable(file_name):
                            t = select_template(file_name)
                        else:
                            t = get_template(file_name)
                        self.nodelist = t.nodelist
                        # --
                        new_context = context_class(dict, autoescape=context.autoescape)
                        # Copy across the CSRF token, if present, because inclusion
                        # tags are often used for forms, and we need instructions
                        # for using CSRF protection to be as simple as possible.
                        csrf_token = context.get('csrf_token', None)
                        if csrf_token is not None:
                            new_context['csrf_token'] = csrf_token
                        return self.nodelist.render(new_context)

                compile_func = curry(generic_tag_compiler, params, defaults, getattr(func, "_decorated_function", func).__name__, InclusionNode)
                compile_func.__doc__ = func.__doc__
                self.tag(getattr(func, "_decorated_function", func).__name__, compile_func)
                return func
            return dec
else:
    from functools import partial
    from django.template.base import TagHelperNode, Template

    class _Library(Library):
        def inclusion_tag(self, file_name, context_class=Context, takes_context=False, name=None):
            def dec(func):
                params, varargs, varkw, defaults = getargspec(func)

                class InclusionNode(TagHelperNode):

                    def render(self, context):
                        resolved_args, resolved_kwargs = self.get_resolved_arguments(context)
                        _dict = func(*resolved_args, **resolved_kwargs)

                        from django.template.loader import get_template, select_template
                        if isinstance(file_name, Template):
                            t = file_name
                        elif not isinstance(file_name, basestring) and is_iterable(file_name):
                            t = select_template(file_name)
                        else:
                            t = get_template(file_name)
                        self.nodelist = t.nodelist
                        new_context = context_class(_dict, **{
                            'autoescape': context.autoescape,
                            'current_app': context.current_app,
                            'use_l10n': context.use_l10n,
                            'use_tz': context.use_tz,
                        })
                        # Copy across the CSRF token, if present, because
                        # inclusion tags are often used for forms, and we need
                        # instructions for using CSRF protection to be as simple
                        # as possible.
                        csrf_token = context.get('csrf_token', None)
                        if csrf_token is not None:
                            new_context['csrf_token'] = csrf_token
                        return self.nodelist.render(new_context)

                function_name = (name or
                    getattr(func, '_decorated_function', func).__name__)
                compile_func = partial(generic_tag_compiler,
                    params=params, varargs=varargs, varkw=varkw,
                    defaults=defaults, name=function_name,
                    takes_context=takes_context, node_class=InclusionNode)
                compile_func.__doc__ = func.__doc__
                self.tag(function_name, compile_func)
                return func
            return dec

template.Library = _Library
