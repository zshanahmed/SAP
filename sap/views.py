# pylint: skip-file

import io, os, os.path, csv, uuid, datetime
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import logout, login
from django.contrib.auth import authenticate
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import xlsxwriter
from .models import Ally, StudentCategories, AllyStudentCategoryRelation
from fuzzywuzzy import fuzz

from .models import Ally, StudentCategories, AllyStudentCategoryRelation, Event, EventAllyRelation
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
from django.utils.dateparse import parse_datetime


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
            return redirect('sap:ally-dashboard')

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


class ViewAllyProfileFromAdminDashboard(View):
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


class EditAllyProfile(View):

    def set_boolean(self, list, postDict, ally, same):
        selectionDict = {'studentsInterestedRadios': ally.people_who_might_be_interested_in_iba,
                         'labShadowRadios': ally.willing_to_offer_lab_shadowing,
                         'connectingRadios': ally.interested_in_connecting_with_other_mentors,
                        'openingRadios': ally.openings_in_lab_serving_at,
                         'mentoringFacultyRadios': ally.interested_in_mentoring,
                        'trainingRadios': ally.interested_in_mentor_training,
                         'volunteerRadios': ally.willing_to_volunteer_for_events,
                         'interestRadios': ally.interested_in_joining_lab,
                        'experienceRadios': ally.has_lab_experience,
                         'interestedRadios': ally.interested_in_mentoring,
                         'agreementRadios': ally.information_release,
                         'beingMentoredRadios': ally.interested_in_being_mentored}
        dict = {}
        for selection in list:
            if postDict[selection][0] == 'Yes':
                dict[selection] = True
                same = same and (dict[selection] == selectionDict[selection])
            else:
                dict[selection] = False
                same = same and (dict[selection] == selectionDict[selection])
        return dict, same

    def get(self, request, *args, **kwargs):
        try:
            username = request.GET['username']
        except KeyError:
            username = request.path.split('/')[-2]
        user_req = request.user
        if (username != user_req.username) and not user_req.is_staff:
            messages.warning(request, 'Access Denied!')
            return redirect('sap:ally-dashboard')
        else:
            try:
                user = User.objects.get(username=username)
                ally = Ally.objects.get(user=user)
                return render(request, 'sap/admin_ally_table/edit_ally.html', {
                    'ally': ally,
                    'req': request.user,
                })
            except Exception as e:
                print(e)
                return HttpResponseNotFound()

    def post(self, request, username=''):
        postDict = dict(request.POST)
        user_req = request.user
        message = ''
        if User.objects.filter(username=postDict["username"][0]).exists():
            same = True
            user = User.objects.get(username=postDict["username"][0])
            ally = Ally.objects.get(user=user)
            try:
                userType = postDict['roleSelected'][0]
                if userType != ally.user_type:
                    ally.user_type = userType
                    same = False
            except KeyError:
                message += ' User type could not be updated!\n'
            try:
                hawkId = postDict['hawkID'][0]
                if hawkId != ally.hawk_id and hawkId != '':
                    ally.hawk_id = hawkId
                    same = False
            except KeyError:
                message += " HawkID could not be updated!\n"
            if ally.user_type != "Undergraduate Student":
                selections, same = self.set_boolean(
                    ['studentsInterestedRadios', 'labShadowRadios', 'connectingRadios',
                     'openingRadios', 'mentoringFacultyRadios',
                     'trainingRadios', 'volunteerRadios'], postDict, ally, same)
                try:
                    aor = ','.join(postDict['stemGradCheckboxes'])
                except KeyError:
                    aor = ""
                try:
                    how_can_we_help = postDict["howCanWeHelp"][0]
                except KeyError:
                    how_can_we_help = ""
                try:
                    description = postDict['research-des'][0]
                except KeyError:
                    description = ""
                if not (description == ally.description_of_research_done_at_lab and
                        how_can_we_help == ally.how_can_science_ally_serve_you and
                        aor == ally.area_of_research):
                    same = False
                ally.description_of_research_done_at_lab = description
                ally.how_can_science_ally_serve_you = how_can_we_help
                ally.area_of_research = aor

                ally.people_who_might_be_interested_in_iba = selections['studentsInterestedRadios']
                ally.interested_in_mentoring = selections['mentoringFacultyRadios']
                ally.willing_to_offer_lab_shadowing = selections['labShadowRadios']
                ally.openings_in_lab_serving_at = selections['openingRadios']
                ally.interested_in_connecting_with_other_mentors = selections['connectingRadios']
                ally.willing_to_volunteer_for_events = selections['volunteerRadios']
                ally.interested_in_mentor_training = selections['trainingRadios']
                ally.save()
            else:
                if user_req.is_staff:
                    selections, same = self.set_boolean(
                        ['interestRadios', 'experienceRadios', 'interestedRadios', 'beingMentoredRadios'],
                        postDict, ally, same)
                else:
                    selections, same = self.set_boolean(
                        ['interestRadios', 'experienceRadios', 'beingMentoredRadios',
                         'interestedRadios', 'agreementRadios'],
                        postDict, ally, same)

                year = postDict['undergradRadios'][0]
                major = postDict['major'][0]
                if not (year == ally.year and major == ally.major):
                    same = False
                ally.year = year
                ally.major = major

                ally.interested_in_joining_lab = selections['interestRadios']
                ally.has_lab_experience = selections['experienceRadios']
                ally.interested_in_being_mentored = selections['beingMentoredRadios']
                ally.interested_in_mentoring = selections['interestedRadios']
                if not user_req.is_staff:
                    ally.information_release = selections['agreementRadios']
                ally.save()

            badUser = False
            badEmail = False
            badPassword = False

            try:
                newUsername = postDict['newUsername'][0]
                if newUsername != '' and newUsername != user.username:
                    if not User.objects.filter(username=newUsername):
                        user.username = newUsername
                        same = False
                    else:
                        badUser = True
                        message +=" Username not updated - Username already exists!\n"
            except KeyError:
                message += ' Username could not be updated!\n'
            try:
                newPassword = postDict['password'][0]
                if newPassword != '':
                    if not len(newPassword) < 8:
                        user.set_password(newPassword)
                        same = False
                    else:
                        badPassword = True
                        message += " Password could not be set because it is less than 8 characters long!"
            except KeyError:
                message += ' Password could not be updated!\n'
            try:
                firstName = postDict['firstName'][0]
                lastName = postDict['lastName'][0]
                if firstName != '' and firstName != user.first_name:
                    user.first_name = firstName
                    same = False
                if lastName != '' and lastName != user.last_name:
                    user.last_name = lastName
                    same = False
            except KeyError:
                message += ' First name or last name could not be updated!\n'
            if user_req.is_staff:
                try:
                    email = postDict['email'][0]
                    if email != '' and email != user.email:
                        if not User.objects.filter(email=email).exists():
                            user.email = email
                            same = False
                        else:
                            message += " Email could not be updated - Email already exists!\n"
                            badEmail = True
                except KeyError:
                    message += ' Email could not be updated!\n'
            user.save()
            if badPassword or badEmail or badPassword or badUser:
                if same:
                    messages.add_message(request, messages.WARNING, message)
                else:
                    messages.add_message(request, messages.WARNING,
                                         'No Changes Detected!' + message)
                return redirect(reverse('sap:admin_edit_ally', args=[postDict['username'][0]]))
            if same:
                messages.add_message(request, messages.WARNING,
                                     'No Changes Detected!' + message)
                return redirect(reverse('sap:admin_edit_ally', args=[postDict['username'][0]]))

            if not user_req.is_staff:
                messages.add_message(request, messages.SUCCESS,
                                        'Profile updated!\n' + message)
            else:
                messages.add_message(request, messages.SUCCESS,
                                    'Ally updated!\n' + message)
        else:
            messages.add_message(request, messages.WARNING,
                                 'Ally does not exist!')
        if user_req.is_staff:
            return redirect('sap:sap-dashboard')
        else:
            return redirect('sap:ally-dashboard')


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


