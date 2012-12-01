from django.contrib import admin
from beelogger.models import Credit, Check

class CreditAdmin(admin.ModelAdmin):
    list_display = ('user', 'format_unit', 'datetime')
    list_filter = ['user', 'datetime', 'unit_type']
    readonly_fields = ['datetime']

class CheckAdmin(admin.ModelAdmin):
    list_display = ('user', 'format_check', 'datetime')
    list_filter = ['user', 'datetime', 'check_type']
    readonly_fields = ['datetime']

admin.site.register(Credit, CreditAdmin)
admin.site.register(Check, CheckAdmin)