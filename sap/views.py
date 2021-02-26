from django.contrib.auth import logout
from .models import Ally
from django.views import generic
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User


# Create your views here.

def logout_request(request):
    logout(request)
    return redirect('sap:home')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'Password Updated Successfully !')
            return redirect('sap:change_password')
        else:
            messages.error(request, "Couldn't Update Password !")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'sap/change_password.html', {
        'form': form
    })


def edit_admin_profile(request):
    if request.method == 'POST':
        curr_user = request.user
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')
        if not User.objects.filter(username=new_username).exists():
            curr_user.username = new_username
            curr_user.email = new_email
            curr_user.save()
            messages.success(request, "Profile Updated !")
            return redirect('sap:sap-admin_profile')
        else:
            messages.error(request, "Couldn't Update Profile ! Username already exists")
    
    return render(request, 'sap/profile.html')

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
