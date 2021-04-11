"""
views has functions that are mapped to the urls in urls.py
"""
import io
import os
import os.path
import csv
import uuid
import datetime
from datetime import date
import xlsxwriter
from fuzzywuzzy import fuzz
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import pandas as pd

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.db import IntegrityError
from django.db.models import Q
from django.views import generic
from django.views.generic import TemplateView, View
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponseNotFound
from django.utils.dateparse import parse_datetime
from .tokens import password_reset_token, account_activation_token

from .forms import UpdateAdminProfileForm, UserResetForgotPasswordForm
from .models import Announcement, EventInviteeRelation, Ally, StudentCategories, AllyStudentCategoryRelation, Event

# Create your views here.

User = get_user_model()


def login_success(request):
    """
    Redirects users based on whether they are staff or not
    """

    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('sap:sap-dashboard')

        return redirect('sap:ally-dashboard')

    return redirect('sap:home')


def logout_request(request):
    """
    function to log an user out
    """
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
    """
    Class that contains admin dashboard view
    """
    def get(self, request):
        """
        method to retrieve all ally information
        """
        username = request.GET['username']
        try:
            user = User.objects.get(username=username)
            ally = Ally.objects.get(user=user)
            return render(request, 'sap/admin_ally_table/view_ally.html', {
                'ally': ally
            })
        except ObjectDoesNotExist:
            return HttpResponseNotFound()


class EditAllyProfile(View):
    """
    Enter what this class/method does
    """

    @staticmethod
    def set_boolean(_list, post_dict, ally, same):
        """Enter what this class/method does"""
        selection_dict = {'studentsInterestedRadios': ally.people_who_might_be_interested_in_iba,
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
        dictionary = {}
        for selection in _list:
            if post_dict[selection][0] == 'Yes':
                dictionary[selection] = True
                same = same and (dictionary[selection] == selection_dict[selection])
            else:
                dictionary[selection] = False
                same = same and (dictionary[selection] == selection_dict[selection])
        return dictionary, same

    @staticmethod
    def get(request, username=''):
        """Enter what this class/method does"""
        try:
            username = request.GET['username']
        except KeyError:
            username = request.path.split('/')[-2]
        user_req = request.user
        if (username != user_req.username) and not user_req.is_staff:
            messages.warning(request, 'Access Denied!')
            return redirect('sap:ally-dashboard')

        try:
            user = User.objects.get(username=username)
            ally = Ally.objects.get(user=user)
            return render(request, 'sap/admin_ally_table/edit_ally.html', {
                'ally': ally,
                'req': request.user,
            })
        except ObjectDoesNotExist:
            return HttpResponseNotFound()

    def post(self, request):
        """Enter what this class/method does"""
        post_dict = dict(request.POST)
        user_req = request.user
        message = ''

        if User.objects.filter(username=post_dict["username"][0]).exists():
            same = True
            user = User.objects.get(username=post_dict["username"][0])
            ally = Ally.objects.get(user=user)
            try:
                user_type = post_dict['roleSelected'][0]
                if user_type != ally.user_type:
                    ally.user_type = user_type
                    same = False
            except KeyError:
                message += ' User type could not be updated!\n'
            try:
                hawk_id = post_dict['hawkID'][0]
                if hawk_id not in (ally.hawk_id, ''):
                    ally.hawk_id = hawk_id
                    same = False
            except KeyError:
                message += " HawkID could not be updated!\n"
            if ally.user_type != "Undergraduate Student":
                selections, same = self.set_boolean(
                    ['studentsInterestedRadios', 'labShadowRadios', 'connectingRadios',
                     'openingRadios', 'mentoringFacultyRadios',
                     'trainingRadios', 'volunteerRadios'], post_dict, ally, same)
                try:
                    aor = ','.join(post_dict['stemGradCheckboxes'])
                except KeyError:
                    aor = ""
                try:
                    how_can_we_help = post_dict["howCanWeHelp"][0]
                except KeyError:
                    how_can_we_help = ""
                try:
                    description = post_dict['research-des'][0]
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
                        post_dict, ally, same)
                else:
                    selections, same = self.set_boolean(
                        ['interestRadios', 'experienceRadios', 'beingMentoredRadios',
                         'interestedRadios', 'agreementRadios'],
                        post_dict, ally, same)

                year = post_dict['undergradRadios'][0]
                major = post_dict['major'][0]
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

            bad_user = False
            bad_email = False
            bad_password = False

            try:
                new_username = post_dict['newUsername'][0]
                if new_username != '' and new_username != user.username:
                    if not User.objects.filter(username=new_username):
                        user.username = new_username
                        same = False
                    else:
                        bad_user = True
                        message += " Username not updated - Username already exists!\n"
            except KeyError:
                message += ' Username could not be updated!\n'
            try:
                new_password = post_dict['password'][0]
                if new_password != '':
                    if not len(new_password) < 8:
                        user.set_password(new_password)
                        same = False
                    else:
                        bad_password = True
                        message += " Password could not be set because it is less than 8 characters long!"
            except KeyError:
                message += ' Password could not be updated!\n'
            try:
                first_name = post_dict['firstName'][0]
                last_name = post_dict['lastName'][0]
                if first_name not in ('', user.first_name):
                    user.first_name = first_name
                    same = False
                if last_name not in ('', user.last_name):
                    user.last_name = last_name
                    same = False
            except KeyError:
                message += ' First name or last name could not be updated!\n'
            if user_req.is_staff:
                try:
                    email = post_dict['email'][0]
                    if email not in ('', user.email):
                        if not User.objects.filter(email=email).exists():
                            user.email = email
                            same = False
                        else:
                            message += " Email could not be updated - Email already exists!\n"
                            bad_email = True
                except KeyError:
                    message += ' Email could not be updated!\n'
            user.save()
            if bad_password or bad_email or bad_password or bad_user:
                if same:
                    messages.add_message(request, messages.WARNING, message)
                else:
                    messages.add_message(request, messages.WARNING,
                                         'No Changes Detected!' + message)
                return redirect(reverse('sap:admin_edit_ally', args=[post_dict['username'][0]]))
            if same:
                messages.add_message(request, messages.WARNING,
                                     'No Changes Detected!' + message)
                return redirect(reverse('sap:admin_edit_ally', args=[post_dict['username'][0]]))

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

        return redirect('sap:ally-dashboard')