class ChangeAdminPassword(View):
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


class CalendarView(TemplateView):
    template_name = "sap/calendar.html"

class EditAdminProfile(View):
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

class AlliesListView(AccessMixin, TemplateView):

    def get(self, request):
        allies_list = Ally.objects.order_by('-id')
        for ally in allies_list:
            if not ally.user.is_active:
                allies_list = allies_list.exclude(id=ally.id)
        return render(request, 'sap/dashboard.html', {'allies_list': allies_list})

    def post(self, request):
        if request.POST.get("form_type") == 'filters':
            postDict = dict(request.POST)
            if 'stemGradCheckboxes' in postDict:
                stemfields = postDict['stemGradCheckboxes']
                exclude_from_aor_default = False
            else:
                exclude_from_aor_default = True
                stemfields =[]
            
            if 'undergradYear' in postDict:
                exclude_from_year_default = False
                undergradYear = postDict['undergradYear']
            else:
                exclude_from_year_default = True
                undergradYear = []
            
            if 'idUnderGradCheckboxes' in postDict:
                studentCategories = postDict['idUnderGradCheckboxes']
                exclude_from_sc_default = False
            else:
                exclude_from_sc_default = True
                studentCategories = []
            
            if 'roleSelected' in postDict:
                userTypes = postDict['roleSelected']
                exclude_from_ut_default = False
            else:
                exclude_from_ut_default = True
                userTypes = []
            
            if 'mentorshipStatus' in postDict:
                mentorshipStatus = postDict['mentorshipStatus'][0]
                exclude_from_ms_default = False
            else:
                exclude_from_ms_default = True
                mentorshipStatus = []
            
            major = postDict['major'][0]
            if major != '':
                exclude_from_major_default = False
            else:
                exclude_from_major_default = True

            allies_list = Ally.objects.order_by('-id')
            if not (exclude_from_year_default and exclude_from_aor_default and exclude_from_sc_default and exclude_from_ut_default and exclude_from_ms_default and exclude_from_major_default):
                for ally in allies_list:
                    exclude_from_aor = exclude_from_aor_default
                    exclude_from_year = exclude_from_year_default
                    exclude_from_sc = exclude_from_sc_default
                    exclude_from_ut = exclude_from_ut_default
                    exclude_from_ms = exclude_from_ms_default
                    exclude_from_major = exclude_from_major_default

                    if (major != '') and (fuzz.ratio(ally.major, major) < 90):
                        exclude_from_major = True

                    if ally.area_of_research:
                        aor = ally.area_of_research.split(',')
                    else:
                        aor = []
                    if (stemfields) and (not bool(set(stemfields) & set(aor))):
                        exclude_from_aor = True
                    
                    if (mentorshipStatus != []):
                        if (mentorshipStatus == 'Mentor') and (ally.interested_in_mentoring == False):
                            exclude_from_ms = True
                        elif (mentorshipStatus == 'Mentee') and (ally.interested_in_being_mentored == False):
                            exclude_from_ms = True
                    
                    try:
                        categories = AllyStudentCategoryRelation.objects.filter(
                            ally_id=ally.id).values()[0]
                        categories = StudentCategories.objects.filter(
                            id=categories['student_category_id'])[0]
                    except:
                        studentCategories = []

                    if (studentCategories):
                        for cat in studentCategories:
                            if (cat == 'First generation college-student') and (categories.first_gen_college_student == False):
                                exclude_from_sc = True
                            elif (cat == 'Low-income') and (categories.low_income == False):
                                exclude_from_sc = True
                            elif (cat == 'Underrepresented racial/ethnic minority') and (categories.under_represented_racial_ethnic == False):
                                exclude_from_sc = True
                            elif (cat == 'LGBTQ') and (categories.lgbtq == False):
                                exclude_from_sc = True
                            elif (cat == 'Rural') and (categories.rural == False):
                                exclude_from_sc = True
                            elif (cat == 'Disabled') and (categories.disabled == False):
                                exclude_from_sc = True

                    if (undergradYear) and (ally.year not in undergradYear):
                        exclude_from_year = True
                    
                    if (userTypes) and (ally.user_type not in userTypes):
                        print('User Type:', ally.user_type)
                        exclude_from_ut = True

                    if exclude_from_aor and exclude_from_year and exclude_from_sc and exclude_from_ut and exclude_from_ms and exclude_from_major:
                        allies_list = allies_list.exclude(id=ally.id)
            for ally in allies_list:
                if not ally.user.is_active:
                    allies_list = allies_list.exclude(id=ally.id)
            return render(request, 'sap/dashboard.html', {'allies_list': allies_list})

