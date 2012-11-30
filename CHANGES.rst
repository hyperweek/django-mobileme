=========
Changelog
=========

0.7.1 / 2012-11-30
==================

  * Sane default when retrieving flavour.

0.7.0 / 2012-11-06
==================

REFACTORED ALL THE THINGS!!!

  * Django 1.4+ is now required.
  * Renamed SetTemplateResponseMiddleware to TemplateForFlavourMiddleware.
  * Added a replacement of Django's inclusion_tag.
  * Removed set_flavour and get_flavour functions.
  * Renamed get_flavour_from_request to flavour_from_request.
  * No longer relies on threadlocals.

0.4.0 / 2012-06-01
==================

  * Added a BaseLoader template loader for code factoring and some template
    loading optimizations.
  * Added a cached template loader.
  * Moved template loader to loaders.mobile module.

0.3.0 / 2012-05-31
==================

  * Renamed django-mobile to django-mobileme.
  * Added template response middleware.
  * Major refactor of django-mobile.
