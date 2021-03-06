from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Ally, StudentCategories, AllyStudentCategoryRelation
from django.views import generic
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import UpdateAdminProfileForm


# Create your views here.


def login_success(request):
    """
    Redirects users based on whether they are staff or not
    """

    if request.user.is_authenticated:
        if request.user.is_staff:
        # users landing page
            return redirect('sap:sap-dashboard')
        else:
            return redirect('sap:sap-admin_profile')


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
        form = UpdateAdminProfileForm(request.POST)

        new_username = form.data['username']
        new_email = form.data['email']
        if not User.objects.filter(username=new_username).exists():
            curr_user.username = new_username
            curr_user.email = new_email
            curr_user.save()
            messages.success(request, "Profile Updated !")
            return redirect('sap:sap-admin_profile')
        else:
            messages.error(request, "Couldn't Update Profile ! Username already exists")
    else:
        form = UpdateAdminProfileForm()
    return render(request, 'sap/profile.html', {
        'form': form
    })


class AccessMixin(LoginRequiredMixin):
    """
    Redirect users based on whether they are staff or not
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



class CreateAdminView(AccessMixin, TemplateView):
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
                    user = User.objects.create_user(newAdminDict['new_username'][0],
                                             newAdminDict['new_email'][0], newAdminDict['new_password'][0])
                    user.is_staff = True
                    user.save()
                    return redirect('/dashboard')
            else:
                messages.add_message(request, messages.ERROR, 'Invalid Credentials entered')
                return redirect('/create_iba_admin')
        else:
            messages.add_message(request, messages.ERROR, 'Account was not created because one or more fields were not entered')
            return redirect('/create_iba_admin')

class SignUpView(TemplateView):
    template_name = "sap/sign-up.html"

    def make_categories(self, studentCategories):
        categories = StudentCategories.objects.create()
        for id in studentCategories:
            if id == 'First generation college-student':
                categories.first_gen_college_student = True
            elif id == 'Low-income':
                categories.low_income = True
            elif id == 'Underrepresented racial/ethnic minority':
                categories.under_represented_racial_ethnic = True
            elif id == 'LGBTQ':
                categories.lgbtq = True
            elif id == 'Rural':
                categories.rural = True
        categories.save()
        return categories

    def set_boolean(self, list, postDict):
        dict = {}
        for selection in list:
            if postDict[selection] == 'Yes':
                dict[selection] = True
            else:
                dict[selection] = False
        return dict

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        postDict = dict(request.POST)
        print(request.POST)
        if User.objects.filter(username=postDict["new_username"][0]).exists():
            messages.add_message(request, messages.WARNING,
                                 'Account can not be created because username already exists')
            return redirect('sign-up/')
        elif User.objects.filter(email=postDict["new_email"][0]).exists():
            messages.add_message(request, messages.WARNING,
                                 'Account can not be created because email already exists')
            return redirect('sign-up/')
        elif postDict["new_password"][0] != postDict["repeat_password"][0]:
            return redirect('sign-up/')
        else:
            user = User.objects.create_user(username=postDict["new_username"][0],
                                            password=postDict["new_password"][0],
                                            email=postDict["new_email"][0],
                                            first_name=postDict["firstName"][0], last_name=postDict["lastName"][0])
            if postDict['roleSelected'][0] == 'Undergraduate Student':
                categories = self.make_categories(postDict["idUnderGradCheckboxes"])
                undergradList = ['interestRadios', 'experienceRadios', 'interestedRadios', 'agreementRadios']
                selections = self.set_boolean(undergradList, postDict)
                ally = Ally.objects.create(user=user, user_type=postDict['roleSelected'][0],
                                           major=postDict['major'][0], year=postDict['undergradRadios'][0],
                                           interested_in_joining_lab=selections['interestRadios'],
                                           has_lab_experience=selections['experienceRadios'],
                                           interested_in_mentoring=selections['interestedRadios'],
                                           information_release=selections['agreementRadios'])
                AllyStudentCategoryRelation.objects.create(student_category_id=categories.id, ally_id=ally.id)
                messages.add_message(request, messages.WARNING, "Account created")
                return redirect("sap:home")
            elif postDict['roleSelected'][0] == 'Graduate Student':
                pass
            elif postDict['roleSelected'][0] == 'Faculty':
                pass
            elif postDict['roleSelected'][0] == 'Staff':
                pass

        return redirect("sap:home")

class ForgotPasswordView(TemplateView):
    template_name= "sap/forgot-password.html"