class MentorsListView(generic.ListView):
    template_name = 'sap/dashboard_ally.html'
    context_object_name = 'allies_list'

    def get(self, request):
        allies_list = Ally.objects.order_by('-id')
        for ally in allies_list:
            if not ally.user.is_active:
                allies_list = allies_list.exclude(id=ally.id)
        return render(request, 'sap/dashboard_ally.html', {'allies_list': allies_list})

    def post(self, request):
        if request.POST.get("form_type") == 'filters':
            postDict = dict(request.POST)
            if 'stemGradCheckboxes' in postDict:
                stemfields = postDict['stemGradCheckboxes']
                exclude_from_aor_default = False
            else:
                exclude_from_aor_default = True
                stemfields =[]
            if 'undergradYear' in postDict:
                exclude_from_year_default = False
                undergradYear = postDict['undergradYear']
            else:
                exclude_from_year_default = True
                undergradYear = []
            allies_list = Ally.objects.order_by('-id')
            if not (exclude_from_year_default and exclude_from_aor_default):
                for ally in allies_list:
                    exclude_from_aor = exclude_from_aor_default
                    exclude_from_year = exclude_from_year_default

                    if ally.area_of_research:
                        aor = ally.area_of_research.split(',')
                    else:
                        aor = []
                    if (stemfields) and (not bool(set(stemfields) & set(aor))):
                        exclude_from_aor = True


                    if (undergradYear) and (ally.year not in undergradYear):
                        exclude_from_year = True

                    if exclude_from_aor and exclude_from_year:
                        allies_list = allies_list.exclude(id=ally.id)
            for ally in allies_list:
                if not ally.user.is_active:
                    allies_list = allies_list.exclude(id=ally.id)
            return render(request, 'sap/dashboard_ally.html', {'allies_list': allies_list})

