from django.conf.urls import patterns, url

from beelogger import views

urlpatterns = patterns('',
    # ex: /polls/
    url(r'^$', views.IndexView.as_view(), name='index'),
    # ex: /polls/5/
    url(r'^test/$', views.TestView.as_view(), name='test'),
)
