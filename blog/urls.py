from django.conf.urls.defaults import *

urlpatterns = patterns('',
                          url(r'^$', 'myspy.blog.views.blog', name="main-page"),
)
