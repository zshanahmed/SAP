import io
import os
import os.path
import csv
import uuid
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import xlsxwriter
from .models import Ally, StudentCategories, AllyStudentCategoryRelation
from django.views import generic
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import UpdateAdminProfileForm, UserPasswordForgotForm, UserResetForgotPasswordForm
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import password_reset_token, account_activation_token
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import date

import pandas as pd
import numpy as np

from .forms import UpdateAdminProfileForm
from django.http import HttpResponseNotFound


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
            return redirect('sap:sap-about')
    else:
        messages.error(request, 'Username or password is incorrect!')


def logout_request(request):
    logout(request)
    return redirect('sap:home')


class AccessMixin(LoginRequiredMixin):
    """
    Redirect users based on whether they are staff or not
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class ViewAllyProfileFromAdminDashboard(AccessMixin, View):
    def get(self, request, *args, **kwargs):
        username = request.GET['username']
        try:
            user = User.objects.get(username=username)
            ally = Ally.objects.get(user=user)
            return render(request, 'sap/admin_ally_table/view_ally.html', {
                'ally': ally
            })
        except:
            return HttpResponseNotFound()


class EditAllyProfileFromAdminDashboard(AccessMixin, View):
    def set_boolean(self, list, postDict):
        dict = {}
        for selection in list:
            if postDict[selection][0] == 'Yes':
                dict[selection] = True
            else:
                dict[selection] = False
        return dict
    def get(self, request, *args, **kwargs):
        username = request.GET['username']
        try:
            user = User.objects.get(username=username)
            ally = Ally.objects.get(user=user)
            return render(request, 'sap/admin_ally_table/edit_ally.html', {
                'ally': ally
            })
        except Exception as e:
            print(e)
            return HttpResponseNotFound()

    def post(self, request):
        postDict = dict(request.POST)
        print(request.POST)
        if User.objects.filter(username=postDict["username"][0]).exists():
            user = User.objects.get(username=postDict["username"][0])
            ally = Ally.objects.get(user=user)
            if ally.user_type == 'Staff':
                selections = self.set_boolean(
                    ['studentsInterestedRadios'], postDict)

                how_can_we_help = postDict["howCanWeHelp"][0]

                ally.people_who_might_be_interested_in_iba = selections['studentsInterestedRadios']
                ally.how_can_science_ally_serve_you = how_can_we_help

                ally.save()
            elif ally.user_type == 'Graduate Student':
                selections = self.set_boolean(
                    ['mentoringGradRadios', 'labShadowRadios', 'connectingRadios', 'volunteerGradRadios', 'gradTrainingRadios'], postDict)
                stem_fields = ','.join(postDict['stemGradCheckboxes'])

                ally.area_of_research = stem_fields
                ally.interested_in_mentoring = selections['mentoringGradRadios']
                ally.willing_to_offer_lab_shadowing = selections['labShadowRadios']
                ally.interested_in_connecting_with_other_mentors = selections['connectingRadios']
                ally.willing_to_volunteer_for_events = selections['volunteerGradRadios']
                ally.interested_in_mentor_training = selections['gradTrainingRadios']

                ally.save()
            elif ally.user_type == 'Undergraduate Student':
                selections = self.set_boolean(
                    ['interestRadios', 'experienceRadios', 'interestedRadios', 'agreementRadios'], postDict)

                ally.year = postDict['undergradRadios'][0]
                ally.major = postDict['major'][0]
                ally.interested_in_joining_lab = selections['interestRadios']
                ally.has_lab_experience=selections['experienceRadios']
                ally.interested_in_mentoring=selections['interestedRadios']
                ally.information_release = selections['agreementRadios']

                ally.save()
            elif ally.user_type == 'Faculty':
                selections = self.set_boolean(
                    ['openingRadios', 'mentoringFacultyRadios', 'volunteerRadios', 'trainingRadios'], postDict)
                stem_fields = ','.join(postDict['stemGradCheckboxes'])

                ally.area_of_research = stem_fields
                ally.description_of_research_done_at_lab = postDict['research-des'][0]
                ally.openings_in_lab_serving_at=selections['openingRadios']
                ally.interested_in_mentoring = selections['mentoringFacultyRadios']
                ally.willing_to_volunteer_for_events = selections['volunteerRadios']
                ally.interested_in_mentor_training = selections['trainingRadios']

                ally.save()

            messages.add_message(request, messages.WARNING,
                                 'Ally updated !')
        else:
            messages.add_message(request, messages.WARNING,
                                 'Ally does not exist !')
        return redirect('sap:sap-dashboard')


class DeleteAllyProfileFromAdminDashboard(AccessMixin, View):
    def get(self, request, *args, **kwargs):
        username = request.GET['username']
        try:
            user = User.objects.get(username=username)
            ally = Ally.objects.get(user=user)
            ally.delete()
            user.delete()
            messages.success(request, 'Successfully deleted the user '+username)
            return redirect('sap:sap-dashboard')
        except Exception as e:
            print(e)
            return HttpResponseNotFound("")


class ChangeAdminPassword(AccessMixin, View):
    """
    Change the password for admin
    """
    def get(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.user)
        return render(request, 'sap/change_password.html', {
            'form': form
        })

    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'Password Updated Successfully !')
            return redirect('sap:change_password')
        else:
            messages.error(request, "Could not Update Password !")

        return render(request, 'sap/change_password.html', {
            'form': form
        })


class EditAdminProfile(AccessMixin, View):
    """
    Change the profile for admin
    """
    def get(self, request, *args, **kwargs):
        form = UpdateAdminProfileForm()
        return render(request, 'sap/profile.html', {
            'form': form
        })

    def post(self, request, *args, **kwargs):
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
            messages.error(
                request, "Could not Update Profile ! Username already exists")
        return render(request, 'sap/profile.html', {
            'form': form
        })


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
            # Check if username credentials are correct
            if authenticate(request, username=newAdminDict['current_username'][0],
                            password=newAdminDict['current_password'][0]) is not None:
                # if are check username exists in database
                if User.objects.filter(username=newAdminDict['new_username'][0]).exists():
                    messages.add_message(request, messages.ERROR, 'Account was not created because username exists')
                    return redirect('/create_iba_admin')
                # Check if repeated password is same
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
            messages.add_message(request, messages.ERROR,
                                 'Account was not created because one or more fields were not entered')
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
            if postDict[selection][0] == 'Yes':
                dict[selection] = True
            else:
                dict[selection] = False
        return dict

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        postDict = dict(request.POST)

        min_length = 8  # Minimum length for a valid password

        print(request.POST)
        if User.objects.filter(username=postDict["new_username"][0]).exists():
            messages.add_message(request, messages.WARNING,
                                 'Account can not be created because username already exists')
            return redirect('/sign-up')
        elif User.objects.filter(email=postDict["new_email"][0]).exists():
            messages.add_message(request, messages.WARNING,
                                 'Account can not be created because email already exists')
            return redirect('/sign-up')
        elif postDict["new_password"][0] != postDict["repeat_password"][0]:
            messages.add_message(
                request,
                messages.WARNING,
                "Repeated password is not the same as the inputted password",
            )
            return redirect("/sign-up")
        elif len(postDict["new_password"][0]) < min_length:
            messages.warning(
                request,
                "Password must be at least {0} characters long".format(min_length),
            )
            return redirect("/sign-up")
        else:
            user = User.objects.create_user(username=postDict["new_username"][0],
                                            password=postDict["new_password"][0],
                                            email=postDict["new_email"][0],
                                            first_name=postDict["firstName"][0], last_name=postDict["lastName"][0])

            if postDict['roleSelected'][0] == 'Staff':
                selections = self.set_boolean(['studentsInterestedRadios'], postDict)
                ally = Ally.objects.create(user=user, user_type=postDict['roleSelected'][0], hawk_id=user.username,
                                           people_who_might_be_interested_in_iba=selections['studentsInterestedRadios'],
                                           how_can_science_ally_serve_you=postDict['howCanWeHelp'])
            else:
                if postDict['roleSelected'][0] == 'Undergraduate Student':
                    try:
                        categories = self.make_categories(postDict["idUnderGradCheckboxes"])
                    except KeyError:
                        categories = StudentCategories.objects.create()
                    undergradList = ['interestRadios', 'experienceRadios', 'interestedRadios', 'agreementRadios']
                    selections = self.set_boolean(undergradList, postDict)
                    ally = Ally.objects.create(user=user, user_type=postDict['roleSelected'][0], hawk_id=user.username,
                                               major=postDict['major'][0], year=postDict['undergradRadios'][0],
                                               interested_in_joining_lab=selections['interestRadios'],
                                               has_lab_experience=selections['experienceRadios'],
                                               interested_in_mentoring=selections['interestedRadios'],
                                               information_release=selections['agreementRadios'])
                elif postDict['roleSelected'][0] == 'Graduate Student':
                    try:
                        stem_fields = ','.join(postDict['stemGradCheckboxes'])
                    except KeyError:
                        stem_fields = None
                    try:
                        categories = self.make_categories(postDict['mentoringGradCheckboxes'])
                    except KeyError:
                        categories = StudentCategories.objects.create()

                    gradList = ['mentoringGradRadios', 'labShadowRadios', 'connectingRadios', 'volunteerGradRadios',
                                'gradTrainingRadios']
                    selections = self.set_boolean(gradList, postDict)
                    ally = Ally.objects.create(user=user, user_type=postDict['roleSelected'][0], hawk_id=user.username,
                                               area_of_research=stem_fields,
                                               interested_in_mentoring=selections['mentoringGradRadios'],
                                               willing_to_offer_lab_shadowing=selections['labShadowRadios'],
                                               interested_in_connecting_with_other_mentors=selections[
                                                   'connectingRadios'],
                                               willing_to_volunteer_for_events=selections['volunteerGradRadios'],
                                               interested_in_mentor_training=selections['gradTrainingRadios'])

                elif postDict['roleSelected'][0] == 'Faculty':
                    try:
                        stem_fields = ','.join(postDict['stemCheckboxes'])
                    except KeyError:
                        stem_fields = None
                    facultyList = ['openingRadios', 'volunteerRadios', 'trainingRadios', 'mentoringFacultyRadios']
                    selections = self.set_boolean(facultyList, postDict)
                    try:
                        categories = self.make_categories(postDict['mentoringCheckboxes'])
                    except KeyError:
                        categories = StudentCategories.objects.create()
                    ally = Ally.objects.create(user=user, user_type=postDict['roleSelected'][0], hawk_id=user.username,
                                               area_of_research=stem_fields,
                                               openings_in_lab_serving_at=selections['openingRadios'],
                                               description_of_research_done_at_lab=postDict['research-des'][0],
                                               interested_in_mentoring=selections['mentoringFacultyRadios'],
                                               willing_to_volunteer_for_events=selections['volunteerRadios'],
                                               interested_in_mentor_training=selections['trainingRadios'])

                AllyStudentCategoryRelation.objects.create(student_category_id=categories.id, ally_id=ally.id)

            messages.success(request, "Account created")
            return redirect("sap:home")

        return redirect("sap:home")


class ForgotPasswordView(TemplateView):
    """
    A view which allows users to reset their password in case they forget it.
    Send a confirmation emails with unique token
    """

    # template_name = "sap/password-forgot.html"

    def get(self, request, *args, **kwargs):
        form = PasswordResetForm(request.GET)
        return render(request, 'sap/password-forgot.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            entered_email = request.POST.get('email')
            valid_email = User.objects.filter(email=entered_email)
            site = get_current_site(request)

            if len(valid_email) > 0:
                user = valid_email[0]
                user.is_active = False  # User needs to be inactive for the reset password duration
                # user.profile.reset_password = True
                user.save()

                message_body = render_to_string('sap/password-forgot-mail.html', {
                    'user': user,
                    'protocol': 'http',
                    'domain': site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),  # encode user's primary key
                    'token': password_reset_token.make_token(user),
                })

                # message_ = reverse('sap:password-forgot-confirm',
                #                    args=[urlsafe_base64_encode(force_bytes(user.pk)),
                #                          password_reset_token.make_token(user)])
                #
                # message_body = 'http:' + '//' + site.domain + message_

                email_content = Mail(
                    from_email='team1sep@hotmail.com',
                    to_emails=entered_email,
                    subject='Reset Password for Science Alliance Portal',
                    html_content=message_body)

                try:
                    #                     sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                    # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                    # TODO: Change API key and invalidate the old one
                    sg = SendGridAPIClient('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')
                    response = sg.send(email_content)
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                except Exception as e:
                    print(e.email_content)

                return redirect('/password-forgot-done')

            else:
                return redirect('/password-forgot-done')
                # return render(request, 'account/password-forgot.html', {'form': form})

        return render(request, 'sap/password-forgot.html', {'form': form})


class ForgotPasswordDoneView(TemplateView):
    """
    A view which is presented if the user entered valid email ing Forget Password view
    """
    template_name = "sap/password-forgot-done.html"


class ForgotPasswordCompleteView(TemplateView):
    """
    A view which
    """
    template_name = "sap/password-forgot-complete.html"


class ForgotPasswordMail(TemplateView):
    """
    Email template for Forgot Password Feature
    """
    template_name = "sap/password-forgot-mail.html"


class ForgotPasswordConfirmView(TemplateView):
    """
    A unique to users who click to the reset forgot passwork link.
    Allow them to create new password.
    """
    # template_name = "sap/password-forgot-confirm.html"
    def get(self, request, *args, **kwargs):
        path = request.path
        path_1, token = os.path.split(path)
        path_0, uidb64 = os.path.split(path_1)

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            messages.warning(request, str(e))
            user = None

        if user is not None and password_reset_token.check_token(user, token):
            context = {
                'form': UserResetForgotPasswordForm(user),
                'uid': uidb64,
                'token': token
            }
            return render(request, 'sap/password-forgot-confirm.html', context)
        else:
            messages.error(request, 'Password reset link is invalid. Please request a new password reset.')
            return redirect('sap:home')

    def post(self, request, *args, **kwargs):
        path = request.path
        path_1, token = os.path.split(path)
        path_0, uidb64 = os.path.split(path_1)

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            messages.warning(request, str(e))
            user = None

        if user is not None and password_reset_token.check_token(user, token):
            form = UserResetForgotPasswordForm(user=user, data=request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)

                user.is_active = True
                # user.profile.reset_password = False
                user.save()
                messages.success(request, 'New Password Created Successfully!')
                return redirect('sap:home')
            else:
                context = {
                    'form': UserResetForgotPasswordForm(user),
                    'uid': uidb64,
                    'token': token
                }
                messages.error(request, 'Password does not meet requirements.')
                return render(request, 'sap/password-forgot-confirm.html', context)
        else:
            messages.error(request, 'Password reset link is invalid. Please request a new password reset.')
            return redirect('sap:home')

userFields = ['last_login', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined']
allyFields = ['user_type', 'area_of_research', 'openings_in_lab_serving_at', 'description_of_research_done_at_lab',
              'interested_in_mentoring', 'interested_in_mentor_training', 'willing_to_offer_lab_shadowing',
              'interested_in_connecting_with_other_mentors', 'willing_to_volunteer_for_events', 'works_at',
              'people_who_might_be_interested_in_iba', 'how_can_science_ally_serve_you', 'year', 'major',
              'information_release', 'interested_in_being_mentored', 'interested_in_joining_lab',
              'has_lab_experience']
categoryFields = ['under_represented_racial_ethnic', 'first_gen_college_student', 'transfer_student', 'lgbtq',
                  'low_income', 'rural']

class DownloadAllies(AccessMixin, HttpResponse):

    @staticmethod
    def fields_helper(model, columns):
        for field in model._meta.get_fields():
            fields = str(field).split(".")[-1]
            if fields in userFields or fields in allyFields or fields in categoryFields:
                columns.append(fields)
        return columns

    @staticmethod
    def cleanup(dict):
        ar = []
        for item in dict.items():
            if item[0] in userFields or item[0] in allyFields or item[0] in categoryFields:
                if item[0] == 'date_joined':
                    ar.append(item[1].strftime("%b-%d-%Y"))
                else:
                    ar.append(item[1])
        return ar

    @staticmethod
    def get_data():
        users = User.objects.all()
        allies = Ally.objects.all()
        categories = StudentCategories.objects.all()
        categoryRelation = AllyStudentCategoryRelation.objects.all()

        data = []
        for ally in allies:
            userId = ally.user_id
            allyId = ally.id

            category = categoryRelation.filter(ally_id=allyId)
            if category.exists():
                categoryId = category[0].student_category_id
                tmp = DownloadAllies.cleanup(users.filter(id=userId)[0].__dict__) + DownloadAllies.cleanup(ally.__dict__) + \
                      DownloadAllies.cleanup(categories.filter(id=categoryId)[0].__dict__)
            else:
                tmp = DownloadAllies.cleanup(users.filter(id=userId)[0].__dict__) + DownloadAllies.cleanup(ally.__dict__) + \
                      [None, None, None, None, None, None]
            data.append(tmp)
        return data

    def allies_download(request):
        if request.user.is_staff:
            response = HttpResponse(content_type='text/csv')
            today = date.today()
            today = today.strftime("%b-%d-%Y")
            fileName = today + "_ScienceAllianceAllies.csv"
            response['Content-Disposition'] = 'attachment; filename=' + fileName
            columns = []
            columns = DownloadAllies.fields_helper(User, columns)
            columns = DownloadAllies.fields_helper(Ally, columns)
            columns = DownloadAllies.fields_helper(StudentCategories, columns)
            data = DownloadAllies.get_data()
            writer = csv.writer(response)
            writer.writerow(columns)
            writer.writerows(data)
            return response
        else:
            return HttpResponseForbidden()

class UploadAllies(AccessMixin, HttpResponse):

    @staticmethod
    def makeAlliesFromFile(df):
        columns = list(df.columns)
        errorLog = {}
        passwordLog = {}
        if columns == (userFields + allyFields + categoryFields):
            allyData = df[allyFields].to_dict('index')
            userData = df[userFields].to_dict('index')
            categoryData = df[categoryFields].to_dict('index')
            for ally in allyData.items():
                if ("Staff" == ally[1]['user_type'] or "Graduate Student" == ally[1]['user_type']
                        or "Undergraduate Student" == ally[1]['user_type'] or "Faculty" == ally[1]['user_type']):
                    password = uuid.uuid4().hex[0:9]
                    user = userData[ally[0]]
                    try:
                        user = User.objects.create_user(username=user['username'], password=password, email=user['email'],
                                                    first_name=user['first_name'], last_name=user['last_name'])
                        passwordLog[ally[0]] = password
                        try:
                            ally1 = Ally.objects.create(user=user, user_type=ally[1]['user_type'], hawk_id=user.username,
                                                       area_of_research=ally[1]['area_of_research'],
                                                       interested_in_mentoring=ally[1]['interested_in_mentoring'],
                                                       willing_to_offer_lab_shadowing=ally[1]['willing_to_offer_lab_shadowing'],
                                                    interested_in_connecting_with_other_mentors=ally[1]['interested_in_connecting_with_other_mentors'],
                                                       willing_to_volunteer_for_events=ally[1]['willing_to_volunteer_for_events'],
                                                       interested_in_mentor_training=ally[1]['interested_in_mentor_training'],
                                                       major=ally[1]['major'], information_release=ally[1]['information_release'],
                                                       has_lab_experience=ally[1]['has_lab_experience'],
                                                       year=ally[1]['year'], interested_in_being_mentored=ally[1]['interested_in_being_mentored'],
                                                       description_of_research_done_at_lab=ally[1]['description_of_research_done_at_lab'],
                                                       interested_in_joining_lab=ally[1]['interested_in_joining_lab'],
                                                       openings_in_lab_serving_at=ally[1]['openings_in_lab_serving_at'],
                                                       people_who_might_be_interested_in_iba=ally[1]['people_who_might_be_interested_in_iba'],
                                                       how_can_science_ally_serve_you=ally[1]['how_can_science_ally_serve_you'],
                                                       works_at=ally[1]['works_at'])
                            if not (ally[1]['user_type'] == "Staff"):
                                category = categoryData[ally[0]]
                                categories = StudentCategories.objects.create(rural=category['rural'],
                                                                              transfer_student=category['transfer_student'],
                                                                              lgbtq=category['lgbtq'],
                                                                              low_income=category['low_income'],
                                                                              first_gen_college_student=category['first_gen_college_student'],
                                                                              under_represented_racial_ethnic=category['under_represented_racial_ethnic'])
                                AllyStudentCategoryRelation.objects.create(ally_id=ally1.id,
                                                                           student_category_id=categories.id)
                        except IntegrityError:
                            errorLog[ally[0]] = "Ally already exists in the database"

                    except IntegrityError:
                        errorLog[ally[0]] = "user with username: " + user['username'] + " or email: " + user['email'] \
                                            + " already exists in database"
                else:
                    errorLog[ally[0]] = "Improperly formated -  user_type must be: Staff, Faculty, " \
                                        "Undergraduate Student, or Graduate Student"
        else:
            errorLog[0] = "Was not able to read the file, because the columns were improperly formatted"
        return errorLog, passwordLog

    @staticmethod
    def processFile(file):
        df = pd.read_csv(file)
        errorLog, passwordLog = UploadAllies.makeAlliesFromFile(df)
        return df, errorLog, passwordLog

    def upload_allies(request):
        if request.user.is_staff:
            try:
                file = request.FILES['file']
                df, errorLog, passwordLog = UploadAllies.processFile(file)

                output = io.BytesIO()
                workbook = xlsxwriter.Workbook(output)
                passwords = workbook.add_worksheet('New Passwords')
                errors = workbook.add_worksheet('Errors Uploading')
                passwords.write(0, 0, 'Username')
                passwords.write(0, 1, 'Email')
                passwords.write(0, 2, 'New Password')
                errors.write(0, 0, 'row of failure')
                errors.write(0, 1, 'failure mode')
                row = 1
                column = 0
                for error in errorLog.items():
                    errors.write(row, column, error[0])
                    errors.write(row, column + 1, error[1])
                    row += 1
                row = 1
                for password in passwordLog.items():
                    passwords.write(row, column, df['username'][password[0]])
                    passwords.write(row, column + 1, df['email'][password[0]])
                    passwords.write(row, column + 2, password[1])
                    row += 1
                workbook.close()
                output.seek(0)

                today = date.today()
                today = today.strftime("%b-%d-%Y")
                fileName = today + "_SAP_Upload-log.xlsx"
                response = HttpResponse(
                    output,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename=' + fileName
                return response
            except KeyError:
                messages.add_message(request, messages.ERROR, 'Please select a file to upload!')

            return redirect('sap:sap-dashboard')
        else:
            return HttpResponseForbidden()