from django.conf.urls import patterns, url

from beelogger import views

urlpatterns = patterns('',
    # ex: /polls/
    url(r'^$', views.IndexView.as_view(), name='index'),
    # ex: /polls/5/
    url(r'^test/$', views.TestView.as_view(), name='test'),
    # ex: /polls/5/results/
    url(r'^check-user-state/$', views.CheckUserStateView, name='check_user_state'),
    url(r'^check-user-in-out/$', views.UserCheckInOutView, name='check_user_in_out'),
    url(r'^checked-user-in-out/$', views.UserCheckedInOutView, name='checked_user_in_out'),
)
