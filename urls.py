          # -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('myspy.catalog.urls')),
    (r'^cart/', include('myspy.cart.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns ('',
          # Статика для тестового веб сервера
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            { 'document_root': settings.MEDIA_ROOT}),
    )
