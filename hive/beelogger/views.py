from django.views.generic import TemplateView
from beelogger.models import HiveUser
import datetime

class TestView(TemplateView):
    template_name = 'test.html'

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)

        context['hiveuser'] = HiveUser.objects.all()

        context['today'] = datetime.datetime.now()

        return context