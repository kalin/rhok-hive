from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from beelogger.models import HiveUser, Check
import datetime

class TestView(TemplateView):
    template_name = 'test.html'

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)

        context['hiveuser'] = HiveUser.objects.all()

        context['today'] = datetime.datetime.now()

        return context

class IndexView(TemplateView):
    template_name = 'beelogger/index.html'

""" Returns state of user """
def CheckUserStateView(request):
    user = HiveUser.objects.filter(user__username=request.POST['pin'])
    if user:
        if user[0].is_checked_in():
            text = 'in'
        else:
            text = 'out'
    else:
        text = 'invalid pin'

    return HttpResponse(text)

""" Actual checking-in/out """
def UserCheckInOutView(request):
    user_set = HiveUser.objects.filter(user__username=request.POST['pin'])
    if user_set:
        user = user_set[0]
        if user.is_checked_in():
            # We check out
            check = Check(user=user, check_type='ou')
            check.save()

        else:
            # We check in
            check = Check(user=user, check_type='in')
            if 'use_daypass' in request.POST:
                check.using_daypass = True
            check.save()

        extra_context = {'user': user, 'check': check}

        return render_to_response('beelogger/user-checked-in-out.html', extra_context)