class AnalyticsView(AccessMixin, TemplateView):
    template_name = "sap/analytics.html"


class AdminProfileView(TemplateView):
    template_name = "sap/profile.html"


class AboutPageView(TemplateView):
    template_name = "sap/about.html"


class ResourcesView(TemplateView):
    template_name = "sap/resources.html"


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
            messages.add_message(request, messages.ERROR,
                                 'Account was not created because one or more fields were not entered')
            return redirect('/create_iba_admin')


class CreateEventView(AccessMixin, TemplateView):
    template_name = "sap/create_event.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        new_event_dict = dict(request.POST)
        event_title = new_event_dict['event_title'][0]
        event_description = new_event_dict['event_description'][0]
        event_start_time = new_event_dict['event_start_time'][0]
        event_end_time = new_event_dict['event_end_time'][0]
        event_end_time = new_event_dict['event_allday'][0]
        event_location = new_event_dict['event_location'][0]

        if 'role_selected' in new_event_dict:
            invite_ally_user_types = new_event_dict['role_selected']
        else:
            invite_ally_user_types = []

        if 'mentor_status' in new_event_dict:
            invite_mentor_mentee = new_event_dict['mentor_status']
        else:
            invite_mentor_mentee = []

        if 'special_category' in new_event_dict:
            invite_ally_belonging_to_special_categories = new_event_dict['special_category']
        else:
            invite_ally_belonging_to_special_categories = []

        if 'research_area' in new_event_dict:
            invite_ally_belonging_to_research_area = new_event_dict['research_area']
        else:
            invite_ally_belonging_to_research_area = []


        if 'invite_all' in new_event_dict:
            invite_all_selected = True
        else:
            invite_all_selected = []

        event = Event.objects.create(title=event_title,
                                     description=event_description,
                                     start_time=parse_datetime(event_start_time + '-0500'), # converting time to central time before storing in db
                                     location=event_location
                                     )

        if invite_all_selected:
            allies_to_be_invited = list(Ally.objects.all())
        else:
            allies_to_be_invited = []

            allies_to_be_invited.extend(Ally.objects.filter(user_type__in=invite_ally_user_types))

            if 'Mentors' in invite_mentor_mentee:
                allies_to_be_invited.extend(Ally.objects.filter(interested_in_mentoring=True))

            if 'Mentees' in invite_mentor_mentee:
                allies_to_be_invited.extend(Ally.objects.filter(interested_in_mentor_training=True))


            allies_to_be_invited.extend(Ally.objects.filter(area_of_research__in=invite_ally_belonging_to_research_area))
            student_categories_to_include_for_event = []

            for category in invite_ally_belonging_to_special_categories:
                if  category == 'First generation college-student':
                    student_categories_to_include_for_event.extend(StudentCategories.objects.filter(first_gen_college_student=True))

                elif category == 'Low-income':
                    student_categories_to_include_for_event.extend(StudentCategories.objects.filter(low_income=True))

                elif category == 'Underrepresented racial/ethnic minority':
                    student_categories_to_include_for_event.extend(StudentCategories.objects.filter(under_represented_racial_ethnic=True))

                elif category == 'LGBTQ':
                    student_categories_to_include_for_event.extend(StudentCategories.objects.filter(lgbtq=True))

                elif category == 'Rural':
                    student_categories_to_include_for_event.extend(StudentCategories.objects.filter(rural=True))

                elif category == 'Disabled':
                    student_categories_to_include_for_event.extend(StudentCategories.objects.filter(disabled=True))

            invited_allies_ids = AllyStudentCategoryRelation.objects.filter(student_category__in=student_categories_to_include_for_event).values('ally')
            allies_to_be_invited.extend(
                Ally.objects.filter(id__in=invited_allies_ids)
                )

        all_event_ally_objs = []
        invited_allies = set()
        allies_to_be_invited = set(allies_to_be_invited)

        for ally in allies_to_be_invited:
            event_ally_rel_obj = EventAllyRelation(event=event, ally=ally)
            all_event_ally_objs.append(event_ally_rel_obj)
            invited_allies.add(event_ally_rel_obj.ally)


        EventAllyRelation.objects.bulk_create(all_event_ally_objs)

        return redirect('/dashboard')


