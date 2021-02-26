from django.contrib.auth import logout
from django.shortcuts import redirect
from .models import Ally
from django.views import generic
from django.views.generic import TemplateView
from django.contrib import messages

# Create your views here.


def login_success(request):
    """
    Redirects users based on whether they are staff or not
    """

    if request.user.is_authenticated:
        # login(request, user)
        if request.user.is_staff:
        # sales users landing page
            return redirect('sap:sap-dashboard')
        else:
            return redirect('sap:sap-admin_profile')


def logout_request(request):
    logout(request)
    return redirect('sap:home')


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


class ForgotPasswordView(TemplateView):
    template_name= "sap/forgot-password.html"