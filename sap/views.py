from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Ally
from django.views import generic
from django.views.generic import TemplateView
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

from django.contrib import messages

# Create your views here.

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

class CreateAdminView(TemplateView):
    template_name = "sap/create_iba_admin.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        newAdminDict = dict(request.POST)
        valid = True
        for key in newAdminDict:
            if newAdminDict[key][0] == '':
                valid = False
        if valid:
            #Check if username credentials are correct
            if authenticate(request, username=newAdminDict['current_username'][0],
                            password=newAdminDict['current_password'][0]) is not None:
                #if are check username exists in database
                if User.objects.filter(username=newAdminDict['new_username'][0]).exists():
                    messages.add_message(request, messages.ERROR, 'Account was not created because username exists')
                    return redirect('/create_iba_admin')
                #Check if repeated password is same
                elif newAdminDict['new_password'][0] != newAdminDict['repeat_password'][0]:
                    messages.add_message(request, messages.ERROR, 'New password was not the same as repeated password')
                    return redirect('/create_iba_admin')
                else:
                    messages.add_message(request, messages.SUCCESS, 'Account Created')
                    User.objects.create_user(newAdminDict['new_username'][0],
                                             newAdminDict['new_email'][0], newAdminDict['new_password'][0])
                    return redirect('/dashboard')
            else:
                messages.add_message(request, messages.ERROR, 'Invalid Credentials entered')
                return redirect('/create_iba_admin')
        else:
            messages.add_message(request, messages.ERROR, 'Account was not created because one or more fields were not entered')
            return redirect('/create_iba_admin')

class ForgotPasswordView(TemplateView):
    template_name= "sap/forgot-password.html"