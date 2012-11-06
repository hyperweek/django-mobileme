===============
django-mobileme
===============

``mobileme`` provides a simple way to detect mobile browsers and gives
you tools at your hand to render some different templates to deliver a mobile
version of your site to the user.


Installation
============

*Pre-Requirements:* ``mobileme`` depends on django's session framework. So
before you try to use ``mobileme`` make sure that the sessions framework
is enabled and working.

    1. Install ``mobileme`` with your favourite python tool, e.g. with
       ``easy_install django-mobileme`` or ``pip install django-mobileme``.

    2. Add ``mobileme.middleware.DetectMobileMiddleware`` to your
       ``MIDDLEWARE_CLASSES`` setting.

    3. Add ``mobileme.middleware.XFlavourMiddleware`` to your
       ``MIDDLEWARE_CLASSES`` setting. Make sure it's listed *after*
       ``MobileDetectionMiddleware`` and also after ``SessionMiddleware``.

    4. Add ``mobileme.middleware.TemplateForFlavourMiddleware`` to your
       ``MIDDLEWARE_CLASSES`` setting.

    5. Add ``mobileme.context_processors.flavour`` to your
       ``TEMPLATE_CONTEXT_PROCESSORS`` setting.

Now you should be able to use ``mobileme`` in its glory. Read below of how
things work and which settings can be tweaked to modify ``mobileme``'s
behaviour.


Usage
=====

The concept of ``mobileme`` is build around the ideas of different
*flavours* for your site. For example the *mobile* version is described as
one possible *flavour*, the desktop version as another.

This makes it possible to provide many possible designs instead of just
differentiating between a full desktop experience and one mobile version.  You
can make multiple mobile flavours available e.g. one for mobile safari on the
iPhone and Android as well as one for Opera and an extra one for the internet
tablets like the iPad.

*Note:* By default ``mobileme`` only distinguishes between *full* and
*mobile* flavour.

After the correct flavour is somehow chosen by the middlewares, it's
assigned to the ``request.flavour`` attribute. You can use this in your views
to provide separate logic.

This flavour is then use to transparently choose custom templates for this
special flavour. The selected template will have the current flavour prefixed
to the template name you actually want to render. This means when
``TemplateResponse('index.html', ...)`` is called with the *mobile* flavour
being active will actually return a response rendered with the
``mobile/index.html`` template. However if this flavoured template is not
available it will gracefully fallback to the default ``index.html`` template.

In some cases its not the desired way to have a completely separate templates
for each flavour. You can also use the ``{{ flavour }}`` template variable to
only change small aspects of a single template. A short example::

    <html>
    <head>
        <title>My site {% if flavour == "mobile" %}(mobile version){% endif %}</title>
    </head>
    <body>
        ...
    </body>
    </html>

This will add ``(mobile version)`` to the title of your site if viewed with
the mobile flavour enabled.

*Note:* The ``flavour`` template variable is only available if you have set up the
``mobileme.context_processors.flavour`` context processor and used
django's ``RequestContext`` as context instance to render the template.

Changing the current flavour
----------------------------

As a convenience, ``mobileme`` comes with a view,
mobile.views.set_flavour(), that sets a user's flavour preference and
redirects to a given URL or, by default, back to the previous page.

Activate this view by adding the following line to your URLconf:

url(r'^setflavour/$', 'mobileme.views.set_flavour', name="set_flavour"),

(Note that this example makes the view available at /setflavour/.)

The view expects to be called via the POST method, with a flavour
parameter set in request. If session support is enabled, the view saves
the flavour choice in the user's session. Otherwise, it saves the
flavour choice in a cookie that is by default named flavour. (The name
can be changed through the FLAVOURS_COOKIE_NAME setting.)

After setting the language choice, ``mobileme`` redirects the user,
following this algorithm:

    * ``mobileme`` looks for a next parameter in the POST data.

    * If that doesn't exist, or is empty, ``mobileme`` tries the URL in
      the Referrer header.

    * If that's empty -- say, if a user's browser suppresses that header --
      then the user will be redirected to / (the site root) as a fallback.