class CreateAnnouncement(AccessMixin, HttpResponse):
    """
    Create annoucnemnnts
    """

    @classmethod
    def create_announcement(cls, request):
        """
        Enter what this class/method does
        """
        if request.user.is_staff:
            post_dict = dict(request.POST)
            curr_user = request.user
            title = post_dict['title'][0]
            description = post_dict['desc'][0]
            Announcement.objects.create(
                username=curr_user.username,
                title=title,
                description=description,
                created_at=datetime.datetime.now()
            )

            messages.success(request, 'Annoucement created successfully !!')
            return redirect('sap:sap-dashboard')

        return HttpResponseForbidden()


class DeleteAllyProfileFromAdminDashboard(AccessMixin, View):
    """
    Enter what this class/method does
    """
    def get(self, request):
        """Enter what this class/method does"""
        username = request.GET['username']

        try:
            user = User.objects.get(username=username)
            ally = Ally.objects.get(user=user)
            ally.delete()
            user.delete()
            messages.success(request, 'Successfully deleted the user ' + username)
            return redirect('sap:sap-dashboard')

        except ObjectDoesNotExist:
            return HttpResponseNotFound("")


class ChangeAdminPassword(View):
    """
    Change the password for admin
    """

    def get(self, request, *args, **kwargs):
        """Enter what this class/method does"""
        form = PasswordChangeForm(request.user)
        return render(request, 'sap/change_password.html', {
            'form': form
        })

    def post(self, request, *args, **kwargs):
        """Enter what this class/method does"""
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'Password Updated Successfully !')
            return redirect('sap:change_password')

        messages.error(request, "Could not Update Password !")

        return render(request, 'sap/change_password.html', {
            'form': form
        })


class CalendarView(TemplateView):
    """
     Show calendar to allies so that they can signup for events
    """

    def get(self, request):
        """Enter what this class/method does"""
        events_list = []
        curr_user = request.user
        if not curr_user.is_staff:
            curr_ally = Ally.objects.get(user_id=curr_user.id)
            curr_events = EventInviteeRelation.objects.filter(ally_id=curr_ally.id)
            for event in curr_events:
                events_list.append(Event.objects.get(id=event.event_id))
        else:
            events_list = Event.objects.all()
        events = serializers.serialize('json', events_list)
        return render(request, 'sap/calendar.html', context={"events": events, "user": curr_user})


class EditAdminProfile(View):
    """
    Change the profile for admin
    """

    def get(self, request):
        """Enter what this class/method does"""
        form = UpdateAdminProfileForm()
        return render(request, 'sap/profile.html', {
            'form': form
        })

    def post(self, request):
        """Enter what this class/method does"""
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


class Announcements(TemplateView):
    """Enter what this class/method does"""
    def get(self, request):
        """Enter what this class/method does"""
        announcments_list = Announcement.objects.order_by('-created_at')
        if request.user.is_staff:
            role = "admin"
        else:
            role = "ally"
        for announcment in announcments_list:
            pass
        return render(request, 'sap/announcements.html', {'announcments_list': announcments_list, 'role': role})


class AlliesListView(AccessMixin, TemplateView):
    """Enter what this class/method does"""

    def get(self, request):
        """Enter what this class/method does"""
        allies_list = Ally.objects.order_by('-id')
        for ally in allies_list:
            if not ally.user.is_active:
                allies_list = allies_list.exclude(id=ally.id)
        return render(request, 'sap/dashboard.html', {'allies_list': allies_list})

    def post(self, request):
        """Enter what this class/method does"""
        if request.POST.get("form_type") == 'filters':
            postDict = dict(request.POST)
            if 'stemGradCheckboxes' in postDict:
                stemfields = postDict['stemGradCheckboxes']
                exclude_from_aor_default = False
            else:
                exclude_from_aor_default = True
                stemfields = []

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
            if not (exclude_from_year_default and exclude_from_aor_default and exclude_from_sc_default and
                    exclude_from_ut_default and exclude_from_ms_default and exclude_from_major_default):
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

                    if mentorshipStatus != []:
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

                    if studentCategories:
                        for cat in studentCategories:
                            if (cat == 'First generation college-student') and (categories.first_gen_college_student == False):
                                exclude_from_sc = True
                            elif (cat == 'Low-income') and (categories.low_income == False):
                                exclude_from_sc = True
                            elif (cat == 'Underrepresented racial/ethnic minority') and \
                                    (categories.under_represented_racial_ethnic == False):
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

                    if exclude_from_aor and exclude_from_year and exclude_from_sc and exclude_from_ut \
                            and exclude_from_ms and exclude_from_major:
                        allies_list = allies_list.exclude(id=ally.id)
            for ally in allies_list:
                if not ally.user.is_active:
                    allies_list = allies_list.exclude(id=ally.id)
            return render(request, 'sap/dashboard.html', {'allies_list': allies_list})


