from django.conf.urls import patterns, url

from beelogger import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^check-user-pin/$', views.CheckUserStateView, name='check_user_pin'),
    url(r'^check-user-in-out/$', views.UserCheckInOutView, name='check_user_in_out'),
    url(r'^csvdump/$', views.CSVDumpView, name='csv_dump'),
    url(r'^csvmonthdump/$', views.CSVDumpCurrentMonth, name='csv_month_dump'),
    url(r'^csvuserdump/$', views.CSVDumpUser, name='csv_dump_user'),
)