Here's example HTML template code::

    <form action="/i18n/setlang/" method="post">
    {% csrf_token %}
    <input name="next" type="hidden" value="{{ redirect_to }}" />
    <select name="language">
    {% get_language_info_list for LANGUAGES as languages %}
    {% for language in languages %}
    <option value="{{ language.code }}">{{ language.name_local }} ({{ language.code }})</option>
    {% endfor %}
    </select>
    <input type="submit" value="Go" />
    </form>

In this example, ``mobileme`` looks up the URL of the page to which the
user will be redirected in the redirect_to context variable.

Notes on caching
----------------

Django is shipping with some convenience methods to easily cache your views.
One of them is ``django.views.decorators.cache.cache_page``. The problem with
caching a whole page in conjunction with ``mobileme`` is, that django's
caching system is not aware of flavours. This means that if the first request
to a page is served with a mobile flavour, the second request might also
get a page rendered with the mobile flavour from the cache -- even if the
second one was requested by a desktop browser.

``mobileme`` is shipping with it's own implementation of ``cache_page``
to resolve this issue. Please use ``mobileme.cache.cache_page`` instead
of django's own ``cache_page`` decorator.

You can also use django's caching middlewares
``django.middleware.cache.UpdateCacheMiddleware`` and
``FetchFromCacheMiddleware`` like you already do. But to make them aware of
flavours, you need to add
``mobileme.cache.middleware.XFlavourMiddleware`` as second last item
in the ``MIDDLEWARE_CLASSES`` settings, right before
``FetchFromCacheMiddleware``.


Reference
=========

``mobileme.context_processors.flavour``

    Context processor that adds the current flavour as *flavour* to the
    context.

``mobileme.context_processors.is_mobile``

    This context processor will add a *is_mobile* variable to the context
    which is ``True`` if the current flavour equals the
    ``DEFAULT_MOBILE_FLAVOUR`` setting.

``mobileme.middleware.DetectMobileMiddleware``

    Detects if a mobile browser tries to access the site and sets the flavour
    to ``DEFAULT_MOBILE_FLAVOUR`` settings value in case.

``mobileme.cache.middleware.XFlavourMiddleware``

    Adds ``X-Flavour`` header to ``request.META`` in ``process_request`` and
    adds this header to ``response['Vary']`` in ``process_response``.

``mobileme.cache.cache_page``

    Same as django's ``cache_page`` decorator but applies ``vary_on_flavour``
    before the view is decorated with
    ``django.views.decorators.cache.cache_page``.

``mobileme.cache.vary_on_flavour``

    ``DEFAULT_MOBILE_FLAVOUR`` setting.
    A decorator created from the ``XFlavourMiddleware`` middleware.


Settings
========

Here is a list of settings that are used by ``mobileme`` and can be
changed in your own ``settings.py``:

FLAVOURS
--------

A list of available flavours for your site.

**Default:** ``('full', 'mobile')``

DEFAULT_MOBILE_FLAVOUR
----------------------

The flavour which is chosen if the built-in ``DetectMobileMiddleware``
detects a mobile browser.

**Default:** ``mobile``

DEFAULT_NOMOBILE_FLAVOUR
------------------------

The flavour which is chosen if the built-in ``DetectMobileMiddleware``
doesn't detects a mobile browser.

**Default:** ``full``

FLAVOURS_TEMPLATE_PREFIX
------------------------

This string will be prefixed to the template names when searching for
flavoured templates. This is useful if you have many flavours and want to
store them in a common subdirectory. Example::

    # Let's say that flavour is 'mobile'
    from django.template.response import TemplateResponse
    TemplateResponse('index.html') # will render 'mobile/index.html'

    # now add this to settings.py
    FLAVOURS_TEMPLATE_PREFIX = 'flavours/'

    # and try again
    TemplateResponse('index.html') # will render 'flavours/mobile/index.html'

**Default:** ``''`` (empty string)

FLAVOURS_COOKIE_NAME
--------------------

The name of the cookie to use for the language cookie. This can be
whatever you want (but should be different from SESSION_COOKIE_NAME).

**Default:** ``'flavour'``

FLAVOURS_SESSION_KEY
--------------------

The user's preference set with the POST parameter is stored in the
user's session when available. This setting determines which session key
is used to hold this information.

**Default:** ``'flavour'``