class MentorsListView(generic.ListView):
    """Enter what this class/method does"""
    template_name = 'sap/dashboard_ally.html'
    context_object_name = 'allies_list'

    def get(self, request):
        """Enter what this class/method does"""
        allies_list = Ally.objects.order_by('-id')
        for ally in allies_list:
            if not ally.user.is_active:
                allies_list = allies_list.exclude(id=ally.id)
        return render(request, 'sap/dashboard_ally.html', {'allies_list': allies_list})

    def post(self, request):
        """Enter what this class/method does"""
        if request.POST.get("form_type") == 'filters':
            postDict = dict(request.POST)
            if 'stemGradCheckboxes' in postDict:
                stemfields = postDict['stemGradCheckboxes']
                exclude_from_aor_default = False
            else:
                exclude_from_aor_default = True
                stemfields = []
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
    """Enter what this class/method does"""
    template_name = "sap/analytics.html"

    @staticmethod
    def clean_undergrad_dic(undergrad_dic):
        """Enter what this class/method does"""
        years = []
        numbers = []
        if undergrad_dic != {}:
            for key in sorted(undergrad_dic, reverse=True):
                years.append(int(key))
                numbers.append(undergrad_dic[key])
        return years, numbers

    @staticmethod
    def clean_other_dic(other_dic):
        """Enter what this class/method does"""
        years = []
        numbers = [[], [], []]
        if other_dic != {}:
            for key in sorted(other_dic, reverse=True):
                years.append(int(key))
                for i in range(0, 3):
                    numbers[i].append(other_dic[key][i])
        return years, numbers

    @staticmethod
    def yearHelper(ally):
        """Enter what this class/method does"""
        user = ally.user
        joined = user.date_joined
        joined = datetime.datetime.strftime(joined, '%Y')
        return joined

    @staticmethod
    def find_years(allies):
        """Enter what this class/method does"""
        year_and_number = {}
        undergrad_number = {}
        for ally in allies:
            joined = AnalyticsView.yearHelper(ally)
            if ally.user_type != 'Undergraduate Student':
                year_and_number[joined] = [0, 0, 0]  # Staff,Grad,Faculty
            else:
                undergrad_number[joined] = 0  # num undergrad in a particular year
        return year_and_number, undergrad_number

    @staticmethod
    def user_type_per_year(allies, year_and_number, undergrad_number):
        """Enter what this class/method does"""
        for ally in allies:
            joined = AnalyticsView.yearHelper(ally)
            if ally.user_type == 'Staff':
                year_and_number[joined][0] += 1
            elif ally.user_type == 'Graduate Student':
                year_and_number[joined][1] += 1
            elif ally.user_type == 'Undergraduate Student':
                undergrad_number[joined] += 1
            elif ally.user_type == 'Faculty':
                year_and_number[joined][2] += 1
        return year_and_number, undergrad_number

    @staticmethod
    def find_the_categories(allies, relation, categories):
        """Enter what this class/method does"""
        categories_list = []
        for ally in allies:
            category_relation = relation.filter(ally_id=ally.id)
            if category_relation.exists():
                category = categories.filter(id=category_relation[0].student_category_id)
                if category.exists():
                    categories_list.append(category[0])
        return categories_list

    @staticmethod
    def determine_num_per_category(category_list):
        """
        Docstring here
        """
        perCategory = [0, 0, 0, 0, 0, 0, 0]  # lbtq,minorities,rural,disabled,firstGen,transfer,lowIncome
        for category in category_list:
            if category.lgbtq:
                perCategory[0] += 1
            if category.under_represented_racial_ethnic:
                perCategory[1] += 1
            if category.rural:
                perCategory[2] += 1
            if category.disabled:
                perCategory[3] += 1
            if category.first_gen_college_student:
                perCategory[4] += 1
            if category.transfer_student:
                perCategory[5] += 1
            if category.low_income:
                perCategory[6] += 1
        return perCategory

    @staticmethod
    def undergrad_per_year(allies):
        """
        @param allies:
        @return:
        """
        per_category = [0, 0, 0, 0]  # Freshman,Sophmore,Junior,Senior
        for ally in allies:
            if ally.year == "Freshman":
                per_category[0] += 1
            if ally.year == "Sophomore":
                per_category[1] += 1
            if ally.year == "Junior":
                per_category[2] += 1
            if ally.year == "Senior":
                per_category[3] += 1

        return per_category

    def get(self, request):
        """Enter what this class/method does"""
        allies = Ally.objects.all()

        if len(allies) != 0:
            categories = StudentCategories.objects.all()
            relation = AllyStudentCategoryRelation.objects.all()

            other_year, undergrad_year = AnalyticsView.find_years(allies)
            other_joined_per_year, undergrad_joined_per_year = AnalyticsView.user_type_per_year(allies, other_year, undergrad_year)
            undergrad_years, undergrad_numbers = AnalyticsView.clean_undergrad_dic(undergrad_joined_per_year)
            other_years, other_numbers = AnalyticsView.clean_other_dic(other_joined_per_year)

            students = allies.filter(user_type="Undergraduate Student")
            mentors = allies.filter(~Q(user_type="Undergraduate Student"))

            student_categories = AnalyticsView.find_the_categories(students, relation, categories)
            mentor_categories = AnalyticsView.find_the_categories(mentors, relation, categories)

            num_student_categories = AnalyticsView.determine_num_per_category(student_categories)
            num_mentor_categories = AnalyticsView.determine_num_per_category(mentor_categories)

            num_undergrad_per_year = AnalyticsView.undergrad_per_year(students)

            return render(request, 'sap/analytics.html', {"numStudentCategories": num_student_categories,
                                                          "numMentorCategories": num_mentor_categories,
                                                          "numUndergradPerYear": num_undergrad_per_year,
                                                          "undergradYears": undergrad_years,
                                                          "undergradNumbers": undergrad_numbers,
                                                          "otherYears": other_years,
                                                          "staffNumbers": other_numbers[0],
                                                          "gradNumbers": other_numbers[1],
                                                          "facultyNumbers": other_numbers[2], })
        else:
            messages.error(request, "No allies to display!")
            return redirect('sap:sap-dashboard')


class AdminProfileView(TemplateView):
    """Enter what this class/method does"""
    template_name = "sap/profile.html"


class AboutPageView(TemplateView):
    """Enter what this class/method does"""
    template_name = "sap/about.html"


class ResourcesView(TemplateView):
    """Enter what this class/method does"""
    template_name = "sap/resources.html"


class SupportPageView(TemplateView):
    """Enter what this class/method does"""
    template_name = "sap/support.html"


class CreateAdminView(AccessMixin, TemplateView):
    """Enter what this class/method does"""
    template_name = "sap/create_iba_admin.html"

    def get(self, request):
        """Enter what this class/method does"""
        return render(request, self.template_name)

    def post(self, request):
        """Enter what this class/method does"""
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


