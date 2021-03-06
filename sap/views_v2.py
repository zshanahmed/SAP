"""
views_v2 has functions that are mapped to the urls in urls.py
"""
import csv
import datetime
import io
import os
import uuid
from datetime import date
from notifications.signals import notify
import pandas as pd
from pandas.errors import ParserError, EmptyDataError
import xlsxwriter
from xlrd import XLRDError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView, View

from sap.forms import UserResetForgotPasswordForm
from sap.models import StudentCategories, Ally, AllyStudentCategoryRelation, Event, EventInviteeRelation, EventAttendeeRelation
from sap.tokens import account_activation_token, password_reset_token
from sap.views import User, AccessMixin


class SignUpEventView(View):
    """
    Register for event.
    """

    def get(self, request, context='calendar'):
        """
        Invitees can register for event
        """

        user_current = request.user
        ally_current = Ally.objects.filter(user=user_current)
        event_id = request.GET['event_id']

        if ally_current.exists() and user_current.is_active:

            event_invitee_rel = EventInviteeRelation.objects.filter(event=event_id, ally=ally_current[0])

            if event_invitee_rel.exists(): # Check if user is invited
                event_attend_rel = EventAttendeeRelation.objects.filter(event=event_id, ally=ally_current[0])

                if not event_attend_rel.exists():  # Check if user is invited
                    EventAttendeeRelation.objects.create(event_id=event_id,
                                                         ally_id=ally_current[0].id)
                    messages.success(request,
                                     'You have successfully signed up for this event!')
                else:
                    messages.success(request,
                                     'You have already signed up for this event!')

            else:
                messages.warning(request,
                                 'You cannot sign up for this event since you are not invited.')

        # else:
        #     messages.error(request,
        #                    'Access denied. You are not registered in our system.')

        if context == 'notification':
            return redirect('sap:notification_center')
        return redirect(reverse('sap:calendar'))



def set_boolean(_list, post_dict):
    """Enter what this class/method does"""
    dictionary = {}
    for selection in _list:
        if post_dict[selection][0] == 'Yes':
            dictionary[selection] = True
        else:
            dictionary[selection] = False
    return dictionary

def categories_to_string(ally):
    """
    Returns categories of ally to list format
    """
    ally_categories = []
    category_rel = AllyStudentCategoryRelation.objects.get(ally_id=ally.id)
    ally_category = StudentCategories.objects.filter(id=category_rel.student_category_id)
    category_dict = list(ally_category.values())[0]
    for key, value in category_dict.items():
        category_map = {
            "first_gen_college_student": "First generation college-student",
            "rural": "Rural",
            "under_represented_racial_ethnic": "Underrepresented racial/ethnic minority",
            "low_income": "Low-income",
            "disabled": "Disabled",
            "transfer_student": "Transfer Student",
            "lgbtq": "LGBTQ"
        }
        if value and key not in ['id']:
            ally_categories.append(category_map[key])
    return ally_categories

def event_invitations(ally):
    """
    Creates invitation for ally
    """
    events_ally = Event.objects.none()
    print(categories_to_string(ally))
    for category in categories_to_string(ally):
        events_ally |= Event.objects.filter(special_category__contains=category)

    if ally.user_type:
        role = ally.user_type
        if role == 'Undergraduate Student':
            if ally.interested_in_being_mentored:
                if Event.objects.filter(mentor_status__contains='Mentees'):
                    events_ally |= Event.objects.filter(role_selected__contains=role).filter(
                        school_year_selected__contains=ally.year).filter(mentor_status__contains='Mentees')
                else:
                    events_ally |= Event.objects.filter(role_selected__contains=role).filter(
                        school_year_selected__contains=ally.year)
            else:
                events_ally |= Event.objects.filter(role_selected__contains=role).filter(
                    school_year_selected__contains=ally.year)
        else:
            if ally.interested_in_mentoring:
                if Event.objects.filter(mentor_status__contains='Mentors'):
                    events_ally |= Event.objects.filter(role_selected__contains=role).filter(
                        mentor_status__contains='Mentors')
                else:
                    events_ally |= Event.objects.filter(role_selected__contains=role)
            else:
                events_ally |= Event.objects.filter(role_selected__contains=role)

    if ally.area_of_research:
        for aor in ally.area_of_research.split(','):
            print('Aor: ', aor, '  ', Event.objects.filter(research_field__contains=aor))
            events_ally |= Event.objects.filter(research_field__contains=aor)

    if events_ally is not None:
        for event in events_ally:
            EventInviteeRelation.objects.create(event_id=event.id, ally_id=ally.id)

