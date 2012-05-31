from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from django.template import RequestContext

from mobileme.decorators import cache_page


def index(request):
    return render_to_response('index.html', {
    }, context_instance=RequestContext(request))


urlpatterns = patterns('',
    url(r'^$', index),
    url(r'^cached/$', cache_page(60 * 10)(index)),
)