class CreateEventView(AccessMixin, TemplateView):
    """Enter what this class/method does"""
    template_name = "sap/create_event.html"

    def get(self, request):
        """Enter what this class/method does"""
        if request.user.is_staff:
            return render(request, self.template_name)
        else:
            return redirect('sap:resources')

    def post(self, request):
        """Enter what this class/method does"""
        new_event_dict = dict(request.POST)
        event_title = new_event_dict['event_title'][0]
        event_description = new_event_dict['event_description'][0]
        event_start_time = new_event_dict['event_start_time'][0]
        event_end_time = new_event_dict['event_end_time'][0]
        event_location = new_event_dict['event_location'][0]

        allies_list = Ally.objects.order_by('-id')
        for ally in allies_list:
            if not ally.user.is_active:
                allies_list = allies_list.exclude(id=ally.id)

        allies_list = list(allies_list)

        if 'role_selected' in new_event_dict:
            invite_ally_user_types = new_event_dict['role_selected']
        else:
            invite_ally_user_types = []

        if 'school_year_selected' in new_event_dict:
            invite_ally_school_years = new_event_dict['school_year_selected']
        else:
            invite_ally_school_years = []

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

        if 'event_allday' in new_event_dict:
            allday = True

        else:
            allday = False

        if event_end_time < event_start_time:
            messages.warning(request, 'End time cannot be less than start time!')
            return redirect('/create_event')

        else:
            event = Event.objects.create(title=event_title,
                                         description=event_description,
                                         start_time=parse_datetime(event_start_time + '-0500'),
                                         # converting time to central time before storing in db
                                         end_time=parse_datetime(event_end_time + '-0500'),
                                         location=event_location,
                                         allday=allday,
                                         )

            if invite_all_selected:
                # If all allies are invited
                # TODO: only invite active allies
                allies_to_be_invited = allies_list

            else:
                allies_to_be_invited = []

            allies_to_be_invited.extend(Ally.objects.filter(user_type__in=invite_ally_user_types))
            allies_to_be_invited.extend(Ally.objects.filter(year__in=invite_ally_school_years))

            if 'Mentors' in invite_mentor_mentee:
                allies_to_be_invited.extend(Ally.objects.filter(interested_in_mentoring=True))

            if 'Mentees' in invite_mentor_mentee:
                allies_to_be_invited.extend(Ally.objects.filter(interested_in_mentor_training=True))

            allies_to_be_invited.extend(Ally.objects.filter(area_of_research__in=invite_ally_belonging_to_research_area))
            student_categories_to_include_for_event = []

            for category in invite_ally_belonging_to_special_categories:
                if category == 'First generation college-student':
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

            invited_allies_ids = AllyStudentCategoryRelation.objects.filter(student_category__in=
                                                                            student_categories_to_include_for_event).values('ally')
            allies_to_be_invited.extend(
                Ally.objects.filter(id__in=invited_allies_ids)
            )

            all_event_ally_objs = []
            invited_allies = set()
            allies_to_be_invited = set(allies_to_be_invited)

            for ally in allies_to_be_invited:
                if ally.user.is_active:
                    event_ally_rel_obj = EventInviteeRelation(event=event, ally=ally)
                    all_event_ally_objs.append(event_ally_rel_obj)
                    invited_allies.add(event_ally_rel_obj.ally)

            EventInviteeRelation.objects.bulk_create(all_event_ally_objs)

            messages.success(request, "Event successfully created!")
            return redirect('/calendar')


class RegisterEventView(TemplateView):
    """
    Register for event.
    """

    def get(self, request, *args, **kwargs):
        """Enter what this class/method does"""
        # # TODO: Update this function once frontend gets done
        # user_current = request.user
        # ally_current = Ally.objects.get(user=user_current)
        # event_id = 1
        #
        # if ally_current is not None and user_current.is_active:
        #     AllyStudentCategoryRelation.objects.create(event_id=event.id,
        #                                                ally_id=ally_current.id)
        #     messages.success(request,
        #                      'You have successfully register for this event!')
        #
        # else:
        #     messages.warning(request,
        #                      'You cannot register for this event.')
        pass


class DeregisterEventView(TemplateView):
    """Enter what this class/method does"""
    def get(self, request, *args, **kwargs):
        """Enter what this class/method does"""
        # template =
        pass


