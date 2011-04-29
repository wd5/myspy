from django.conf.urls.defaults import *

urlpatterns = patterns('',
                          url(r'^$', 'blog.views.index', name="main-page"),
)