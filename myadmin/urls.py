from django.conf.urls.defaults import *

urlpatterns = patterns('',
                      url(r'^$', 'myadmin.views.auth', name="auth-page"),
                      url(r'^sales$', 'myadmin.views.sales', name="auth-page"),
                      url(r'^client/(?P<id>[-\w]+)/$', 'myadmin.views.edit_client', name="client-id"),
                      url(r'^client/add$', 'myadmin.views.add_client', name="add-client"),)