class SignUpView(TemplateView):
    """Enter what this class/method does"""
    template_name = "sap/sign-up.html"

    def make_categories(self, student_categories):
        """Enter what this class/method does"""

        categories = StudentCategories.objects.create()
        for category_id in student_categories:
            if category_id == 'First generation college-student':
                categories.first_gen_college_student = True
            elif category_id == 'Low-income':
                categories.low_income = True
            elif category_id == 'Underrepresented racial/ethnic minority':
                categories.under_represented_racial_ethnic = True
            elif category_id == 'LGBTQ':
                categories.lgbtq = True
            elif category_id == 'Rural':
                categories.rural = True
            elif category_id == 'Disabled':
                categories.disabled = True
        categories.save()
        return categories

    def set_boolean(self, _list, post_dict):
        """Enter what this class/method does"""
        dictionary = {}
        for selection in _list:
            if post_dict[selection][0] == 'Yes':
                dictionary[selection] = True
            else:
                dictionary[selection] = False
        return dictionary

    def create_new_user(self, post_dict):
        """
        Create new user and associated ally based on what user inputs in sign-up page
        """
        user = User.objects.create_user(username=post_dict["new_username"][0],
                                        password=post_dict["new_password"][0],
                                        email=post_dict["new_email"][0],
                                        first_name=post_dict["firstName"][0],
                                        last_name=post_dict["lastName"][0],
                                        is_active=False  # Important! Set to False until user verify via email
                                        )

        if post_dict['roleSelected'][0] == 'Staff':
            selections = self.set_boolean(['studentsInterestedRadios'], post_dict)
            ally = Ally.objects.create(user=user,
                                       user_type=post_dict['roleSelected'][0],
                                       hawk_id=user.username,
                                       people_who_might_be_interested_in_iba=selections['studentsInterestedRadios'],
                                       how_can_science_ally_serve_you=post_dict['howCanWeHelp'])
        else:
            if post_dict['roleSelected'][0] == 'Undergraduate Student':
                try:
                    categories = self.make_categories(post_dict["idUnderGradCheckboxes"])
                except KeyError:
                    categories = StudentCategories.objects.create()
                undergrad_list = ['interestRadios', 'experienceRadios', 'interestedRadios',
                                 'agreementRadios', 'beingMentoredRadios']
                selections = self.set_boolean(undergrad_list, post_dict)
                ally = Ally.objects.create(user=user,
                                           user_type=post_dict['roleSelected'][0],
                                           hawk_id=user.username,
                                           major=post_dict['major'][0],
                                           year=post_dict['undergradRadios'][0],
                                           interested_in_joining_lab=selections['interestRadios'],
                                           has_lab_experience=selections['experienceRadios'],
                                           interested_in_mentoring=selections['interestedRadios'],
                                           information_release=selections['agreementRadios'])
            elif post_dict['roleSelected'][0] == 'Graduate Student':
                try:
                    stem_fields = ','.join(post_dict['stemGradCheckboxes'])
                except KeyError:
                    stem_fields = None
                try:
                    categories = self.make_categories(post_dict['mentoringGradCheckboxes'])
                except KeyError:
                    categories = StudentCategories.objects.create()

                grad_list = ['mentoringGradRadios', 'labShadowRadios', 'connectingRadios', 'volunteerGradRadios',
                            'gradTrainingRadios']
                selections = self.set_boolean(grad_list, post_dict)
                ally = Ally.objects.create(user=user,
                                           user_type=post_dict['roleSelected'][0],
                                           hawk_id=user.username,
                                           area_of_research=stem_fields,
                                           interested_in_mentoring=selections['mentoringGradRadios'],
                                           willing_to_offer_lab_shadowing=selections['labShadowRadios'],
                                           interested_in_connecting_with_other_mentors=selections['connectingRadios'],
                                           willing_to_volunteer_for_events=selections['volunteerGradRadios'],
                                           interested_in_mentor_training=selections['gradTrainingRadios'])

            elif post_dict['roleSelected'][0] == 'Faculty':
                try:
                    stem_fields = ','.join(post_dict['stemCheckboxes'])
                except KeyError:
                    stem_fields = None
                faculty_list = ['openingRadios', 'volunteerRadios', 'trainingRadios', 'mentoringFacultyRadios']
                selections = self.set_boolean(faculty_list, post_dict)
                try:
                    categories = self.make_categories(post_dict['mentoringCheckboxes'])
                except KeyError:
                    categories = StudentCategories.objects.create()
                ally = Ally.objects.create(user=user,
                                           user_type=post_dict['roleSelected'][0],
                                           hawk_id=user.username,
                                           area_of_research=stem_fields,
                                           openings_in_lab_serving_at=selections['openingRadios'],
                                           description_of_research_done_at_lab=post_dict['research-des'][0],
                                           interested_in_mentoring=selections['mentoringFacultyRadios'],
                                           willing_to_volunteer_for_events=selections['volunteerRadios'],
                                           interested_in_mentor_training=selections['trainingRadios'])

            AllyStudentCategoryRelation.objects.create(student_category_id=categories.id, ally_id=ally.id)

        return user, ally

    def send_verification_email(self, user, site, entered_email):
        """
        Send verification email to finish sign-up, basically set is_active to True
        """
        _ = self.__doc__
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
            sendgrid_obj = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            sendgrid_obj.send(email_content)

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
        post_dict = dict(request.POST)

        min_length = 8  # Minimum length for a valid password

        if User.objects.filter(email=post_dict["new_email"][0]).exists():
            user_temp = User.objects.get(email=post_dict["new_email"][0])

            if user_temp.is_active:  # If user is active, cannot create new account
                messages.warning(request,
                                 'Account can not be created because an account associated with this email address already exists!')
                return redirect('/sign-up')

            else:  # If user is not active, delete user_temp and create new user on db with is_active=False

                ally_temp = Ally.objects.filter(user=user_temp)
                if ally_temp.exists():
                    ally_temp[0].delete()
                user_temp.delete()

                # print(request.POST)
                if User.objects.filter(username=post_dict["new_username"][0]).exists():
                    messages.warning(request,
                                     'Account can not be created because username already exists!')
                    return redirect('/sign-up')
                # elif User.objects.filter(email=postDict["new_email"][0]).exists():
                #     messages.add_message(request, messages.WARNING,
                #                          'Account can not be created because email already exists')
                #     return redirect('/sign-up')
                elif post_dict["new_password"][0] != post_dict["repeat_password"][0]:
                    messages.warning(request,
                                     "Repeated password is not the same as the inputted password!", )
                    return redirect("/sign-up")
                elif len(post_dict["new_password"][0]) < min_length:
                    messages.warning(request,
                                     "Password must be at least {0} characters long".format(min_length), )
                    return redirect("/sign-up")
                else:
                    user, _ = self.create_new_user(post_dict=post_dict)
                    site = get_current_site(request)
                    self.send_verification_email(user=user, site=site, entered_email=post_dict["new_email"][0])

                    return redirect("sap:sign-up-done")

        elif not User.objects.filter(email=post_dict["new_email"][0]).exists():
            if User.objects.filter(username=post_dict["new_username"][0]).exists():
                messages.warning(request,
                                 'Account can not be created because username already exists!')
                return redirect('/sign-up')
            # elif User.objects.filter(email=postDict["new_email"][0]).exists():
            #     messages.add_message(request, messages.WARNING,
            #                          'Account can not be created because email already exists')
            #     return redirect('/sign-up')
            elif post_dict["new_password"][0] != post_dict["repeat_password"][0]:
                messages.warning(request,
                                 "Repeated password is not the same as the inputted password!")
                return redirect("/sign-up")
            elif len(post_dict["new_password"][0]) < min_length:
                messages.warning(request,
                                 "Password must be at least {0} characters long".format(min_length))
                return redirect("/sign-up")
            else:
                user, ally = self.create_new_user(post_dict=post_dict)
                site = get_current_site(request)
                self.send_verification_email(user=user, site=site, entered_email=post_dict["new_email"][0])

                return redirect("sap:sign-up-done")


class SignUpDoneView(TemplateView):
    """
    A view which is presented if the user successfully fill out the form presented in Sign-Up view
    """
    template_name = "sap/sign-up-done.html"

    def get(self, request, *args, **kwargs):
        """Enter what this class/method does"""
        site = get_current_site(request)
        accepted_origin = 'http:' + '//' + site.domain + reverse('sap:sign-up')

        try:
            origin = request.headers['Referer']

            if request.headers['Referer'] and origin == accepted_origin:
                return render(request, self.template_name)
            elif request.user.is_authenticated:
                return redirect('sap:resources')
            else:
                return redirect('sap:home')

        except KeyError:
            if request.user.is_authenticated:
                return redirect('sap:resources')
            else:
                return redirect('sap:home')


