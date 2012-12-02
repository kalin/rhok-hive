from django.conf.urls import patterns, include, url
from beelogger import urls as beelogger_urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hive.views.home', name='home'),
    # url(r'^hive/', include('hive.foo.urls')),
    url(r'^beelogger/', include(beelogger_urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
