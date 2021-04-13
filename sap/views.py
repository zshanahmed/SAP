"""
views has functions that are mapped to the urls in urls.py
"""
import datetime
from fuzzywuzzy import fuzz

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.db.models import Q
from django.views import generic
from django.views.generic import TemplateView, View
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.utils.dateparse import parse_datetime

from .forms import UpdateAdminProfileForm
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


class CustomLoginView(LoginView):

    def get(self, request):
        pass

    def post(self, request):
        pass


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
                if new_username not in ('', user.username):
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

    def get(self, request):
        """Enter what this class/method does"""
        form = PasswordChangeForm(request.user)
        return render(request, 'sap/change_password.html', {
            'form': form
        })

    def post(self, request):
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
        # for announcment in announcments_list:
        #    pass
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
            post_dict = dict(request.POST)
            if 'stemGradCheckboxes' in post_dict:
                stemfields = post_dict['stemGradCheckboxes']
                exclude_from_aor_default = False
            else:
                exclude_from_aor_default = True
                stemfields = []

            if 'undergradYear' in post_dict:
                exclude_from_year_default = False
                undergrad_year = post_dict['undergradYear']
            else:
                exclude_from_year_default = True
                undergrad_year = []

            if 'idUnderGradCheckboxes' in post_dict:
                student_categories = post_dict['idUnderGradCheckboxes']
                exclude_from_sc_default = False
            else:
                exclude_from_sc_default = True
                student_categories = []

            if 'roleSelected' in post_dict:
                user_types = post_dict['roleSelected']
                exclude_from_ut_default = False
            else:
                exclude_from_ut_default = True
                user_types = []

            if 'mentorshipStatus' in post_dict:
                mentorship_status = post_dict['mentorshipStatus'][0]
                exclude_from_ms_default = False
            else:
                exclude_from_ms_default = True
                mentorship_status = []

            major = post_dict['major'][0]
            if major != '':
                exclude_from_major_default = False
            else:
                exclude_from_major_default = True

            allies_list = Ally.objects.order_by('-id')
            if not (
                    exclude_from_year_default and exclude_from_aor_default and exclude_from_sc_default and exclude_from_ut_default
                    and exclude_from_ms_default and exclude_from_major_default):
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
                    if stemfields and (not bool(set(stemfields) & set(aor))):
                        exclude_from_aor = True

                    if mentorship_status != []:
                        if (mentorship_status == 'Mentor') and (ally.interested_in_mentoring is False):
                            exclude_from_ms = True
                        elif (mentorship_status == 'Mentee') and (ally.interested_in_being_mentored is False):
                            exclude_from_ms = True

                    try:
                        categories = AllyStudentCategoryRelation.objects.filter(
                            ally_id=ally.id).values()[0]
                        categories = StudentCategories.objects.filter(
                            id=categories['student_category_id'])[0]
                    except:
                        student_categories = []

                    if student_categories:
                        for cat in student_categories:
                            if (cat == 'First generation college-student') and (categories.first_gen_college_student is False):
                                exclude_from_sc = True
                            elif (cat == 'Low-income') and (categories.low_income is False):
                                exclude_from_sc = True
                            elif (cat == 'Underrepresented racial/ethnic minority') and \
                                    (categories.under_represented_racial_ethnic is False):
                                exclude_from_sc = True
                            elif (cat == 'LGBTQ') and (categories.lgbtq is False):
                                exclude_from_sc = True
                            elif (cat == 'Rural') and (categories.rural is False):
                                exclude_from_sc = True
                            elif (cat == 'Disabled') and (categories.disabled is False):
                                exclude_from_sc = True

                    if undergrad_year and (ally.year not in undergrad_year):
                        exclude_from_year = True

                    if user_types and (ally.user_type not in user_types):
                        exclude_from_ut = True

                    exclude_from_ms_major = exclude_from_ms and exclude_from_major

                    if exclude_from_aor and exclude_from_year and exclude_from_sc and exclude_from_ut \
                            and exclude_from_ms_major:
                        allies_list = allies_list.exclude(id=ally.id)

            for ally in allies_list:
                if not ally.user.is_active:
                    allies_list = allies_list.exclude(id=ally.id)
            return render(request, 'sap/dashboard.html', {'allies_list': allies_list})

        return HttpResponse()


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
            post_dict = dict(request.POST)
            if 'stemGradCheckboxes' in post_dict:
                stemfields = post_dict['stemGradCheckboxes']
                exclude_from_aor_default = False
            else:
                exclude_from_aor_default = True
                stemfields = []
            if 'undergradYear' in post_dict:
                exclude_from_year_default = False
                undergrad_year = post_dict['undergradYear']
            else:
                exclude_from_year_default = True
                undergrad_year = []
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

                    if (undergrad_year) and (ally.year not in undergrad_year):
                        exclude_from_year = True

                    if exclude_from_aor and exclude_from_year:
                        allies_list = allies_list.exclude(id=ally.id)

            for ally in allies_list:
                if not ally.user.is_active:
                    allies_list = allies_list.exclude(id=ally.id)

            return render(request, 'sap/dashboard_ally.html', {'allies_list': allies_list})

        return HttpResponse()


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
    def year_helper(ally):
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
            joined = AnalyticsView.year_helper(ally)
            if ally.user_type != 'Undergraduate Student':
                year_and_number[joined] = [0, 0, 0]  # Staff,Grad,Faculty
            else:
                undergrad_number[joined] = 0  # num undergrad in a particular year
        return year_and_number, undergrad_number

    @staticmethod
    def user_type_per_year(allies, year_and_number, undergrad_number):
        """Enter what this class/method does"""
        for ally in allies:
            joined = AnalyticsView.year_helper(ally)
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
        per_category = [0, 0, 0, 0, 0, 0, 0]  # lbtq,minorities,rural,disabled,firstGen,transfer,lowIncome
        for category in category_list:
            if category.lgbtq:
                per_category[0] += 1
            if category.under_represented_racial_ethnic:
                per_category[1] += 1
            if category.rural:
                per_category[2] += 1
            if category.disabled:
                per_category[3] += 1
            if category.first_gen_college_student:
                per_category[4] += 1
            if category.transfer_student:
                per_category[5] += 1
            if category.low_income:
                per_category[6] += 1
        return per_category

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
        new_admin_dict = dict(request.POST)
        valid = True
        for key in new_admin_dict:
            if new_admin_dict[key][0] == '':
                valid = False
        if valid:
            # Check if username credentials are correct
            if authenticate(request, username=new_admin_dict['current_username'][0],
                            password=new_admin_dict['current_password'][0]) is not None:
                # if are check username exists in database
                if User.objects.filter(username=new_admin_dict['new_username'][0]).exists():
                    messages.add_message(request, messages.ERROR, 'Account was not created because username exists')
                    return redirect('/create_iba_admin')
                # Check if repeated password is same
                if new_admin_dict['new_password'][0] != new_admin_dict['repeat_password'][0]:
                    messages.add_message(request, messages.ERROR, 'New password was not the same as repeated password')
                    return redirect('/create_iba_admin')

                messages.add_message(request, messages.SUCCESS, 'Account Created')
                user = User.objects.create_user(new_admin_dict['new_username'][0],
                                                new_admin_dict['new_email'][0], new_admin_dict['new_password'][0])
                user.is_staff = True
                user.save()
                return redirect('/dashboard')

            messages.add_message(request, messages.ERROR, 'Invalid Credentials entered')
            return redirect('/create_iba_admin')

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

        allday = 'event_allday' in new_event_dict

        if event_end_time < event_start_time:
            messages.warning(request, 'End time cannot be less than start time!')
            return redirect('/create_event')

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
