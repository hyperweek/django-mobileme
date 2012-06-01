import re
import threading

from .conf import settings

_local = threading.local()

user_agents_test_match = r'^(?:%s)' % '|'.join([
    "w3c ", "acs-", "alav", "alca", "amoi", "audi",
    "avan", "benq", "bird", "blac", "blaz", "brew",
    "cell", "cldc", "cmd-", "dang", "doco", "eric",
    "hipt", "inno", "ipaq", "java", "jigs", "kddi",
    "keji", "leno", "lg-c", "lg-d", "lg-g", "lge-",
    "maui", "maxo", "midp", "mits", "mmef", "mobi",
    "mot-", "moto", "mwbp", "nec-", "newt", "noki",
    "xda",  "palm", "pana", "pant", "phil", "play",
    "port", "prox", "qwap", "sage", "sams", "sany",
    "sch-", "sec-", "send", "seri", "sgh-", "shar",
    "sie-", "siem", "smal", "smar", "sony", "sph-",
    "symb", "t-mo", "teli", "tim-", "tosh", "tsm-",
    "upg1", "upsi", "vk-v", "voda", "wap-", "wapa",
    "wapi", "wapp", "wapr", "webc", "winw", "winw",
    "xda-",
])
user_agents_test_search = "(?:%s)" % '|'.join([
    'up.browser', 'up.link', 'mmp', 'symbian', 'smartphone', 'midp',
    'wap', 'phone', 'windows ce', 'pda', 'mobile', 'mini', 'palm',
    'netfront', 'opera mobi',
])
user_agents_exception_search = u"(?:%s)" % u'|'.join([
    'ipad',
])

http_accept_re = re.compile("application/vnd\.wap\.xhtml\+xml", re.IGNORECASE)
user_agents_test_match_re = re.compile(user_agents_test_match, re.IGNORECASE)
user_agents_test_search_re = re.compile(user_agents_test_search, re.IGNORECASE)
user_agents_exception_search_re = re.compile(user_agents_exception_search, re.IGNORECASE)


def get_flavour_from_request(request):
    """
    Analyzes the request to find what flavour the user wants the system to
    show. Only flavours listed in settings.FLAVOURS are taken into account.
    """
    from mobileme.conf import settings

    if hasattr(request, 'session'):
        flavour = request.session.get(settings.FLAVOURS_SESSION_NAME, None)
    else:
        flavour = request.COOKIES.get(settings.FLAVOURS_COOKIE_NAME)

    if flavour and flavour in settings.FLAVOURS:
        return flavour

    is_mobile = False
    if 'HTTP_USER_AGENT' in request.META:
        user_agent = request.META['HTTP_USER_AGENT']

        # Test common mobile values.
        if user_agents_test_search_re.search(user_agent) and \
            not user_agents_exception_search_re.search(user_agent):
            is_mobile = True
        else:
            # Nokia like test for WAP browsers.
            # http://www.developershome.com/wap/xhtmlmp/xhtml_mp_tutorial.asp?page=mimeTypesFileExtension
            if 'HTTP_ACCEPT' in request.META:
                http_accept = request.META['HTTP_ACCEPT']
                if http_accept_re.search(http_accept):
                    is_mobile = True

        if not is_mobile:
            # Now we test the user_agent from a big list.
            if user_agents_test_match_re.match(user_agent):
                is_mobile = True

    return is_mobile and settings.DEFAULT_MOBILE_FLAVOUR or settings.FLAVOURS[0]


def get_flavour(request=None, default=None):
    if request is not None:
        if hasattr(request, 'flavour'):
            flavour = request.flavour

        if flavour and flavour in settings.FLAVOURS:
            return flavour

        if hasattr(request, 'session'):
            flavour = request.session.get(settings.FLAVOURS_SESSION_NAME, None)

        if flavour and flavour in settings.FLAVOURS:
            return flavour

        flavour = request.COOKIES.get(settings.FLAVOURS_COOKIE_NAME)

        if flavour and flavour in settings.FLAVOURS:
            return flavour

    flavour = getattr(_local, 'flavour', default)
    if flavour and flavour in settings.FLAVOURS:
        return flavour

    return settings.FLAVOURS[0]


def set_flavour(flavour, request=None):
    if flavour not in settings.FLAVOURS:
        raise ValueError(
            u"'%r' is no valid flavour. Allowed flavours are: %s" % (
                flavour,
                ', '.join(settings.FLAVOURS),))
    if request:
        request.flavour = flavour
    _local.flavour = flavour