class SignUpConfirmView(TemplateView):
    """
    Only for those who click on verification email during sign-up.
    No POST method.
    """

    def get(self, request, *args, **kwargs):
        """Enter what this class/method does"""
        path = request.path
        path_1, token = os.path.split(path)
        _, uidb64 = os.path.split(path_1)

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            messages.warning(request, str(e))
            user = None

        if user is not None and user.is_active:
            messages.success(request, 'Account already verified.')
            return redirect('sap:home')

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True  # activates the user
            user.save()
            messages.success(request, 'Account successfully created! You can now log in with your new account.')
            return redirect('sap:home')

        messages.error(request, 'Invalid account activation link.')
        return redirect('sap:home')


class ForgotPasswordView(TemplateView):
    """
    A view which allows users to reset their password in case they forget it.
    Send a confirmation emails with unique token
    """

    # template_name = "sap/password-forgot.html"

    def get(self, request, *args, **kwargs):
        """Enter what this class/method does"""
        form = PasswordResetForm(request.GET)
        return render(request, 'sap/password-forgot.html', {'form': form})

    def post(self, request):
        """Enter what this class/method does"""
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
                    from_email="iba@uiowa.edu",
                    to_emails=entered_email,
                    subject='Reset Password for Science Alliance Portal',
                    html_content=message_body)

                try:
                    # TODO: Change API key and invalidate the old one
                    sendgrid_obj = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                    sendgrid_obj.send(email_content)
                except Exception:
                    #print(e)
                    pass

                return redirect('/password-forgot-done')

            return redirect('/password-forgot-done')
            # return render(request, 'account/password-forgot.html', {'form': form})

        return render(request, 'sap/password-forgot.html', {'form': form})


class ForgotPasswordDoneView(TemplateView):
    """
    A view which is presented if the user entered valid email in Forget Password view
    """
    template_name = "sap/password-forgot-done.html"

    def get(self, request, *args, **kwargs):
        """Enter what this class/method does"""
        site = get_current_site(request)
        accepted_origin = 'http:' + '//' + site.domain + reverse('sap:password-forgot')

        try:
            origin = request.headers['Referer']

            if request.headers['Referer'] and origin == accepted_origin:
                return render(request, self.template_name)

            if request.user.is_authenticated:
                return redirect('sap:resources')

            return redirect('sap:home')

        except KeyError:
            if request.user.is_authenticated:
                return redirect('sap:resources')
            else:
                return redirect('sap:home')


class ForgotPasswordConfirmView(TemplateView):
    """
    A unique view to users who click to the reset forgot passwork link.
    Allow them to create new password.
    """

    # template_name = "sap/password-forgot-confirm.html"
    def get(self, request, *args, **kwargs):
        """Enter what this class/method does"""
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
        """Enter what this class/method does"""
        path = request.path
        path_1, token = os.path.split(path)
        path_0, uidb64 = os.path.split(path_1)

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exception:
            messages.warning(request, str(exception))
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

            # else part
            context = {
                'form': UserResetForgotPasswordForm(user),
                'uid': uidb64,
                'token': token
            }
            messages.error(request, 'Password does not meet requirements.')
            return render(request, 'sap/password-forgot-confirm.html', context)

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
    """Enter what this class/method does"""

    @staticmethod
    def fields_helper(model, columns):
        """Enter what this class/method does"""
        for field in model._meta.get_fields():
            fields = str(field).split(".")[-1]
            if fields in userFields or fields in allyFields or fields in categoryFields:
                columns.append(fields)
        return columns

    @staticmethod
    def cleanup(dictionary):
        """Enter what this class/method does"""
        ar_list = []
        for item in dictionary.items():
            if item[0] in userFields or item[0] in allyFields or item[0] in categoryFields:
                if item[0] == 'date_joined':
                    ar_list.append(item[1].strftime("%b-%d-%Y"))
                else:
                    ar_list.append(item[1])
        return ar_list

    @staticmethod
    def get_data():
        """Enter what this class/method does"""
        users = User.objects.all()
        allies = Ally.objects.all()
        categories = StudentCategories.objects.all()
        category_relation = AllyStudentCategoryRelation.objects.all()

        data = []
        for ally in allies:
            user_id = ally.user_id
            ally_id = ally.id

            category = category_relation.filter(ally_id=ally_id)
            if category.exists():
                category_id = category[0].student_category_id
                tmp = DownloadAllies.cleanup(users.filter(id=user_id)[0].__dict__) + DownloadAllies.cleanup(ally.__dict__) + \
                      DownloadAllies.cleanup(categories.filter(id=category_id)[0].__dict__)
            else:
                tmp = DownloadAllies.cleanup(users.filter(id=user_id)[0].__dict__) + DownloadAllies.cleanup(ally.__dict__) + \
                      [None, None, None, None, None, None, None]
            data.append(tmp)
        return data

    @staticmethod
    def allies_download(request):
        """Enter what this class/method does"""
        if request.user.is_staff:
            response = HttpResponse(content_type='text/csv')
            today = date.today()
            today = today.strftime("%b-%d-%Y")
            file_name = today + "_ScienceAllianceAllies.csv"
            response['Content-Disposition'] = 'attachment; filename=' + file_name
            columns = []
            columns = DownloadAllies.fields_helper(User, columns)
            columns = DownloadAllies.fields_helper(Ally, columns)
            columns = DownloadAllies.fields_helper(StudentCategories, columns)
            data = DownloadAllies.get_data()
            writer = csv.writer(response)
            writer.writerow(columns)
            writer.writerows(data)
            return response

        return HttpResponseForbidden()


boolFields = ['Do you currently have openings for undergraduate students in your lab?',
              'Would you be willing to offer lab shadowing to potential students?',
              'Are you interested in mentoring students?',
              'Are you interested in connecting with other mentors?',
              'Would you be willing to volunteer for panels, networking workshops, and other ' + \
              'events as professional development for students?',
              'Are you interested in mentor training?',
              'Do you know students who would be interested in the Science Alliance?',
              'Are you interested in joining a lab?',
              'Do you have experience working in a laboratory?',
              'Are you interested in becoming a peer mentor?']


