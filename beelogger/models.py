from django.db import models
from django.contrib.auth.models import User

""" Credit """
class Credit(models.Model):
    UNIT_TYPE_CHOICES = (
        ('H', 'Hours'),
        ('D', 'Days'),
        ('U', 'Unlimited'),
    )
    user = models.ForeignKey(User)
    units = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True)
    unit_type = models.CharField(max_length=1, choices=UNIT_TYPE_CHOICES, default='H')

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
    user = models.ForeignKey(User)
    datetime = models.DateTimeField(auto_now_add=True)
    check_type = models.CharField(max_length=2, choices=CHECK_TYPE_CHOICES, default='in')

    def format_check(self):
        return self.get_check_type_display()
    format_check.short_description = 'Check type'

    def __unicode__(self):
        return '%s - %s' % (self.user, self.datetime)