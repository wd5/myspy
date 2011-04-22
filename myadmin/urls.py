from django.conf.urls.defaults import *

urlpatterns = patterns('',
                      url(r'^$', 'myadmin.views.auth', name="auth-page"),
                      url(r'^sales/$', 'myadmin.views.sales', name="sales-page"),
                      url(r'^sales/(?P<when>[-\w]+)/$', 'myadmin.views.date_sales', name="date_sales-page"),
                      url(r'^client/(?P<id>[-\w]+)/$', 'myadmin.views.edit_client', name="edit-client"),
                      url(r'^client/(?P<id>[-\w]+)/delete$', 'myadmin.views.delete_client', name="delete-client"),
                      url(r'^client/add$', 'myadmin.views.add_client', name="add-client"),
                      url(r'^store$', 'myadmin.views.store', name="store-page"),
                      url(r'^cash$', 'myadmin.views.cash', name="cash-page"),
                      url(r'^cash/(?P<id>[-\w]+)/$', 'myadmin.views.edit_cashflow', name="edit-cashflow"),
                      url(r'^cash/add$', 'myadmin.views.add_cashflow', name="cash-page"),
                      url(r'^cash/editbalance$', 'myadmin.views.edit_balance', name="edit-balance"),)

