from django.conf.urls.defaults import *

urlpatterns = patterns('',
                      url(r'^$', 'myadmin.views.auth', name="auth-page"),
                      url(r'^logout/$', 'myadmin.views.logout_view', name="logout-page"),
                      url(r'^sales/$', 'myadmin.views.sales_active', name="active-sales-page"),
                      url(r'^sales/(?P<when>[-\w]+)/$', 'myadmin.views.sales', name="date_sales-page"),
                      url(r'^client/(?P<id>[-\w]+)/$', 'myadmin.views.edit_client', name="edit-client"),
                      url(r'^client/(?P<id>[-\w]+)/delete$', 'myadmin.views.delete_client', name="delete-client"),
                      url(r'^client/(?P<id>[-\w]+)/copy$', 'myadmin.views.copy_client', name="copy-client"),
                      url(r'^client/add$', 'myadmin.views.add_client', name="add-client"),
                      url(r'^store$', 'myadmin.views.store', name="store-page"),
                      url(r'^cash/add/$', 'myadmin.views.add_cashflow', name="cash-page"),
                      url(r'^cash/(?P<when>[-\w]+)/$', 'myadmin.views.cash', name="date_cash-page"),
                      url(r'^cash/edit/(?P<id>[-\w]+)/$', 'myadmin.views.edit_cashflow', name="edit-cashflow"),
                      url(r'^cash/editbalance$', 'myadmin.views.edit_balance', name="edit-balance"),
                      url(r'^tasks/$', 'myadmin.views.tasks', name="tasks-page"),
                      url(r'^tasks/done/$', 'myadmin.views.show_taskdone', name="done-task"),
                      url(r'^tasks/my/$', 'myadmin.views.my_tasks', name="my-tasks"),
                      url(r'^tasks/myown/$', 'myadmin.views.myown_tasks', name="myown-tasks"),
                      url(r'^tasks/add/$', 'myadmin.views.add_task', name="add-task"),
                      url(r'^tasks/edit/(?P<id>[-\w]+)/$', 'myadmin.views.edit_task', name="edit-task"),
                      url(r'^tasks/(?P<id>[-\w]+)/is_done$', 'myadmin.views.task_done', name="task-done"),
                      url(r'^tasks/edit/(?P<id>[-\w]+)/delete$', 'myadmin.views.delete_task', name="delete-task"),
                      url(r'^tasks/(?P<id>[-\w]+)/$', 'myadmin.views.task', name="task-page"),
                      url(r'^orders/$', 'myadmin.views.orders', name="orders-page"),
                      url(r'^orders/done/$', 'myadmin.views.show_orderdone', name="done-order"),
                      url(r'^orders/add/$', 'myadmin.views.add_order', name="add-order"),
                      url(r'^orders/(?P<id>[-\w]+)/$', 'myadmin.views.order', name="order-page"),
                      url(r'^orders/(?P<id>[-\w]+)/is_done$', 'myadmin.views.order_done', name="order-done"),
                      url(r'^orders/edit/(?P<id>[-\w]+)/$', 'myadmin.views.edit_order', name="edit-order"),
                      url(r'^orders/edit/(?P<id>[-\w]+)/delete$', 'myadmin.views.delete_order', name="delete-order"),
                      url(r'^statistic/$', 'myadmin.views.statistic', name="statistic-page"),)
