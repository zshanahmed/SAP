"""
views has functions that are mapped to the urls in urls.py
"""
import datetime
from fuzzywuzzy import fuzz

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import logout, authenticate, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views import generic
from django.views.generic import TemplateView, View
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.utils.dateparse import parse_datetime

from .forms import UpdateAdminProfileForm
from .models import Announcement, EventInviteeRelation, EventAttendeeRelation, Ally, StudentCategories, AllyStudentCategoryRelation, Event

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
    @staticmethod
    def get(request, ally_username=''):
        """
        method to retrieve all ally information
        """
        try:
            user = User.objects.get(username=ally_username)
            ally = Ally.objects.get(user=user)
            return render(request, 'sap/admin_ally_table/view_ally.html', {
                'ally': ally
            })
        except ObjectDoesNotExist:
            return HttpResponseNotFound()


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
                created_at=datetime.datetime.utcnow()
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
        """
        This function gets all the events to be shown on Calendar
        """
        events_list = []
        curr_user = request.user
        if not curr_user.is_staff:
            curr_ally = Ally.objects.get(user_id=curr_user.id)
            curr_events = EventInviteeRelation.objects.filter(ally_id=curr_ally.id)
            for event in curr_events:
                events_list.append(Event.objects.get(id=event.event_id))
        else:
            events_list = Event.objects.all()
            for event in events_list:
                event.num_invited = EventInviteeRelation.objects.filter(event_id=event.id).count()
                event.num_attending = EventAttendeeRelation.objects.filter(event_id=event.id).count()
                event.save()
        events = serializers.serialize('json', events_list)
        return render(request, 'sap/calendar.html',
                      context={
                          "events": events,
                          "user": curr_user
                      })


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
        for announcment in announcments_list:
            announcment.created_at = announcment.created_at.strftime(
                "%m/%d/%Y, %I:%M %p")
        return render(request, 'sap/announcements.html', {'announcments_list': announcments_list, 'role': role})


class AlliesListView(AccessMixin, TemplateView):
    """Enter what this class/method does"""

    def get(self, request):
        """Renders the dashboard with the allies and categories as django template variables."""
        allies_list = Ally.objects.order_by('-id')
        for ally in allies_list:
            if not ally.user.is_active:
                allies_list = allies_list.exclude(id=ally.id)
        return render(request, 'sap/dashboard.html', {'allies_list': allies_list})

    def post(self, request):
        """Filters and returns allies based on selected criteria"""
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
                    except KeyError:
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
        """Returns a view of allies"""
        allies_list = Ally.objects.order_by('-id')
        for ally in allies_list:
            if ally.user.is_active:
                if not ally.user.is_active:
                    allies_list = allies_list.exclude(id=ally.id)
        return render(request, 'sap/dashboard_ally.html', {'allies_list': allies_list})

    def post(self, request):
        """Returns filtered version of allies on the dashboard"""
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
                if ally.user.is_active:
                    if not ally.user.is_active:
                        allies_list = allies_list.exclude(id=ally.id)
            return render(request, 'sap/dashboard_ally.html', {'allies_list': allies_list})

        return HttpResponse()


class AnalyticsView(AccessMixin, TemplateView):
    """takes in input from other methods and returns the seperate years and numbers"""
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
        """takes in input from other methods and returns the seperate years and numbers"""
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
        """turns datetime object into a string (just the year)"""
        user = ally.user
        joined = user.date_joined
        joined = datetime.datetime.strftime(joined, '%Y')
        return joined

    @staticmethod
    def find_years(allies):
        """get the years that each user type signed up for"""
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
        """Finds the number of each type of ally that signup per year"""
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
        """finds all categories and appends them to a list"""
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
        Gets the number per category of allies
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
        gets number of students per year
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
        """gets analytics view"""
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
