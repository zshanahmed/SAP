from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
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


class AccessMixin(LoginRequiredMixin):
    """
    Redirects users based on whether they are staff or not
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AlliesListView(AccessMixin, generic.ListView):
    template_name = 'sap/dashboard.html'
    context_object_name = 'allies_list'

    def get_queryset(self):
        return Ally.objects.order_by('-id')


class AnalyticsView(AccessMixin, TemplateView):
    template_name = "sap/analytics.html"


class AdminProfileView(TemplateView):
    template_name = "sap/profile.html"


class AboutPageView(TemplateView):
    template_name = "sap/about.html"


class SupportPageView(TemplateView):
    template_name = "sap/support.html"


class ForgotPasswordView(TemplateView):
    template_name= "sap/forgot-password.html"