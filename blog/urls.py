from django.conf.urls.defaults import *

urlpatterns = patterns('',
                          url(r'^$', 'catalog.views.index', name="main-page"),
)