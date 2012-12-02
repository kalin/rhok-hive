from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from beelogger.models import HiveUser, Check, Credit
import csv
from datetime import datetime, timedelta
from django.db.models.aggregates import Sum

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

def CSVDumpView(request):
    # proper csv headers commented out for commenting
    #response = HttpResponse(mimetype='text/csv')
    #response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    response = HttpResponse(mimetype='text/plain')

    writer = csv.writer(response)
    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])

    for user in HiveUser.objects.all():
        writer.writerow(['test',str(user)])

        month_time = dict()
        month_hours = dict()
        total_time = timedelta()

        checks = user.check_set.all().reverse()

        i = 0
        while i < len(checks):
            if (checks[i].check_type == 'in'):
                # only look at 'in' checkins. 'out' records will then be the next ones

                in_time = checks[i].datetime
                out_time = checks[i+1].datetime
                visit_time = out_time - in_time
                total_time += visit_time

                """keystring = str(in_time.year) + '-' + str(in_time.month)
                if (keystring in month_time == False):
                    month_time[keystring] = datetime.timedelta()
                month_time[keystring] += visit_time"""

                totalling_before_date = datetime.fromtimestamp(0)
                totalling_before_date = datetime(2012,12,1)

                credit_changes = checks[i+1].credit_set.all()
                if (len(credit_changes) > 0):
                    cc = credit_changes[0] # the credit change for this visit
                    ccs_before = Credit.objects.all() \
                        .filter(datetime__lte = cc.datetime) \
                        .filter(datetime__gte = totalling_before_date) \
                        .filter(unit_type = cc.unit_type) \
                        .aggregate(sum = Sum('units'))['sum']
                    if ccs_before == None:
                        ccs_before = 0
                
                writer.writerow([in_time,out_time,visit_time,month_time,total_time, \
                    cc.units,ccs_before])

            i += 1

    return response

