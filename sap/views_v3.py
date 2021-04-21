"""
views_v3 has functions that are mapped to the urls in urls.py
"""
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.views.generic import View
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseNotFound
from .models import Ally, StudentCategories, AllyStudentCategoryRelation, Event, \
    EventInviteeRelation, EventAttendeeRelation

User = get_user_model()

class EditAllyProfile(View):
    """
    allows admins/ allies to edit profiles/ their own profile
    """

    @staticmethod
    def set_category(ally_categories, category_id, boolean_value):
        """ sets ally category based on what the category is called and a boolean value"""
        if category_id == 'First generation college-student':
            ally_categories.first_gen_college_student = boolean_value
        elif category_id == 'Low-income':
            ally_categories.low_income = boolean_value
        elif category_id == 'Underrepresented racial/ethnic minority':
            ally_categories.under_represented_racial_ethnic = boolean_value
        elif category_id == 'LGBTQ':
            ally_categories.lgbtq = boolean_value
        elif category_id == 'Transfer Student':
            ally_categories.transfer_student = boolean_value
        elif category_id == 'Rural':
            ally_categories.rural = boolean_value
        elif category_id == 'Disabled':
            ally_categories.disabled = boolean_value
        return ally_categories

    @staticmethod
    def set_categories(student_categories, ally_categories, same):
        """creates a categories object and then sets them, returning wether or not they were the same as well"""
        categories_dict = {
            'First generation college-student': ally_categories.first_gen_college_student,
            'Low-income': ally_categories.low_income,
            'Underrepresented racial/ethnic minority': ally_categories.under_represented_racial_ethnic,
            'LGBTQ': ally_categories.lgbtq,
            'Transfer Student': ally_categories.transfer_student,
            'Rural': ally_categories.rural,
            'Disabled':  ally_categories.disabled
        }
        for category, is_category in categories_dict.items():
            if category in student_categories:
                if not is_category:
                    same = False
                    EditAllyProfile.set_category(ally_categories, category, True)
            else:
                if is_category:
                    same = False
                    EditAllyProfile.set_category(ally_categories, category, False)
        ally_categories.save()
        return same

    @staticmethod
    def set_boolean(_list, post_dict, ally, same):
        """Enter what this class/method does"""
        selection_dict = {'studentsInterestedRadios': ally.people_who_might_be_interested_in_iba,
                          'labShadowRadios': ally.willing_to_offer_lab_shadowing,
                          'connectingWithMentorsRadios': ally.interested_in_connecting_with_other_mentors,
                          'openingRadios': ally.openings_in_lab_serving_at,
                          'mentoringRadios': ally.interested_in_mentoring,
                          'undergradMentoringRadios': ally.interested_in_mentoring,
                          'mentorTrainingRadios': ally.interested_in_mentor_training,
                          'volunteerRadios': ally.willing_to_volunteer_for_events,
                          'interestLabRadios': ally.interested_in_joining_lab,
                          'labExperienceRadios': ally.has_lab_experience,
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
    def get(request, username='', category_id=0):
        """Enter what this class/method does"""
        user_req = request.user

        if (username != user_req.username) and not user_req.is_staff:
            messages.warning(request, 'Access Denied!')
            return redirect('sap:ally-dashboard')
        try:
            user = User.objects.get(username=username)
            ally = Ally.objects.get(user=user)
            category_relation = AllyStudentCategoryRelation.objects.get(ally_id=ally.id)
            category = StudentCategories.objects.get(id=category_id)
            if category_relation.ally_id != ally.id:
                messages.warning(request, 'Access Denied!')
                if user_req.is_staff:
                    return redirect('sap:sap-dashboard')
                return redirect('sap:ally-dashboard')

            return render(request, 'sap/admin_ally_table/edit_ally.html', {
                'ally': ally,
                'category': category,
                'req': request.user,
            })
        except ObjectDoesNotExist:
            return HttpResponseNotFound()



#{'csrfmiddlewaretoken': ['ex5Zuuyjk241FNEvxQoU4a4bnYbw4oI9gtHoblO2iG6EHhRhgAmvcerjUN9Wa6c9'],
    # 'firstName': ['Alesia'], 'lastName': ['Larsen'], 'newUsername': ['alarsen'], 'username':
    # ['alarsen'], 'email': ['alesia-larsen@uiowa.ed'], 'hawkID': ['alarsen'], 'password': [''],
    # 'roleSelected': ['Undergraduate Student'], 'undergradYear': ['Freshman'], 'major': ['Human Physiolog'],
    # 'intersetLabRadios': ['Yes'], 'labExperienceRadios': ['No'], 'undergradMentoringRadios': ['Yes'],
    # 'beingMentoredRadios': ['No']}

    def post(self, request, username='', category_id='0'):
        """Updates profile details from edit_ally page"""
        post_dict = dict(request.POST)
        user_req = request.user
        category_id = int(category_id)

        try:
            user = User.objects.get(username=username)
            ally = Ally.objects.get(user=user)
            category = StudentCategories.objects.get(id=category_id)
            category_relation = AllyStudentCategoryRelation.objects.get(student_category_id=ally.id)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.WARNING,
                                 'Ally does not exist!')
            if user_req.is_staff:
                return redirect('sap:sap-dashboard')
            return redirect('sap:ally-dashboard')

        if category_id != category_relation.student_category_id:
            messages.add_message(request, messages.WARNING, 'Access Denied!')
            if user_req.is_staff:
                return redirect('sap:sap-dashboard')
            return redirect('sap:ally-dashboard')

        if (not user_req.is_staff) and user_req.username != username:
            messages.add_message(request, messages.WARNING, 'Access Denied!')
            return redirect('sap:ally-dashboard')

        message = ''
        same = True
        try:
            user_type = post_dict['roleSelected'][0]
            if user_type != ally.user_type:
                ally.user_type = user_type
                same = False
        except KeyError:
            message += 'User type could not be updated!\n'
        try:
            hawk_id = post_dict['hawkID'][0]
            if hawk_id not in (ally.hawk_id, ''):
                ally.hawk_id = hawk_id
                same = False
        except KeyError:
            message += " HawkID could not be updated!\n"
        if ally.user_type != "Undergraduate Student":
            selections, same = self.set_boolean(
                ['studentsInterestedRadios', 'labShadowRadios', 'connectingWithMentorsRadios',
                 'openingRadios', 'mentoringRadios',
                 'mentorTrainingRadios', 'volunteerRadios'], post_dict, ally, same)
            try:
                same = EditAllyProfile.set_categories(post_dict['mentorCheckboxes'], category, same)
            except KeyError:
                same = EditAllyProfile.set_categories([], category, same)
            try:
                aor = ','.join(post_dict['areaOfResearchCheckboxes'])
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
            ally.interested_in_mentoring = selections['mentoringRadios']
            ally.willing_to_offer_lab_shadowing = selections['labShadowRadios']
            ally.openings_in_lab_serving_at = selections['openingRadios']
            ally.interested_in_connecting_with_other_mentors = selections['connectingWithMentorsRadios']
            ally.willing_to_volunteer_for_events = selections['volunteerRadios']
            ally.interested_in_mentor_training = selections['mentorTrainingRadios']
            ally.save()
        else:
            if user_req.is_staff:
                selections, same = self.set_boolean(
                    ['interestLabRadios', 'labExperienceRadios', 'undergradMentoringRadios', 'beingMentoredRadios'],
                    post_dict, ally, same)
            else:
                selections, same = self.set_boolean(
                    ['interestLabRadios', 'labExperienceRadios', 'beingMentoredRadios',
                     'undergradMentoringRadios', 'agreementRadios'],
                    post_dict, ally, same)

            try:
                same = EditAllyProfile.set_categories(post_dict['identityCheckboxes'], category, same)
            except KeyError:
                same = EditAllyProfile.set_categories([], category, same)

            year = post_dict['undergradYear'][0]
            major = post_dict['major'][0]
            if not (year == ally.year and major == ally.major):
                same = False
            ally.year = year
            ally.major = major

            ally.interested_in_joining_lab = selections['interestLabRadios']
            ally.has_lab_experience = selections['labExperienceRadios']
            ally.interested_in_being_mentored = selections['beingMentoredRadios']
            ally.interested_in_mentoring = selections['undergradMentoringRadios']
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
            return redirect(reverse('sap:admin_edit_ally', args=[user.username, category_id]))
        if same:
            messages.add_message(request, messages.WARNING,
                                 'No Changes Detected!' + message)
            return redirect(reverse('sap:admin_edit_ally', args=[user.username, category_id]))

        if not user_req.is_staff:
            messages.add_message(request, messages.SUCCESS,
                                 'Profile updated!\n' + message)
        else:
            messages.add_message(request, messages.SUCCESS,
                                 'Ally updated!\n' + message)
        if user_req.is_staff:
            return redirect('sap:sap-dashboard')

        return redirect('sap:ally-dashboard')

class AllyEventInformation(View):
    @staticmethod
    def get(request, ally_username=''):
        try:
            user = User.objects.get(username=ally_username)
            ally = Ally.objects.get(user=user)
        except ObjectDoesNotExist:
            messages.warning(request, 'Ally Does not Exist!')
            if request.user.is_staff:
                return redirect('sap:sap-dashboard')
            else:
                return redirect('sap:ally-dashboard')

        events = Event.objects.all()

        events_invited_to = EventInviteeRelation.objects.filter(ally_id=ally.id)
        events_signed_up = EventAttendeeRelation.objects.filter(ally_id=ally.id)

        event_invited = []
        event_signed_up_id = []
        for event in events_invited_to:
            event_invited.append(events.filter(id=event.event_id)[0])
        for event in events_signed_up:
            event_signed_up_id.append(event.event_id)

        return render(request, 'sap/admin_ally_table/view_ally_event_information.html', {
            'ally': ally,
            'invited_events': event_invited,
            'signed_up_events': event_signed_up_id,
        })