def make_categories(student_categories):
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
        elif category_id == 'Transfer student':
            categories.transfer_student = True
        elif category_id == 'Rural':
            categories.rural = True
        elif category_id == 'Disabled':
            categories.disabled = True
    categories.save()
    return categories


def create_new_user(post_dict):
    """
    Create new user and associated ally based on what user inputs in sign-up page
    Also creates event invitations for new user based on the information they provide
    """
    print(post_dict)
    user = User.objects.create_user(username=post_dict["new_username"][0],
                                    password=post_dict["new_password"][0],
                                    email=post_dict["new_email"][0],
                                    first_name=post_dict["firstName"][0],
                                    last_name=post_dict["lastName"][0],
                                    is_active=False)  # Set to False until user verify via email

    if post_dict['roleSelected'][0] != "Undergraduate Student":
        selections = set_boolean(['studentsInterestedRadios', 'labShadowRadios', 'connectingWithMentorsRadios',
                                  'openingRadios', 'mentoringRadios', 'trainingRadios', 'volunteerRadios'],
                                 post_dict)
        try:
            stem_fields = ','.join(post_dict['areaOfResearchCheckboxes'])
        except KeyError:
            stem_fields = None
        ally = Ally.objects.create(user=user, user_type=post_dict['roleSelected'][0], hawk_id=user.username,
                                   people_who_might_be_interested_in_iba=selections['studentsInterestedRadios'],
                                   how_can_science_ally_serve_you=post_dict['howCanWeHelp'][0],
                                   area_of_research=stem_fields, openings_in_lab_serving_at=selections['openingRadios'],
                                   willing_to_offer_lab_shadowing=selections['labShadowRadios'],
                                   interested_in_mentor_training=selections['trainingRadios'],
                                   willing_to_volunteer_for_events=selections['volunteerRadios'],
                                   interested_in_mentoring=selections['mentoringRadios'],
                                   interested_in_connecting_with_other_mentors=selections['connectingWithMentorsRadios'],
                                   description_of_research_done_at_lab=post_dict['research-des'][0])
        try:
            categories = make_categories(post_dict["mentorCheckboxes"])
        except KeyError:
            categories = StudentCategories.objects.create()
    else:
        selections = set_boolean(['interestLabRadios', 'labExperienceRadios', 'beingMentoredRadios',
                                  'undergradMentoringRadios', 'agreementRadios'], post_dict)
        ally = Ally.objects.create(user=user,
                                   user_type=post_dict['roleSelected'][0],
                                   hawk_id=user.username,
                                   major=post_dict['major'][0],
                                   year=post_dict['undergradYear'][0],
                                   interested_in_joining_lab=selections['interestLabRadios'],
                                   has_lab_experience=selections['labExperienceRadios'],
                                   interested_in_mentoring=selections['undergradMentoringRadios'],
                                   information_release=selections['agreementRadios'],
                                   interested_in_being_mentored=selections['beingMentoredRadios'])
        try:
            categories = make_categories(post_dict["identityCheckboxes"])
        except KeyError:  # pragma: no cover
            categories = StudentCategories.objects.create()

    admins = User.objects.filter(is_staff=True)
    msg = 'New ally has joined: ' + user.username
    for admin in admins:
        notify.send(user, recipient=admin, verb=msg, action_object=ally)
    notify.send(user, recipient=user, verb='Welcome to Science Alliance!')

    AllyStudentCategoryRelation.objects.create(student_category_id=categories.id, ally_id=ally.id)
    event_invitations(ally)
    return user, ally


