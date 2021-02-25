from .models import Ally
from django.views import generic
from django.views.generic import TemplateView
from django.contrib import messages

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
    
class ForgotPasswordView(TemplateView):
    template_name= "sap/forgot-password.html"