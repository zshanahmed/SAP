from .models import Ally
from django.views import generic
from django.views.generic import TemplateView
from django.views.generic import FormView
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect


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

class CreateAdminView(TemplateView):
    template_name = "sap/create_iba_admin.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        print(request.POST)
        messages.add_message(request, messages.SUCCESS, 'Account Created')
        return redirect('/dashboard')