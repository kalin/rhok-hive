from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from beelogger.models import HiveUser, Check, Credit
import csv
from datetime import datetime, date, timedelta
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
    response,writer = PrepareCSVResponseObject()

    for user in HiveUser.objects.all():
        results = ProcessChecks(user.check_set.all())

        for result in results:
            writer.writerow(result)

    return response

def CSVDumpUser(request):
    response,writer = PrepareCSVResponseObject()

    checks = Check.objects.filter(user__user = request.GET['pin'])

    for result in ProcessChecks(checks):
        writer.writerow(result)

    return response

def CSVDumpCurrentMonth(request):
    response,writer = PrepareCSVResponseObject()

    today = date.today()

    if 'pin' in request.GET:
        checks = GetOneMonthsData(today.year, today.month, request.GET['pin'])
    else:
        #checks = []
        #for user in HiveUser.objects.all():
        #    checks.extend(GetOneMonthsData(today.year, today.month, user.user))
        #TODO! this returns incorrect data, datetimes are in wrong places
        checks = GetOneMonthsData(today.year, today.month)

    for result in ProcessChecks(checks):
        writer.writerow(result)

    return response

def GetOneMonthsData(year, month, specificUser = False):
    beginMonthDate = datetime(year,month,1)

    if month < 12:
        endYear = year
        endMonth = month + 1
    else:
        endYear = year + 1
        endMonth = 1
    
    endMonthDate = datetime(endYear,endMonth,1) - timedelta(seconds = 1) # one second before midnight

    if specificUser:
        checks = Check.objects.filter(user__user = specificUser) \
            .filter(datetime__gte = beginMonthDate) \
            .filter(datetime__lte = endMonthDate)
    else:
        checks = Check.objects.filter(datetime__gte = beginMonthDate) \
            .filter(datetime__lte = endMonthDate)
    
    return checks

def PrepareCSVResponseObject():
    # proper csv headers commented out for commenting
    #response = HttpResponse(mimetype='text/csv')
    #response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    response = HttpResponse(mimetype='text/plain')

    writer = csv.writer(response)
    writer.writerow(['user','in_time','out_time','visit_time','total_time', \
        'credit_change','ccs_before','cc_unit_type'])

    return response,writer

def ProcessChecks(checks):
        if len(checks) < 2:
            return []

        if checks[0].datetime > checks[2].datetime:
            checks.reverse()

        result = []
        total_time = timedelta()
        totalling_before_date = checks[len(checks)-1].datetime

        i = 0
        while i < len(checks):
            if (checks[i].check_type == 'ou'):
                # only look at 'in' checkins. 'out' records will then be the next ones

                in_time = checks[i+1].datetime
                out_time = checks[i].datetime
                visit_time = out_time - in_time
                total_time += visit_time

                credit_changes = checks[i].credit_set.all()
                cc_units = 0
                ccs_before = 0
                cc_unit_type = ''
                if (len(credit_changes) > 0):
                    cc = credit_changes[0] # the credit change for this visit
                    cc_units = cc.units
                    cc_unit_type = cc.unit_type
                    ccs_before = Credit.objects.all() \
                        .filter(user = checks[i].user) \
                        .filter(datetime__lte = cc.datetime) \
                        .filter(datetime__gte = totalling_before_date) \
                        .filter(unit_type = cc.unit_type) \
                        .aggregate(sum = Sum('units'))['sum']
                
                result.append([checks[i].user,in_time,out_time,visit_time,total_time, \
                    cc_units,ccs_before,cc_unit_type])

            i += 1

        return result

