from .models import Ally
from django.views import generic
from django.views.generic import TemplateView


# Create your views here.


class AlliesListView(generic.ListView):
    template_name = 'sap/dashboard.html'
    context_object_name = 'allies_list'

    def get_queryset(self):
        return Ally.objects.order_by('-id')

class AnalyticsView(TemplateView):
    template_name = "sap/analytics.html"

class AdminProfileView(TemplateView):
    template_name = "sap/profile.html"

class AboutPageView(TemplateView):
    template_name = "sap/about.html"

class SupportPageView(TemplateView):
    template_name = "sap/support.html"

