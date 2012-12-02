from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
import datetime as dt

""" HiveUser/Bee """
class HiveUser(models.Model):
    user = models.OneToOneField(User)

    def __unicode__(self):
        return '%s' % self.user

    def get_credit_hours(self):
        q = self.credit_set.filter(unit_type='H').aggregate(total=Sum('units'))
        return q['total']

    def get_credit_days(self):
        q = self.credit_set.filter(unit_type='D').aggregate(total=Sum('units'))
        return q['total']

    def get_unlimited_expiry_date(self):
        UNLIMITED_TIME = dt.timedelta(weeks=4) # 1 month
        unlimited_credit = self.credit_set.filter(unit_type='U')[:1]
        if unlimited_credit:
            return (unlimited_credit[0].datetime + UNLIMITED_TIME)
        else:
            return False

    def is_unlimited(self):
        today = dt.datetime.now()
        expiry_date = self.get_unlimited_expiry_date()
        if expiry_date:
            return today < expiry_date
        else:
            return False

    def is_checked_in(self):
        last_check = self.check_set.all()[:1]
        if last_check:
            if last_check[0].check_type == 'in':
                return True
            else:
                return False
        else:
            return False

""" Check-in/check-out """
class Check(models.Model):
    CHECK_TYPE_CHOICES = (
        ('in', 'Check-in'),
        ('ou', 'Check-out'),
    )
    user = models.ForeignKey(HiveUser)
    datetime = models.DateTimeField(auto_now_add=True)
    check_type = models.CharField(max_length=2, choices=CHECK_TYPE_CHOICES, default='in')
    using_daypass = models.BooleanField()

    class Meta:
        ordering = ['-datetime']

    def format_check(self):
        return self.get_check_type_display()
    format_check.short_description = 'Check type'

    def __unicode__(self):
        return '%s - %s' % (self.user, self.datetime)

    def save(self, *args, **kwargs):
        # We might need to record time spent by the user
        if self.check_type == 'ou':
            if not self.user.is_unlimited():
                check_in = self.user.check_set.filter(check_type='in')[0]
                if check_in.using_daypass:
                    credit = Credit(user=self.user, units=-1, unit_type='D', check=self)
                else:
                    timedelta = dt.datetime.now() - check_in.datetime
                    hours = timedelta.total_seconds()/3600.0*-1
                    credit = Credit(user=self.user, units=hours, unit_type='H', check=self)
                credit.save()

        super(Check, self).save(*args, **kwargs)

""" Credit """
class Credit(models.Model):
    UNIT_TYPE_CHOICES = (
        ('H', 'Hours'),
        ('D', 'Days'),
        ('U', 'Unlimited'),
    )
    user = models.ForeignKey(HiveUser)
    units = models.FloatField()
    datetime = models.DateTimeField(auto_now_add=True)
    unit_type = models.CharField(max_length=1, choices=UNIT_TYPE_CHOICES, default='H')
    check = models.ForeignKey(Check, blank=True, null=True)

    class Meta:
        ordering = ['-datetime']

    def format_unit(self):
        return '%F %s' % (self.units, self.get_unit_type_display().lower())
    format_unit.short_description = 'Credit/Debit'

    def __unicode__(self):
        return '%s | %s' % (self.user, self.format_unit())