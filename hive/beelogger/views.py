from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import redirect, render
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
    user_set = HiveUser.objects.filter(user__username=request.POST['pin'])
    if user_set:
        extra_context = {
            'user': user_set[0]
        }
        return render(request, 'beelogger/user-check-state.html', extra_context)
    else:
        return HttpResponse('<div class="alert alert-error">Invalid PIN</div>')

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

        return render(request, 'beelogger/user-checked-in-out.html', extra_context)

def UsersCurrentlyCheckedIn(request):
    response = HttpResponse(mimetype = 'text/plain') # use application/json or something later

    today = date.today()

    checkins = Check.objects.filter(datetime__gte = today) \
        .filter(check_type = 'in').count()

    checkouts = Check.objects.filter(datetime__gte = today) \
        .filter(check_type = 'ou').count()

    response.write(str(checkins - checkouts))

    return response

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
        # basically in this format the users' check ins and outs are going to be interleaved
        # so we'd have to search for the user's check-in/out rather than being able to assume
        # it's in the next row over. not sure if that's worth it. might give up
        # on having users interleaved in order and just have all their activity for a
        # month/day together, followed by next user. see if we can better clarify what
        # sorts of dumps would be most useful
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
    writer.writerow(['user','last_reload','over_limit', \
        'in_time','out_time','visit_time','total_time', \
        'credit_change','ccs_before','cc_unit_type'])

    return response,writer

def ProcessChecks(checks):
        if len(checks) < 2:
            return []

        if checks[0].datetime > checks[2].datetime:
            checks.reverse()

        result = []
        total_time = timedelta()

        first_check = checks[len(checks)-1].datetime
        totalling_before_date = date(first_check.year, first_check.month, 1)

        user_last_reload = dict()

        i = 0
        while i < len(checks):
            if (checks[i].check_type == 'ou'):
                # only look at 'in' checkins. 'out' records will then be the next ones

                in_time = checks[i+1].datetime
                out_time = checks[i].datetime
                visit_time = out_time - in_time
                total_time += visit_time

                current_user = checks[i].user

                credit_changes = checks[i].credit_set.all()
                cc_units = 0
                ccs_before = 0
                cc_unit_type = ''
                if (len(credit_changes) > 0):
                    cc = credit_changes[0] # the credit change for this visit
                    cc_units = cc.units
                    cc_unit_type = cc.unit_type
                    ccs_before = Credit.objects \
                        .filter(user = current_user) \
                        .filter(datetime__lte = cc.datetime) \
                        .filter(datetime__gte = totalling_before_date) \
                        .filter(unit_type = cc.unit_type) \
                        .aggregate(sum = Sum('units'))['sum']

                if (current_user in user_last_reload) == False:
                    # get the most recent positive credit for the given user
                    user_last_reload[checks[i].user] = Credit.objects.filter(user = current_user) \
                        .filter(units__gt = 0) \
                        .filter(unit_type = cc_unit_type) \
                        .order_by('-datetime')[:1]

                current_reload = None
                if (current_user in user_last_reload) and (len(user_last_reload[current_user]) > 0):
                    current_reload = user_last_reload[current_user][0].format_unit()
                over_limit = (ccs_before <= 0)

                result.append([checks[i].user, current_reload, over_limit, \
                    in_time, out_time, visit_time, total_time, \
                    cc_units,ccs_before,cc_unit_type])

            i += 1

        return result