class SignUpView(TemplateView):
    """Enter what this class/method does"""
    template_name = "sap/sign-up.html"

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
            from_email="zshanahmed2@gmail.com",
            to_emails=entered_email,
            subject='Action Required: Confirm Your New Account',
            html_content=message_body)

        try:
            sendgrid_obj = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            sendgrid_obj.send(email_content)

            messages.info(self.request,
                          'ATTENTION REQUIRED: To finish creating a new account, '
                          'please follow instructions in the email we just sent you.')
        except HTTPError as e:  # pragma: no cover
            print(e.body)
            messages.warning(self.request,
                             'Please try again another time or contact team1sep@hotmail.com '
                             'and report this error code, HTTP401.')

    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, self.template_name)
        return redirect('sap:home')

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
            # If user is not active, delete user_temp and create new user on db with is_active=False

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
            if post_dict["new_password"][0] != post_dict["repeat_password"][0]:
                messages.warning(request,
                                 "Repeated password is not the same as the inputted password!", )
                return redirect("/sign-up")

            if len(post_dict["new_password"][0]) < min_length:
                messages.warning(request,
                                 "Password must be at least {0} characters long".format(min_length), )
                return redirect("/sign-up")

            user, _ = create_new_user(post_dict=post_dict)
            site = get_current_site(request)
            self.send_verification_email(user=user, site=site, entered_email=post_dict["new_email"][0])
        else:
            if User.objects.filter(username=post_dict["new_username"][0]).exists():
                messages.warning(request,
                                 'Account can not be created because username already exists!')
                return redirect('/sign-up')
            # elif User.objects.filter(email=postDict["new_email"][0]).exists():
            #     messages.add_message(request, messages.WARNING,
            #                          'Account can not be created because email already exists')
            #     return redirect('/sign-up')
            if post_dict["new_password"][0] != post_dict["repeat_password"][0]:
                messages.warning(request,
                                 "Repeated password is not the same as the inputted password!")
                return redirect("/sign-up")
            if len(post_dict["new_password"][0]) < min_length:
                messages.warning(request,
                                 "Password must be at least {0} characters long".format(min_length))
                return redirect("/sign-up")
            user, _ = create_new_user(post_dict=post_dict)
            site = get_current_site(request)
            self.send_verification_email(user=user, site=site, entered_email=post_dict["new_email"][0])

        return redirect("sap:home")


