from django.db import models
from django.contrib.auth.models import User
import datetime as dt

""" HiveUser/Bee """
class HiveUser(models.Model):
    user = models.OneToOneField(User)

    def __unicode__(self):
        return '%s' % self.user

    def get_credit_hours(self):
        return self.credit_set.filter(unit_type='U')

    def get_credit_days(self):
        return self.credit_set.filter(unit_type='D')

    def get_unlimited_expiry_date(self):
        UNLIMITED_TIME = dt.timedelta(weeks=4) # 1 month
        unlimited_credit = self.credit_set.filter(unit_type='U')[:1]
        if unlimited_credit:
            return (unlimited_credit[0].datetime + UNLIMITED_TIME)
        else:
            return False

    def is_unlimited(self):
        today = dt.datetime.now()
        return (today - self.get_unlimited_expiry_date())

    def is_checked_in(self):
        last_check = self.check_set.all()[:1]
        if last_check:
            if last_check[0].check_type == 'in':
                return True
            else:
                return False
        else:
            return False

""" Credit """
class Credit(models.Model):
    UNIT_TYPE_CHOICES = (
        ('H', 'Hours'),
        ('D', 'Days'),
        ('U', 'Unlimited'),
    )
    user = models.ForeignKey(HiveUser)
    units = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True)
    unit_type = models.CharField(max_length=1, choices=UNIT_TYPE_CHOICES, default='H')

    class Meta:
        ordering = ['-datetime']

    def format_unit(self):
        return '%d %s' % (self.units, self.get_unit_type_display().lower())
    format_unit.short_description = 'Credit/Debit'

    def __unicode__(self):
        return '%s | %s' % (self.user, self.format_unit())

""" Check-in/check-out """
class Check(models.Model):
    CHECK_TYPE_CHOICES = (
        ('in', 'Check-in'),
        ('ou', 'Check-out'),
    )
    user = models.ForeignKey(HiveUser)
    datetime = models.DateTimeField(auto_now_add=True)
    check_type = models.CharField(max_length=2, choices=CHECK_TYPE_CHOICES, default='in')

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
            check_out_datetime = dt.datetime.now()
            check_in_datetime = self.user.check_set.filter(check_type='in')[0].datetime
            timedelta = check_out_datetime - check_in_datetime

        super(Check, self).save(*args, **kwargs)