class CalendarListView(TemplateView):
    template_name = "sap/calendar_list.html"


class EventSignUpView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def get(self, request, *args, **kwargs):
        pass


class EventSignUpDoneView(TemplateView):
    def get(self, request, *args, **kwargs):
        # template =
        pass

    def post(self, request, *args, **kwargs):
    # TODO: a function to withdraw from meeting
        pass


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
            elif id == 'Disabled':
                categories.disabled = True
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

    def create_new_user(self, postDict):
        """
        Create new user and associated ally based on what user inputs in sign-up page
        """
        user = User.objects.create_user(username=postDict["new_username"][0],
                                        password=postDict["new_password"][0],
                                        email=postDict["new_email"][0],
                                        first_name=postDict["firstName"][0],
                                        last_name=postDict["lastName"][0],
                                        is_active=False  # Important! Set to False until user verify via email
                                        )

        if postDict['roleSelected'][0] == 'Staff':
            selections = self.set_boolean(['studentsInterestedRadios'], postDict)
            ally = Ally.objects.create(user=user,
                                       user_type=postDict['roleSelected'][0],
                                       hawk_id=user.username,
                                       people_who_might_be_interested_in_iba=selections['studentsInterestedRadios'],
                                       how_can_science_ally_serve_you=postDict['howCanWeHelp'])
        else:
            if postDict['roleSelected'][0] == 'Undergraduate Student':
                try:
                    categories = self.make_categories(postDict["idUnderGradCheckboxes"])
                except KeyError:
                    categories = StudentCategories.objects.create()
                undergradList = ['interestRadios', 'experienceRadios', 'interestedRadios',
                                 'agreementRadios', 'beingMentoredRadios']
                selections = self.set_boolean(undergradList, postDict)
                ally = Ally.objects.create(user=user,
                                           user_type=postDict['roleSelected'][0],
                                           hawk_id=user.username,
                                           major=postDict['major'][0],
                                           year=postDict['undergradRadios'][0],
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
                ally = Ally.objects.create(user=user,
                                           user_type=postDict['roleSelected'][0],
                                           hawk_id=user.username,
                                           area_of_research=stem_fields,
                                           interested_in_mentoring=selections['mentoringGradRadios'],
                                           willing_to_offer_lab_shadowing=selections['labShadowRadios'],
                                           interested_in_connecting_with_other_mentors=selections['connectingRadios'],
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
                ally = Ally.objects.create(user=user,
                                           user_type=postDict['roleSelected'][0],
                                           hawk_id=user.username,
                                           area_of_research=stem_fields,
                                           openings_in_lab_serving_at=selections['openingRadios'],
                                           description_of_research_done_at_lab=postDict['research-des'][0],
                                           interested_in_mentoring=selections['mentoringFacultyRadios'],
                                           willing_to_volunteer_for_events=selections['volunteerRadios'],
                                           interested_in_mentor_training=selections['trainingRadios'])

            AllyStudentCategoryRelation.objects.create(student_category_id=categories.id, ally_id=ally.id)

        return user, ally

    def send_verification_email(self, user, site, entered_email):
        """
        Send verification email to finish sign-up, basically set is_active to True
        """
        message_body = render_to_string('sap/sign-up-mail.html', {
            'user': user,
            'protocol': 'http',
            'domain': site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),  # encode user's primary key
            'token': account_activation_token.make_token(user),
        })

        email_content = Mail(
            from_email="iba@uiowa.edu",
            to_emails=entered_email,
            subject='Action Required: Confirm Your New Account',
            html_content=message_body)

        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(email_content)

        except Exception as e:
            print(e)

    def get(self, request):
        """
        First log current user out
        """
        logout(request)
        return render(request, self.template_name)

    def post(self, request):
        """
        If user/ally is in the db but is_active=False, that user/ally is deemed "replaceable", meaning new account can
        be created with its email address.
        If user/ally is in the db but is_active=True, cannot create new account with that email address.
        """
        postDict = dict(request.POST)

        min_length = 8  # Minimum length for a valid password

        if User.objects.filter(email=postDict["new_email"][0]).exists():
            user_temp = User.objects.get(email=postDict["new_email"][0])

            if user_temp.is_active: # If user is active, cannot create new account
                messages.warning(request,
                                 'Account can not be created because an account associated with this email address already exists!')
                return redirect('/sign-up')

            else:   # If user is not active, delete user_temp and create new user on db with is_active=False
                ally_temp = Ally.objects.get(user=user_temp)
                ally_temp.delete()
                user_temp.delete()

                # print(request.POST)
                if User.objects.filter(username=postDict["new_username"][0]).exists():
                    messages.warning(request,
                                     'Account can not be created because username already exists!')
                    return redirect('/sign-up')
                # elif User.objects.filter(email=postDict["new_email"][0]).exists():
                #     messages.add_message(request, messages.WARNING,
                #                          'Account can not be created because email already exists')
                #     return redirect('/sign-up')
                elif postDict["new_password"][0] != postDict["repeat_password"][0]:
                    messages.warning(request,
                                     "Repeated password is not the same as the inputted password!",)
                    return redirect("/sign-up")
                elif len(postDict["new_password"][0]) < min_length:
                    messages.warning(request,
                                     "Password must be at least {0} characters long".format(min_length),)
                    return redirect("/sign-up")
                else:
                    user, ally = self.create_new_user(postDict=postDict)
                    site = get_current_site(request)
                    self.send_verification_email(user=user, site=site, entered_email=postDict["new_email"][0])

                    return redirect("sap:sign-up-done")

        elif not User.objects.filter(email=postDict["new_email"][0]).exists():
            if User.objects.filter(username=postDict["new_username"][0]).exists():
                messages.warning(request,
                                 'Account can not be created because username already exists!')
                return redirect('/sign-up')
            # elif User.objects.filter(email=postDict["new_email"][0]).exists():
            #     messages.add_message(request, messages.WARNING,
            #                          'Account can not be created because email already exists')
            #     return redirect('/sign-up')
            elif postDict["new_password"][0] != postDict["repeat_password"][0]:
                messages.warning(request,
                                 "Repeated password is not the same as the inputted password!")
                return redirect("/sign-up")
            elif len(postDict["new_password"][0]) < min_length:
                messages.warning(request,
                                 "Password must be at least {0} characters long".format(min_length))
                return redirect("/sign-up")
            else:
                user, ally = self.create_new_user(postDict=postDict)
                site = get_current_site(request)
                self.send_verification_email(user=user, site=site, entered_email=postDict["new_email"][0])

                return redirect("sap:sign-up-done")


class SignUpDoneView(TemplateView):
    """
    A view which is presented if the user successfully fill out the form presented in Sign-Up view
    """
    template_name = "sap/sign-up-done.html"


class SignUpConfirmView(TemplateView):
    """
    Only for those who click on verification email during sign-up.
    No POST method.
    """
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

        if user is not None and user.is_active:
            messages.success(request, 'Account already verified.')
            return redirect('sap:home')
        elif user is not None and account_activation_token.check_token(user, token):
            user.is_active = True  # activates the user
            user.save()
            messages.success(request, 'Account successfully created! You can now log in with your new account.')
            return redirect('sap:home')
        else:
            messages.error(request, 'Invalid account activation link.')
            return redirect('sap:home')


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
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)), # encode user's primary key
                    'token': password_reset_token.make_token(user),
                })

                # message_ = reverse('sap:password-forgot-confirm',
                #                    args=[urlsafe_base64_encode(force_bytes(user.pk)),
                #                          password_reset_token.make_token(user)])
                #
                # message_body = 'http:' + '//' + site.domain + message_

                email_content = Mail(
                    from_email="iba@uiowa.edu",
                    to_emails=entered_email,
                    subject='Reset Password for Science Alliance Portal',
                    html_content=message_body)

                try:
                    # TODO: Change API key and invalidate the old one
                    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                    response = sg.send(email_content)
                except Exception as e:
                    print(e)

                return redirect('/password-forgot-done')

            else:
                return redirect('/password-forgot-done')
                # return render(request, 'account/password-forgot.html', {'form': form})

        return render(request, 'sap/password-forgot.html', {'form': form})