# class SignUpDoneView(TemplateView):
#     """
#     A view which is presented if the user successfully fill out the form presented in Sign-Up view
#     """
#     template_name = "sap/sign-up-done.html"
#
#     def get(self, request, *args, **kwargs):
#         """Enter what this class/method does"""
#         site = get_current_site(request)
#         accepted_origin = 'http:' + '//' + site.domain + reverse('sap:sign-up')
#
#         try:
#             origin = request.headers['Referer']
#
#             if request.headers['Referer'] and origin == accepted_origin:
#                 return render(request, self.template_name)
#
#             if request.user.is_authenticated:
#                 return redirect('sap:resources')
#
#             return redirect('sap:home')
#
#         except KeyError:
#             if request.user.is_authenticated:
#                 return redirect('sap:resources')
#
#             return redirect('sap:home')


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
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exception:
            messages.warning(request, str(exception))
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
        if not request.user.is_authenticated:
            form = PasswordResetForm(request.GET)
            return render(request, 'sap/password-forgot.html', {'form': form})

        return redirect('sap:home')

    def post(self, request):
        """
        Only if the confirmation email is successfully sent by SendGrid, ally.reset_password can be updated
        """
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            entered_email = request.POST.get('email')
            valid_email = User.objects.filter(email=entered_email)
            site = get_current_site(request)

            if len(valid_email) > 0:
                user = valid_email[0]
                ally_filter = Ally.objects.filter(user=user)

                # Can only reset forgotten password for active user and there is an ally associated with the user
                if user.is_active and ally_filter.exists():
                    ally = ally_filter[0]
                    # ally.reset_password = True
                    # ally.save()

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
                        from_email="zshanahmed2@gmail.com",
                        to_emails=entered_email,
                        subject='Reset Password for Science Alliance Portal',
                        html_content=message_body)

                    try:
                        sendgrid_obj = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                        sendgrid_obj.send(email_content)

                    except HTTPError:  # pragma: no cover
                        messages.warning(self.request,
                                         'Please try again another time or contact team1sep@hotmail.com '
                                         'and report this error code, HTTP401.')
                        return redirect('sap:home')

                    # this part will only be executed if try block succeed
                    ally.reset_password = True
                    ally.save()

                    messages.info(request,
                                  'ATTENTION REQUIRED: To finish resetting your password, '
                                  'please follow instructions in the email we just sent you.')

                    return redirect('sap:home')


            # return redirect('/password-forgot-done')
            # return render(request, 'account/password-forgot.html', {'form': form})
            messages.info(request,
                          'ATTENTION REQUIRED: To finish resetting your password, '
                          'please follow instructions in the email we just sent you.')
            return redirect('sap:home')

        # if form is not valid
        return render(request, 'sap/password-forgot.html', {'form': form})


# class ForgotPasswordDoneView(TemplateView):
#     """
#     A view which is presented if the user entered valid email in Forget Password view
#     """
#     template_name = "sap/password-forgot-done.html"
#
#     def get(self, request, *args, **kwargs):
#         """Enter what this class/method does"""
#         site = get_current_site(request)
#         accepted_origin = 'http:' + '//' + site.domain + reverse('sap:password-forgot')
#
#         try:
#             origin = request.headers['Referer']
#
#             if request.headers['Referer'] and origin == accepted_origin:
#                 return render(request, self.template_name)
#
#             if request.user.is_authenticated:
#                 return redirect('sap:resources')
#
#             return redirect('sap:home')
#
#         except KeyError:
#             if request.user.is_authenticated:
#                 return redirect('sap:resources')
#
#             return redirect('sap:home')