class UploadAllies(AccessMixin, HttpResponse):
    """Enter what this class/method does"""

    @staticmethod
    def cleanup_frame(data_frame):
        """Enter what this class/method does"""
        errorlog = {}
        try:
            data_frame = data_frame.drop(['Workflow ID', 'Status', 'Name'], axis=1)
        except KeyError:
            errorlog[1000] = "Could not drop unnecessary columns \'Workflow ID\', \'Status\', \'Name\'"
        try:
            data_frame1 = pd.DataFrame({"Name": data_frame['Initiator']})
        except KeyError:
            errorlog[2000] = "CRITICAL ERROR: The \'Initiator\' column is not present, cannot proceed"
            return data_frame, errorlog
        try:
            data_frame2 = data_frame1.applymap(lambda x: x.split('\n'))
            data_frame2 = data_frame2.applymap(lambda x: x[0] + x[1])
            data_frame2 = data_frame2.replace(regex=['\d'], value='')
            data_frame2 = data_frame2['Name'].str.split(', ', n=1, expand=True)
            data_frame2 = data_frame2.rename({0: 'last_name', 1: 'first_name'}, axis=1)
            data_frame = data_frame.join(data_frame2)
            data_frame['email'] = data_frame['Initiator'].str.extract(r'(.*@uiowa.edu)')
            data_frame = data_frame.drop(['Initiator'], axis=1)
        except Exception:
            errorlog[3000] = "CRITICAL ERROR: data could not be extracted from \'Initiator\' column " \
                             "and added as columns"
            return data_frame, errorlog
        try:
            data_frame[boolFields] = data_frame[boolFields].fillna(value=False)
            data_frame[boolFields] = data_frame[boolFields].replace('Yes (Yes)', True)
            data_frame[boolFields] = data_frame[boolFields].replace('No (No)', False)
            data_frame['interested_in_mentoring'] = False
            for i in range(0, len(data_frame)):
                data_frame['interested_in_mentoring'][i] = data_frame['Are you interested in becoming a peer mentor?'][i] or \
                                                   data_frame['Are you interested in mentoring students?'][i]
            data_frame = data_frame.drop(['Are you interested in becoming a peer mentor?',
                          'Are you interested in mentoring students?'], axis=1)
            data_frame = data_frame.rename({
                'Do you currently have openings for undergraduate students in your lab?': 'openings_in_lab_serving_at',
                'Would you be willing to offer lab shadowing to potential students?': 'willing_to_offer_lab_shadowing',
                'Are you interested in connecting with other mentors?': 'interested_in_connecting_with_other_mentors',
                'Would you be willing to volunteer for panels, networking workshops, and other events as professional ' +
                'development for students?': 'willing_to_volunteer_for_events',
                'Are you interested in mentor training?': 'interested_in_mentor_training',
                'Do you know students who would be interested in the Science Alliance?': 'people_who_might_be_interested_in_iba',
                'Are you interested in joining a lab?': 'interested_in_joining_lab',
                'Do you have experience working in a laboratory?': 'has_lab_experience'
            }, axis=1)
        except KeyError:
            errorlog[4000] = "CRITICAL ERROR: boolean could not replace blanks. Ensure the following are present:" + \
                             str(boolFields)
            return data_frame, errorlog
        try:
            data_frame = data_frame.fillna(value='')
            data_frame['STEM Area of Research'] = data_frame['STEM Area of Research'].replace(regex=[r'\n'], value=',')
            data_frame['STEM Area of Research'] = data_frame['STEM Area of Research'].replace(regex=[r'\s\([^)]*\)'], value='')
            data_frame['University Type'] = data_frame['University Type'].replace(regex=[r'\s\([^)]*\)', '/Post-doc'], value='')
            data_frame['Year'] = data_frame['Year'].replace(regex=r'\s\([^)]*\)', value='')
            data_frame = data_frame.rename({'STEM Area of Research': 'area_of_research',
                            'University Type': 'user_type',
                            'Please provide a short description of the type of research done by undergrads':
                                'description_of_research_done_at_lab',
                            'Year': 'year', 'Major': 'major',
                            'How can the Science Alliance serve you?': 'how_can_science_ally_serve_you'},
                           axis=1)
        except KeyError:
            errorlog[5000] = "CRITICAL ERROR: problem in tidying charfield columns. ensure the following is present:" \
                             "STEM Area of Research, University Type, Please provide a short description of the type " \
                             "of research done by undergrads, " \
                             "Year, Major"
            return data_frame, errorlog
        try:
            data_frame['Submission Date'] = data_frame['Submission Date'].map(lambda x: x.strftime("%b-%d-%Y"))
            data_frame = data_frame.rename({'Submission Date': 'date_joined'}, axis=1)
        except KeyError:
            errorlog[6000] = "CRITICAL ERROR: problem converting timestamp to date, please ensure Submission Date is a column"
            return data_frame, errorlog
        try:
            data_frame['username'] = ''
            for i in range(0, len(data_frame)):
                hawkid = data_frame['first_name'][i][0] + data_frame['last_name'][i]
                data_frame['username'][i] = hawkid.lower()
        except Exception as e:
            errorlog[7000] = "CRITICAL ERROR: Could not convert first name and last name to hawkid. Please Ensure the " \
                             "Initiator is present"
            return data_frame, errorlog
        data_frame['information_release'] = False
        data_frame['interested_in_being_mentored'] = False
        data_frame['is_active'] = True
        data_frame['works_at'] = ''
        data_frame['last_login'] = ''
        data_frame[categoryFields] = False
        try:
            # pd.set_option('display.max_columns', 100)
            for i in range(0, len(data_frame)):
                tmp = data_frame['Are you interested in serving as a mentor to students who identify as any ' \
                         'of the following (check all that may apply)'][i]
                if 'First generation college-student' in tmp:
                    data_frame['first_gen_college_student'][i] = True
                if 'LGBTQ' in tmp:
                    data_frame['lgbtq'][i] = True
                if 'Transfer student' in tmp:
                    data_frame['transfer_student'][i] = True
                if 'Underrepresented racial/ethnic minority' in tmp:
                    data_frame['under_represented_racial_ethnic'][i] = True
            data_frame = data_frame.drop(['Are you interested in serving as a mentor to students who identify as any of the following '
                          '(check all that may apply)'], axis=1)
        except Exception:
            errorlog[8000] = "Possible data error: willing to mentor may be inaccurate. Please ensure the column: " \
                             "\'Are you interested in serving as a mentor to students who identify as any of the following " \
                             "(check all that may apply)\'" \
                             " is present"
        return data_frame, errorlog

    @staticmethod
    def make_allies_from_data_frame(data_frame, error_log):
        """Enter what this class/method does"""
        password_log = {}
        ally_data = {}
        user_data = {}
        category_data = {}
        try:
            ally_data = data_frame[allyFields].to_dict('index')
            user_data = data_frame[userFields].to_dict('index')
            category_data = data_frame[categoryFields].to_dict('index')
        except KeyError:
            error_log[9000] = "CRITICAL ERROR: Data does not contain necessary columns. Please ensure that the data has columns:\n" + \
                              str(userFields + allyFields + categoryFields)
        for ally in ally_data.items():
            if ("Staff" == ally[1]['user_type'] or ally[1]['user_type'] == "Graduate Student"
                    or ally[1]['user_type'] == "Undergraduate Student" or ally[1]['user_type'] == 'Faculty'):
                password = uuid.uuid4().hex[0:9]
                user = user_data[ally[0]]
                try:
                    time = datetime.datetime.strptime(user['date_joined'], '%b-%d-%Y')
                    # time = datetime.strptime(user['date_joined'], "%Y-%m-%d")
                    user = User.objects.create_user(username=user['username'], password=password, email=user['email'],
                                                    first_name=user['first_name'], last_name=user['last_name'],
                                                    date_joined=time)
                    password_log[ally[0]] = password
                    try:
                        ally1 = Ally.objects.create(user=user, user_type=ally[1]['user_type'], hawk_id=user.username,
                                                    area_of_research=ally[1]['area_of_research'],
                                                    interested_in_mentoring=ally[1]['interested_in_mentoring'],
                                                    willing_to_offer_lab_shadowing=ally[1]['willing_to_offer_lab_shadowing'],
                                                    interested_in_connecting_with_other_mentors=ally[1][
                                                        'interested_in_connecting_with_other_mentors'],
                                                    willing_to_volunteer_for_events=ally[1]['willing_to_volunteer_for_events'],
                                                    interested_in_mentor_training=ally[1]['interested_in_mentor_training'],
                                                    major=ally[1]['major'], information_release=ally[1]['information_release'],
                                                    has_lab_experience=ally[1]['has_lab_experience'],
                                                    year=ally[1]['year'], interested_in_being_mentored=ally[1]
                            ['interested_in_being_mentored'],
                                                    description_of_research_done_at_lab=ally[1]['description_of_research_done_at_lab'],
                                                    interested_in_joining_lab=ally[1]['interested_in_joining_lab'],
                                                    openings_in_lab_serving_at=ally[1]['openings_in_lab_serving_at'],
                                                    people_who_might_be_interested_in_iba=ally[1]['people_who_might_be_interested_in_iba'],
                                                    how_can_science_ally_serve_you=ally[1]['how_can_science_ally_serve_you'],
                                                    works_at=ally[1]['works_at'])
                        if not ally[1]['user_type'] == "Staff":
                            category = category_data[ally[0]]
                            categories = StudentCategories.objects.create(rural=category['rural'],
                                                                          transfer_student=category['transfer_student'],
                                                                          lgbtq=category['lgbtq'],
                                                                          low_income=category['low_income'],
                                                                          first_gen_college_student=category['first_gen_college_student'],
                                                                          under_represented_racial_ethnic=category
                                                                          ['under_represented_racial_ethnic'],
                                                                          disabled=category['disabled'])
                            AllyStudentCategoryRelation.objects.create(ally_id=ally1.id,
                                                                       student_category_id=categories.id)
                    except IntegrityError:
                        error_log[ally[0]] = "Ally already exists in the database"

                except IntegrityError:
                    error_log[ally[0]] = "user with username: " + user['username'] + " or email: " + user['email'] \
                                         + " already exists in database"
            else:
                error_log[ally[0]] = "Improperly formated -  user_type must be: Staff, Faculty, " \
                                    "Undergraduate Student, or Graduate Student"
        return error_log, password_log

    @staticmethod
    def process_file(file):
        """Enter what this class/method does"""
        error_log = {}
        data_frame = pd.DataFrame()
        try:
            data_frame = pd.read_csv(file)
        except Exception:
            try:
                data_frame = pd.read_excel(file)
            except Exception:
                error_log[900] = "Problem reading file: was it stored in .csv or xlsx?"

        columns = list(data_frame.columns)
        if columns != (userFields + allyFields + categoryFields):
            data_frame, error_log = UploadAllies.cleanup_frame(data_frame)
        else:
            data_frame = data_frame.replace(data_frame.fillna('', inplace=True))
        error_log, password_log = UploadAllies.make_allies_from_data_frame(data_frame, error_log)
        return UploadAllies.make_file(data_frame, error_log, password_log)

    @staticmethod
    def make_file(data_frame, error_log, password_log):
        """Enter what this class/method does"""
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
        for error in error_log.items():
            errors.write(row, column, error[0])
            errors.write(row, column + 1, error[1])
            row += 1
        row = 1
        for password in password_log.items():
            passwords.write(row, column, data_frame['username'][password[0]])
            passwords.write(row, column + 1, data_frame['email'][password[0]])
            passwords.write(row, column + 2, password[1])
            row += 1
        workbook.close()
        output.seek(0)
        return output

    @staticmethod
    def upload_allies(request):
        """Enter what this class/method does"""
        if request.user.is_staff:
            try:
                file = request.FILES['file']
                output = UploadAllies.process_file(file)
                today = date.today()
                today = today.strftime("%b-%d-%Y")
                file_name = today + "_SAP_Upload-log.xlsx"
                response = HttpResponse(
                    output,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename=' + file_name
                return response
            except KeyError:
                messages.add_message(request, messages.ERROR, 'Please select a file to upload!')

            return redirect('sap:sap-dashboard')

        return HttpResponseForbidden()