class ForgotPasswordDoneView(TemplateView):
    """
    A view which is presented if the user entered valid email in Forget Password view
    """
    template_name = "sap/password-forgot-done.html"


class ForgotPasswordConfirmView(TemplateView):
    """
    A unique view to users who click to the reset forgot passwork link.
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
                  'low_income', 'rural', 'disabled']
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
                      [None, None, None, None, None, None, None]
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


boolFields=['Do you currently have openings for undergraduate students in your lab?',
            'Would you be willing to offer lab shadowing to potential students?',
            'Are you interested in mentoring students?',
            'Are you interested in connecting with other mentors?',
            'Would you be willing to volunteer for panels, networking workshops, and other events as professional development for students?',
            'Are you interested in mentor training?',
            'Do you know students who would be interested in the Science Alliance?',
            'Are you interested in joining a lab?',
            'Do you have experience working in a laboratory?',
            'Are you interested in becoming a peer mentor?']
class UploadAllies(AccessMixin, HttpResponse):

    @staticmethod
    def cleanupFrame(df):
        errorlog = {}
        try:
            df = df.drop(['Workflow ID', 'Status', 'Name'], axis=1)
        except KeyError:
            errorlog[1000] = "Could not drop unnecessary columns \'Workflow ID\', \'Status\', \'Name\'"
        try:
            df1 = pd.DataFrame({"Name": df['Initiator']})
        except KeyError:
            errorlog[2000] = "CRITICAL ERROR: The \'Initiator\' column is not present, cannot proceed"
            return df, errorlog
        try:
            df2 = df1.applymap(lambda x: x.split('\n'))
            df2 = df2.applymap(lambda x: x[0] + x[1])
            df2 = df2.replace(regex=['\d'], value='')
            df2 = df2['Name'].str.split(', ', n=1, expand=True)
            df2 = df2.rename({0: 'last_name', 1: 'first_name'}, axis=1)
            df = df.join(df2)
            df['email'] = df['Initiator'].str.extract(r'(.*@uiowa.edu)')
            df = df.drop(['Initiator'], axis=1)
        except:
            errorlog[3000] = "CRITICAL ERROR: data could not be extracted from \'Initiator\' column " \
                             "and added as columns"
            return df, errorlog
        try:
            df[boolFields] = df[boolFields].fillna(value=False)
            df[boolFields] = df[boolFields].replace('Yes (Yes)', True)
            df[boolFields] = df[boolFields].replace('No (No)', False)
            df['interested_in_mentoring'] = False
            for i in range(0, len(df)):
                df['interested_in_mentoring'][i] = df['Are you interested in becoming a peer mentor?'][i] or \
                                                   df['Are you interested in mentoring students?'][i]
            df = df.drop(['Are you interested in becoming a peer mentor?',
                          'Are you interested in mentoring students?'], axis=1)
            df = df.rename({
                'Do you currently have openings for undergraduate students in your lab?': 'openings_in_lab_serving_at',
                'Would you be willing to offer lab shadowing to potential students?': 'willing_to_offer_lab_shadowing',
                'Are you interested in connecting with other mentors?': 'interested_in_connecting_with_other_mentors',
                'Would you be willing to volunteer for panels, networking workshops, and other events as professional development for students?': 'willing_to_volunteer_for_events',
                'Are you interested in mentor training?': 'interested_in_mentor_training',
                'Do you know students who would be interested in the Science Alliance?': 'people_who_might_be_interested_in_iba',
                'Are you interested in joining a lab?': 'interested_in_joining_lab',
                'Do you have experience working in a laboratory?': 'has_lab_experience'
            }, axis=1)
        except KeyError:
            errorlog[4000] = "CRITICAL ERROR: boolean could not replace blanks. Ensure the following are present:" + \
                str(boolFields)
            return df, errorlog
        try:
            df = df.fillna(value='')
            df['STEM Area of Research'] = df['STEM Area of Research'].replace(regex=[r'\n'], value=',')
            df['STEM Area of Research'] = df['STEM Area of Research'].replace(regex=[r'\s\([^)]*\)'], value='')
            df['University Type'] = df['University Type'].replace(regex=[r'\s\([^)]*\)', '/Post-doc'], value='')
            df['Year'] = df['Year'].replace(regex=r'\s\([^)]*\)', value='')
            df = df.rename({'STEM Area of Research': 'area_of_research',
                            'University Type': 'user_type',
                            'Please provide a short description of the type of research done by undergrads': 'description_of_research_done_at_lab',
                            'Year': 'year', 'Major': 'major',
                            'How can the Science Alliance serve you?': 'how_can_science_ally_serve_you'},
                           axis=1)
        except KeyError:
            errorlog[5000] = "CRITICAL ERROR: problem in tidying charfield columns. ensure the following is present:" \
            "STEM Area of Research, University Type, Please provide a short description of the type of research done by undergrads, " \
            "Year, Major"
            return df, errorlog
        try:
            df['Submission Date'] = df['Submission Date'].map(lambda x: x.strftime("%b-%d-%Y"))
            df = df.rename({'Submission Date': 'date_joined'}, axis=1)
        except KeyError:
            errorlog[6000] = "CRITICAL ERROR: problem converting timestamp to date, please ensure Submission Date is a column"
            return df, errorlog
        try:
            df['username'] = ''
            for i in range(0, len(df)):
                hawkid = df['first_name'][i][0] + df['last_name'][i]
                df['username'][i] = hawkid.lower()
        except:
            errorlog[7000] = "CRITICAL ERROR: Could not convert first name and last name to hawkid. Please Ensure the " \
            "Initiator is present"
            return df, errorlog
        df['information_release'] = False
        df['interested_in_being_mentored'] = False
        df['is_active'] = True
        df['works_at'] = ''
        df['last_login'] = ''
        df[categoryFields] = False
        try:
            # pd.set_option('display.max_columns', 100)
            # print(df)
            for i in range(0, len(df)):
                tmp = df['Are you interested in serving as a mentor to students who identify as any of the following (check all that may apply)'][i]
                if 'First generation college-student' in tmp:
                    df['first_gen_college_student'][i] = True
                if 'LGBTQ' in tmp:
                    df['lgbtq'][i] = True
                if 'Transfer student' in tmp:
                    df['transfer_student'][i] = True
                if 'Underrepresented racial/ethnic minority' in tmp:
                    df['under_represented_racial_ethnic'][i] = True
            df = df.drop(['Are you interested in serving as a mentor to students who identify as any of the following (check all that may apply)'], axis=1)
        except:
            errorlog[8000] = "Possible data error: willing to mentor may be inaccurate. Please ensure the column: " \
            "\'Are you interested in serving as a mentor to students who identify as any of the following (check all that may apply)\'" \
            " is present"
        return df, errorlog


    @staticmethod
    def makeAlliesFromDataFrame(df, errorLog):
        columns = list(df.columns)
        passwordLog = {}
        allyData = {}
        userData = {}
        categoryData = {}
        try:
            allyData = df[allyFields].to_dict('index')
            userData = df[userFields].to_dict('index')
            categoryData = df[categoryFields].to_dict('index')
        except KeyError:
            errorLog[9000] = "CRITICAL ERROR: Data does not contain necessary columns. Please ensure that the data has columns:\n" + \
                str(userFields + allyFields + categoryFields)
        for ally in allyData.items():
            if ("Staff" == ally[1]['user_type'] or "Graduate Student" == ally[1]['user_type']
                    or "Undergraduate Student" == ally[1]['user_type'] or "Faculty" == ally[1]['user_type']):
                password = uuid.uuid4().hex[0:9]
                user = userData[ally[0]]
                try:
                    time = datetime.datetime.strptime(user['date_joined'], '%b-%d-%Y')
                    #time = datetime.strptime(user['date_joined'], "%Y-%m-%d")
                    user = User.objects.create_user(username=user['username'], password=password, email=user['email'],
                                                first_name=user['first_name'], last_name=user['last_name'],
                                                    date_joined=time)
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
                                                                          under_represented_racial_ethnic=category['under_represented_racial_ethnic'],
                                                                          disabled=category['disabled'])
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
        return errorLog, passwordLog

    @staticmethod
    def processFile(file):
        errorLog = {}
        passwordLog = {}
        df = pd.DataFrame()
        try:
            df = pd.read_csv(file)
        except:
            try:
                df = pd.read_excel(file)
            except:
                errorLog[900] = "Problem reading file: was it stored in .csv or xlsx?"

        columns = list(df.columns)
        if columns != (userFields + allyFields + categoryFields):
            df, errorLog = UploadAllies.cleanupFrame(df)
        else:
            df = df.replace(df.fillna('', inplace=True))
        errorLog, passwordLog = UploadAllies.makeAlliesFromDataFrame(df, errorLog)
        return UploadAllies.makeFile(df, errorLog, passwordLog)

    @staticmethod
    def makeFile(df, errorLog, passwordLog):
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
        return output


    def upload_allies(request):
        if request.user.is_staff:
            try:
                file = request.FILES['file']
                output = UploadAllies.processFile(file)
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