class ForgotPasswordConfirmView(TemplateView):
    """
    A unique view to users who click to the reset forgot passwork link.
    Allow them to create new password.
    """

    # template_name = "sap/password-forgot-confirm.html"
    def get(self, request, **kwargs):
        """
        Can only access this page is user is active and ally.reset_password = True
        """

        path = request.path
        path_1, token = os.path.split(path)

        if 'uidb64' in kwargs:
            uidb64 = kwargs['uidb64']
        else:
            _, uidb64 = os.path.split(path_1)

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            ally = Ally.objects.get(user=user)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exception:
            messages.warning(request, str(exception))
            user = None
            ally = None

        if user is not None and ally is not None and password_reset_token.check_token(user, token):
            if user.is_active and ally.reset_password:
                context = {
                    'form': UserResetForgotPasswordForm(user),
                    'uid': uidb64,
                    'token': token
                }
                return render(request, 'sap/password-forgot-confirm.html', context)

            if user.is_active and not ally.reset_password:
                messages.error(request, 'Password reset link is expired. Please request a new password reset.')
                return redirect('sap:home')

        messages.error(request, 'Password reset link is invalid. Please request a new password reset.')
        return redirect('sap:home')

    def post(self, request, **kwargs):
        """
        Submit a new password
        Also check if ally.reset_password=True before proceeding
        """
        path = request.path
        path_1, token = os.path.split(path)

        if 'uidb64' in kwargs:
            uidb64 = kwargs['uidb64']
        else:
            _, uidb64 = os.path.split(path_1)

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            ally = Ally.objects.get(user=user)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exception:
            messages.warning(request, str(exception))
            user = None
            ally = None

        if user is not None and ally is not None and password_reset_token.check_token(user, token):
            if user.is_active and ally.reset_password:
                form = UserResetForgotPasswordForm(user=user, data=request.POST)
                if form.is_valid():
                    form.save()
                    update_session_auth_hash(request, form.user)

                    ally.reset_password = False
                    ally.save()
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

            if user.is_active and not ally.reset_password:
                messages.error(request, 'Password reset link is expired. Please request a new password reset.')
                return redirect('sap:home')

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
    """Downloads allies in the database"""

    @staticmethod
    def fields_helper(model, columns):
        """only gets relevant fields from each database entry"""
        for field in model._meta.get_fields():
            fields = str(field).split(".")[-1]
            if fields in userFields or fields in allyFields or fields in categoryFields:
                columns.append(fields)
        return columns

    @staticmethod
    def cleanup(dictionary):
        """outputs nicely formatted list of data"""
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
        """Make pandas dataframe of ally data"""
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
        """Takes request and outputs allies csv as HttpResponse"""
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
    def cleanup_frame(data_frame, errorlog):
        """Enter what this class/method does"""
        try:
            data_frame = data_frame.drop(['Workflow ID', 'Status', 'Name'], axis=1)
        except KeyError: # pragma: no cover
            errorlog[1000] = "Could not drop unnecessary columns \'Workflow ID\', \'Status\', \'Name\'"
        try:
            data_frame1 = pd.DataFrame({"Name": data_frame['Initiator']})
        except KeyError:  # pragma: no cover
            errorlog[2000] = "CRITICAL ERROR: The \'Initiator\' column is not present, cannot proceed"
            return data_frame, errorlog
        try:
            data_frame2 = data_frame1.applymap(lambda x: x.split('\n'))
            data_frame2 = data_frame2.applymap(lambda x: x[0] + x[1])
            data_frame2 = data_frame2.replace(regex=[r'\d'], value='')
            data_frame2 = data_frame2['Name'].str.split(', ', n=1, expand=True)
            data_frame2 = data_frame2.rename({0: 'last_name', 1: 'first_name'}, axis=1)
            data_frame = data_frame.join(data_frame2)
            data_frame['email'] = data_frame['Initiator'].str.extract(r'(.*@uiowa.edu)')
            data_frame = data_frame.drop(['Initiator'], axis=1)
        except KeyError:  # pragma: no cover
            errorlog[3000] = "CRITICAL ERROR: data could not be extracted from \'Initiator\' column " \
                             "and added as columns"
            return data_frame, errorlog
        try:
            data_frame[boolFields] = data_frame[boolFields].fillna(value=False)
            data_frame[boolFields] = data_frame[boolFields].replace('Yes (Yes)', True)
            data_frame[boolFields] = data_frame[boolFields].replace('No (No)', False)
            data_frame['interested_in_being_mentored'] = False
            data_frame['interested_in_mentoring'] = False
            data_frame['Year'] = data_frame['Year'].replace(regex=r'\s\([^)]*\)', value='')
            data_frame['Year'] = data_frame['Year'].replace(regex=r'Sophmore', value='Sophomore')
            for i in range(0, len(data_frame)):
                year = data_frame['Year'][i]
                if year in ('Freshman', 'Sophomore'):
                    data_frame['interested_in_being_mentored'][i] = data_frame['Are you interested in becoming a peer mentor?'][i] or \
                                                                    data_frame['Are you interested in mentoring students?'][i]
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
        except KeyError:  # pragma: no cover
            errorlog[4000] = "CRITICAL ERROR: boolean could not replace blanks. Ensure the following are present:" + \
                             str(boolFields)
            return data_frame, errorlog
        try:
            data_frame = data_frame.fillna(value='')
            data_frame['STEM Area of Research'] = data_frame['STEM Area of Research'].replace(regex=[r'\n'], value=',')
            data_frame['STEM Area of Research'] = data_frame['STEM Area of Research'].replace(regex=[r'\s\([^)]*\)'], value='')
            data_frame['University Type'] = data_frame['University Type'].replace(regex=[r'\s\([^)]*\)', '/Post-doc'], value='')
            data_frame = data_frame.rename({'STEM Area of Research': 'area_of_research',
                                            'University Type': 'user_type',
                                            'Please provide a short description of the type of research done by undergrads':
                                                'description_of_research_done_at_lab',
                                            'Year': 'year', 'Major': 'major',
                                            'How can the Science Alliance serve you?': 'how_can_science_ally_serve_you'},
                                           axis=1)
        except KeyError:  # pragma: no cover
            errorlog[5000] = "CRITICAL ERROR: problem in tidying charfield columns. ensure the following is present:" \
                             "STEM Area of Research, University Type, Please provide a short description of the type " \
                             "of research done by undergrads, " \
                             "Year, Major"
            return data_frame, errorlog
        try:
            data_frame['Submission Date'] = data_frame['Submission Date'].map(lambda x: x.strftime("%b-%d-%Y"))
            data_frame = data_frame.rename({'Submission Date': 'date_joined'}, axis=1)
        except KeyError:  # pragma: no cover
            errorlog[6000] = "CRITICAL ERROR: problem converting timestamp to date, please ensure Submission Date is a column"
            return data_frame, errorlog
        try:
            data_frame['username'] = ''
            for i in range(0, len(data_frame)):
                hawkid = data_frame['first_name'][i][0] + data_frame['last_name'][i]
                data_frame['username'][i] = hawkid.lower()
        except KeyError:  # pragma: no cover
            errorlog[7000] = "CRITICAL ERROR: Could not convert first name and last name to hawkid. Please Ensure the " \
                             "Initiator is present"
            return data_frame, errorlog
        data_frame['information_release'] = False
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
                if 'LBGTQ' in tmp:
                    data_frame['lgbtq'][i] = True
                if 'Transfer student' in tmp:
                    data_frame['transfer_student'][i] = True
                if 'Underrepresented racial/ethnic minority' in tmp:
                    data_frame['under_represented_racial_ethnic'][i] = True
            data_frame = data_frame.drop(['Are you interested in serving as a mentor to students who identify as any of the following '
                                          '(check all that may apply)'], axis=1)
        except KeyError:  # pragma: no cover
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
        except KeyError:  # pragma: no cover
            error_log[9000] = "CRITICAL ERROR: Data does not contain necessary columns. Please ensure that the data has columns:\n" + \
                              str(userFields + allyFields + categoryFields)
        for ally in ally_data.items():
            if (ally[1]['user_type'] == "Staff" or ally[1]['user_type'] == "Graduate Student"
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

                        notify.send(user, recipient=user, verb='Welcome to Science Alliance!')

                    except IntegrityError: # pragma: no cover
                        error_log[ally[0]] = "Ally already exists in the database"

                except IntegrityError:  # pragma: no cover
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
        except ParserError: # pragma: no cover
            error_log[900] = "Empty xlsx cannot make allies."
        except EmptyDataError:  # pragma: no cover
            error_log[900] = "Empty csv cannot make allies"
        except UnicodeDecodeError:  # pragma: no cover
            try:
                data_frame = pd.read_excel(file)
            except XLRDError:
                error_log[900] = "Problem reading file: was it stored in .csv or xlsx?"
        columns = list(data_frame.columns)
        if columns != (userFields + allyFields + categoryFields):
            data_frame, error_log = UploadAllies.cleanup_frame(data_frame, error_log)
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
        """Uploads allies if they match the requested format and returns a log of users added and errors encountered"""
        if request.user.is_staff:
            try:
                print(request.FILES)
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
            except KeyError:  # pragma: no cover
                messages.add_message(request, messages.ERROR, 'Please select a file to upload!')

            return redirect('sap:sap-dashboard')

        return HttpResponseForbidden()
