from django.conf.urls.defaults import *

urlpatterns = patterns('',
                      url(r'^$', 'myadmin.views.auth', name="auth-page"),
                      url(r'^sales$', 'myadmin.views.sales', name="sales-page"),
                      url(r'^client/(?P<id>[-\w]+)/$', 'myadmin.views.edit_client', name="edit-client"),
                      url(r'^client/add$', 'myadmin.views.add_client', name="add-client"),
                      url(r'^store$', 'myadmin.views.store', name="store-page"),
                      url(r'^cash$', 'myadmin.views.cash', name="cash-page"),
                      url(r'^cash/add$', 'myadmin.views.add_cashflow', name="cash-page"),)

