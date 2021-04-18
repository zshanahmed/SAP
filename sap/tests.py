"""
contains unit tests for sap app
"""
from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, Client  # tests file
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UpdateAdminProfileForm
from .models import Ally, AllyStudentCategoryRelation, StudentCategories

User = get_user_model()


def create_ally(username, hawk_id):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    user_1 = User.objects.create_user(username=username,
                                      email='jlennon@beatles.com',
                                      password='glass onion',
                                      first_name='John',
                                      last_name='Beatles')

    return Ally.objects.create(user=user_1, hawk_id=hawk_id, user_type='student', works_at='College of Engineering', year='first',
                               major='Computer Science')


class AdminAllyTableFeatureTests(TestCase):
    """
    Unit tests for features on the Admin dashboard
    """

    def setUp(self):
        self.username = 'Admin_1'
        self.password = 'admin_password1'
        self.email = 'email@test.com'
        self.client = Client()

        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.ally_user = User.objects.create_user(username='johndoe',
                                                  email='johndoe@uiowa.edu',
                                                  password='johndoe',
                                                  first_name='John',
                                                  last_name='Doe')

        self.ally = Ally.objects.create(
            user=self.ally_user,
            hawk_id='johndoe',
            user_type='Staff',
            works_at='College of Engineering',
            area_of_research='Computer Science and Engineering,Health and Human Physiology,Physics',
            description_of_research_done_at_lab='Created tools to fight fingerprinting',
            people_who_might_be_interested_in_iba=True,
            how_can_science_ally_serve_you='Help in connecting with like minded people',
            year='Senior',
            major='Electical Engineering',
            willing_to_offer_lab_shadowing=True,
            willing_to_volunteer_for_events=True,
            interested_in_mentoring=False,
            interested_in_connecting_with_other_mentors=True,
            interested_in_mentor_training=True,
            interested_in_joining_lab=True,
            has_lab_experience=True,
            information_release=True,
            openings_in_lab_serving_at=True,
        )

        self.ally_student_category = StudentCategories.objects.create(
            under_represented_racial_ethnic = False,
            first_gen_college_student = False,
            transfer_student = False,
            lgbtq = False,
            low_income = False,
            rural = True,
            disabled = False
        )

        self.ally_student_category_relation = AllyStudentCategoryRelation.objects.create(
            ally=self.ally,
            student_category = self.ally_student_category
        )

        self.ally_user_2 = User.objects.create_user(username='johndoe_2',
                                                    email='johndoe@uiowa.edu',
                                                    password='johndoe',
                                                    first_name='John',
                                                    last_name='Doe',
                                                    is_active=False)

        self.ally_2 = Ally.objects.create(
            user=self.ally_user_2,
            hawk_id='johndoe_2',
            user_type='Staff',
            works_at='College of Engineering',
            description_of_research_done_at_lab='Created tools to fight fingerprinting',
            people_who_might_be_interested_in_iba=True,
            how_can_science_ally_serve_you='Help in connecting with like minded people',
            year='Senior',
            major='Electical Engineering',
            willing_to_offer_lab_shadowing=True,
            willing_to_volunteer_for_events=True,
            interested_in_mentoring=False,
            interested_in_being_mentored=True,
            interested_in_connecting_with_other_mentors=True,
            interested_in_mentor_training=True,
            interested_in_joining_lab=True,
            has_lab_experience=True,
            information_release=True,
            openings_in_lab_serving_at=True,
        )

        self.ally_2_student_category = StudentCategories.objects.create(
            under_represented_racial_ethnic = True,
            first_gen_college_student = True,
            transfer_student = True,
            lgbtq = True,
            low_income = True,
            rural = False,
            disabled = True
        )

        self.ally_2_student_category_relation = AllyStudentCategoryRelation.objects.create(
            ally=self.ally_2,
            student_category = self.ally_2_student_category
        )

    def test_major_filter_for_admin(self):
        """
        Show all allies conforming to major filter
        """
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()
        self.ally_user_2.is_active = True
        self.ally_user_2.save()
        self.client.login(username=self.username, password=self.password)

        # Should return no allies
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'major': 'Random',
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, "No allies are available.", html=True
        )

        # Should find our johndoe
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'major': 'Electical Engineering',
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, self.ally_user.first_name + ' ' + self.ally_user.last_name, html=True
        )


    def test_mentorship_status_filter_for_admin(self):
        """
        Show all allies conforming to mentorship status filter
        """
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()
        self.ally_user_2.is_active = True
        self.ally_user_2.save()
        self.client.login(username=self.username, password=self.password)

        # Should return no allies
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'mentorshipStatus': ['Mentor'],
                'major': '',
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, "No allies are available.", html=True
        )

        # Should find our johndoe
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'mentorshipStatus': ['Mentee'],
                'major': '',
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, self.ally_user.first_name + ' ' + self.ally_user.last_name, html=True
        )

    def test_user_type_filter_for_admin(self):
        """
        Show all allies conforming to user type filter
        """
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()
        self.ally_user_2.is_active = True
        self.ally_user_2.save()
        self.client.login(username=self.username, password=self.password)

        # Should return no allies
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'roleSelected': ['Faculty'],
                'major': '',
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, "No allies are available.", html=True
         )

        # Should find our johndoe
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'roleSelected': ['Staff'],
                'major': '',
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, self.ally_user.first_name + ' ' + self.ally_user.last_name, html=True
        )

    def test_student_category_filter_for_admin(self):
        """
        Show all allies conforming to student category filter
        """
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()
        self.ally_user_2.is_active = True
        self.ally_user_2.save()
        self.client.login(username=self.username, password=self.password)

        # Should return no allies
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'idUnderGradCheckboxes': ['First generation college-student', 'Low-income', 'Underrepresented racial/ethnic minority',
                                          'LGBTQ', 'Rural', 'Disabled'],
                'major': '',
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, "No allies are available.", html=True
        )

        # Should find our johndoe
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'idUnderGradCheckboxes': ['Rural'],
                'major': '',
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, self.ally_user.first_name + ' ' + self.ally_user.last_name, html=True
        )

    def test_year_filter_for_admin(self):
        """
        Show all allies conforming to year filters
        """
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        # Should return no allies
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'undergradYear': ['Junior'],
                'major': '',
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, "No allies are available.", html=True
        )

        # Should find our johndoe
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'undergradYear': ['Senior'],
                'major': '',
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, self.ally_user.first_name + ' ' + self.ally_user.last_name, html=True
        )

    def test_stem_aor_filter_for_admin(self):
        """
        Show all allies conforming to stem aor filters
        """
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        # Should return no allies
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'stemGradCheckboxes': ['Bioinformatics'],
                'major': '',
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, "No allies are available.", html=True
        )

        # Should find our johndoe
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'stemGradCheckboxes': ['Physics'],
                'major': '',
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, self.ally_user.first_name + ' ' + self.ally_user.last_name, html=True
        )

    def test_edit_ally_page_for_admin(self):
        """
        Show and Complete Edit ally page for admin
        """

        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        # Testing for Staff user type
        response = self.client.get('/edit_allies/', {'username': self.ally_user.username,
                                                     'category_relation_id': 0})
        self.assertEqual(response.status_code, HTTPStatus.OK)

        dictionary = {'csrfmiddlewaretoken': ['YXW4Ib9TNmwod6ZETztHgp3ouwbg09sbAYibaXHc5RMKbAECHTZKHIsdJrvzvvP5'],
         'firstName': self.ally_user.first_name, 'lastName': self.ally_user.last_name,
         'newUsername': self.ally_user.username,'username': self.ally_user.username,
         'email': self.ally_user.email, 'hawkID': self.ally.hawk_id,
         'password': [''], 'roleSelected': self.ally.user_type,
         'areaOfResearchCheckboxes': ['Biochemistry', 'Bioinformatics', 'Chemical Engineering', 'Chemistry'],
         'research-des': [''], 'openingRadios': ['Yes'], 'labShadowRadios': ['Yes'], 'mentoringRadios': ['Yes'],
         'volunteerRadios': ['Yes'], 'mentorTrainingRadios': ['Yes'], 'connectingWithMentorsRadios': ['Yes'],
         'studentsInterestedRadios': ['Yes'], 'howCanWeHelp': ['']}

        response = self.client.post('/edit_allies/', dictionary, follow=True)

        self.assertContains(
            response, "Science Alliance Portal", html=True
        )
        message = list(response.context['messages'])[0]
        assert "Ally updated!" in str(message)

        # Testing for UnderGrad Student user type
        self.ally.user_type = "Undergraduate Student"
        self.ally.save()
        response = self.client.post(
            '/edit_allies/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'username': [self.ally_user.username], 'category_relation_id': 0,
                'undergradYear': ['Freshman'], 'major': ['Psychology'],
                'interestLabRadios': ['No'], 'labExperienceRadios': ['Yes'], 'undergradMentoringRadios': ['No'],
                'agreementRadios': ['Yes'], 'beingMentoredRadios': ['Yes']
            }, follow=True
        )
        self.assertContains(
            response, "Science Alliance Portal", html=True
        )
        message = list(response.context['messages'])[0]
        assert "Ally updated!" in str(message)


        dictionary = {'csrfmiddlewaretoken': ['YXW4Ib9TNmwod6ZETztHgp3ouwbg09sbAYibaXHc5RMKbAECHTZKHIsdJrvzvvP5'],
         'firstName': 'firstName', 'lastName': 'lastName',
         'newUsername': 'bigUsername', 'username': self.ally_user.username, 'category_relation_id': 0,
         'email': 'bigEmail', 'hawkID': 'bigHawk',
         'password': [''], 'roleSelected': 'Faculty',
         'areaOfResearchCheckboxes': "",
         'research-des': [''], 'openingRadios': ['Yes'], 'labShadowRadios': ['Yes'], 'mentoringRadios': ['Yes'],
         'volunteerRadios': ['Yes'], 'mentorTrainingRadios': ['Yes'], 'connectingWithMentorsRadios': ['Yes'],
         'studentsInterestedRadios': ['Yes'], 'howCanWeHelp': ['']}

        response = self.client.post('/edit_allies/', dictionary, follow=True)

        self.assertContains(
            response, "Science Alliance Portal", html=True
        )
        message = list(response.context['messages'])[0]
        assert "Ally updated!" in str(message)

        dictionary = {'csrfmiddlewaretoken': ['YXW4Ib9TNmwod6ZETztHgp3ouwbg09sbAYibaXHc5RMKbAECHTZKHIsdJrvzvvP5'],
         'firstName': 'firstName',
         'newUsername': self.user.username, 'username': 'bigUsername', 'category_relation_id': 0,
         'email': self.user.email, 'hawkID': 'bigHawk2',
         'password': ['thebiggestPassword'], 'roleSelected': 'Faculty',
         'openingRadios': ['Yes'], 'labShadowRadios': ['Yes'], 'mentoringRadios': ['Yes'],
         'volunteerRadios': ['Yes'], 'mentorTrainingRadios': ['Yes'], 'connectingWithMentorsRadios': ['Yes'],
         'studentsInterestedRadios': ['Yes']}

        response = self.client.post('/edit_allies/', dictionary, follow=True)


    def test_edit_non_ally_page_for_admin(self):
        """
        Show that the code return 404 when username is wrong
        """

        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(
            '/edit_allies/', {'username': 'something'})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        response = self.client.post(
            '/edit_allies/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'username': ['somthing'], 'category_relation_id': 0,
                'studentsInterestedRadios': [str(self.ally.people_who_might_be_interested_in_iba)],
                'howCanWeHelp': ['Finding Jobs']
            }, follow=True
        )
        self.assertContains(
            response, "Science Alliance Portal", html=True
        )
        message = str(list(response.context['messages'])[0])
        assert "Ally does not exist!" in message

    def test_view_ally_page_for_admin(self):
        """
        Show View ally page for admin
        """

        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get('/allies/', {'username': self.ally_user.username})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Ally Profile", html=True
        )

    def test_view_non_ally_page_for_admin(self):
        """
        Show that the code return 404 when username is wrong
        """

        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(
            '/allies/', {'username': 'something'})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_delete_ally(self):
        """
        Unit test for delete ally feature
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        name = self.ally_user.first_name + ' ' + self.ally_user.last_name

        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertContains(response, name, html=True)
        response = self.client.get('/delete/', {'username': self.ally_user.username}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotContains(response, name, html=True)

    def test_delete_ally_fail(self):
        """
        Unit test for deleting non existent ally
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        name = self.ally_user.first_name + " " + self.ally_user.last_name

        response = self.client.get(reverse("sap:sap-dashboard"))
        self.assertContains(response, name, html=True)
        response = self.client.get("/delete/", {"username": "nouserfound"}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class AllyDashboardTests(TestCase):
    """
    Unit tests for features on the ally dashboard
    """

    def setUp(self):
        self.username = 'Ally_1'
        self.password = 'ally_password1'
        self.email = 'email_ally@test.com'
        self.client = Client()

        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.ally_user = User.objects.create_user(username='johndoe1',
                                                  email='johndoe1@uiowa.edu',
                                                  password='johndoe1',
                                                  first_name='John1',
                                                  last_name='Doe1')

        self.ally_user1 = User.objects.create_user(username='johndoe2',
                                                   email='johndoe2@uiowa.edu',
                                                   password='johndoe2',
                                                   first_name='John2',
                                                   last_name='Doe2')

        self.user_ally = Ally.objects.create(
            user=self.user,
            hawk_id='johndoe2',
            user_type='Staff',
            works_at='College of Engineering',
            area_of_research='Computer Science and Engineering,Health and Human Physiology,Physics',
            description_of_research_done_at_lab='Created tools to fight fingerprinting',
            people_who_might_be_interested_in_iba=True,
            how_can_science_ally_serve_you='Help in connecting with like minded people',
            year='Senior',
            major='Electical Engineering',
            willing_to_offer_lab_shadowing=True,
            willing_to_volunteer_for_events=True,
            interested_in_mentoring=True,
            interested_in_connecting_with_other_mentors=True,
            interested_in_mentor_training=True,
            interested_in_joining_lab=True,
            has_lab_experience=True,
            information_release=True,
            openings_in_lab_serving_at=True,
        )

        self.ally = Ally.objects.create(
            user=self.ally_user,
            hawk_id='johndoe1',
            user_type='Staff',
            works_at='College of Engineering',
            area_of_research='Computer Science and Engineering,Health and Human Physiology,Physics',
            description_of_research_done_at_lab='Created tools to fight fingerprinting',
            people_who_might_be_interested_in_iba=True,
            how_can_science_ally_serve_you='Help in connecting with like minded people',
            year='Senior',
            major='Electical Engineering',
            willing_to_offer_lab_shadowing=True,
            willing_to_volunteer_for_events=True,
            interested_in_mentoring=True,
            interested_in_connecting_with_other_mentors=True,
            interested_in_mentor_training=True,
            interested_in_joining_lab=True,
            has_lab_experience=True,
            information_release=True,
            openings_in_lab_serving_at=True,
        )

        self.ally_user_2 = User.objects.create_user(username='johndoe_3',
                                                    email='johndoe3@uiowa.edu',
                                                    password='johndoe3',
                                                    first_name='John3',
                                                    last_name='Doe3',
                                                    is_active=False)

        self.ally_2 = Ally.objects.create(
            user=self.ally_user_2,
            hawk_id='johndoe_3',
            user_type='Staff',
            works_at='College of Engineering',
            description_of_research_done_at_lab='Created tools to fight fingerprinting',
            people_who_might_be_interested_in_iba=True,
            how_can_science_ally_serve_you='Help in connecting with like minded people',
            year='Senior',
            major='Electical Engineering',
            willing_to_offer_lab_shadowing=True,
            willing_to_volunteer_for_events=True,
            interested_in_mentoring=True,
            interested_in_connecting_with_other_mentors=True,
            interested_in_mentor_training=True,
            interested_in_joining_lab=True,
            has_lab_experience=True,
            information_release=True,
            openings_in_lab_serving_at=True,
        )

    def test_dasbhoard_access_for_nonadmin(self):
        """
        Display non admin dashboard page for allies
        """
        self.user.is_staff = False
        self.user.is_active = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse("sap:ally-dashboard"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_year_filter_for_nonadmin(self):
        """
        Show all allies conforming to year filters
        """
        self.user.is_staff = False
        self.user.is_active = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        # Should return no allies
        response = self.client.post(
            '/ally-dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'undergradYear': ['Junior'],
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, "No allies are available.", html=True
        )

        # Should find our johndoe
        response = self.client.post(
            '/ally-dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'undergradYear': ['Senior'],
                'form_type': 'filters'
            }, follow=True
        )
        self.assertContains(
            response, self.ally_user.first_name + ' ' + self.ally_user.last_name, html=True
        )

    def test_update_profile_for_nonadmin(self):
        """
        Update profile for nonadmin
        """
        self.user.is_staff = False
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:ally-dashboard'), follow=True)
        self.assertContains(
            response, "Science Alliance Portal", html=True
        )

        response = self.client.get('/update_ally_profile/', {'username': self.username}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        dictionary = {'csrfmiddlewaretoken': ['YXW4Ib9TNmwod6ZETztHgp3ouwbg09sbAYibaXHc5RMKbAECHTZKHIsdJrvzvvP5'],
         'firstName': 'big guy', 'lastName': 'giga', 'newUsername': 'bigusername1234', 'username': self.username,
        'hawkID': ['bigHawk2'], 'password': ['thebiggestPassword'], 'roleSelected': 'Graduate Student',
         'openingRadios': ['Yes'], 'labShadowRadios': ['No'], 'mentoringRadios': ['Yes'], 'research-des': [''],
        'howCanWeHelp': ['no'], 'volunteerRadios': ['Yes'], 'mentorTrainingRadios': ['Yes'],
        'connectingWithMentorsRadios': ['Yes'], 'studentsInterestedRadios': ['no']}

        response = self.client.post('/update_ally_profile/', dictionary, follow=True)

        message = list(response.context['messages'])[0]
        self.assertIn("Profile updated!", message.message)

    def test_update_profile_fail_for_nonadmin(self):
        """
        Update profile for nonadmin
        """
        self.user.is_staff = False
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:ally-dashboard'), follow=True)
        self.assertContains(
            response, "Science Alliance Portal", html=True
        )
        response = self.client.get('/update_ally_profile/', {'username': self.ally_user}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Science Alliance Portal", html=True
        )
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Access Denied!")

    def test_stem_aor_filter_for_nonadmin(self):
        """
        Show all allies conforming to stem aor filters
        """
        self.user.is_staff = False
        self.user.is_active = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        # Should return no allies
        response = self.client.post(
            '/ally-dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'stemGradCheckboxes': ['Bioinformatics'],
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, "No allies are available.", html=True
        )

        # Should find our johndoe
        response = self.client.post(
            '/ally-dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'stemGradCheckboxes': ['Physics'],
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, self.ally_user.first_name + ' ' + self.ally_user.last_name, html=True
        )


class AdminUpdateProfileAndPasswordTests(TestCase):
    """
    Unit test for update profile feature for admin and to reset their passwords
    """

    def setUp(self):
        self.username = 'Admin_1'
        self.password = 'admin_password1'
        self.email = 'email@test.com'
        self.client = Client()
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

    def test_change_password_page_for_admin(self):
        """
        Show Change Password page for Admin
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:change_password'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Change Password", html=True
        )

    def test_change_password_page_for_ally(self):
        """
        Show Change Password page for Ally
        """
        self.user.is_staff = False
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:change_password'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_update_profile_page_for_admin(self):
        """
        Show Change Password page for Admin
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-admin_profile'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Update Admin Profile", html=True
        )

    def test_update_profile_page_for_ally(self):
        """
        Show Change Password page for Ally
        """
        self.user.is_staff = False
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-admin_profile'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_failure_mismatched_new_pass_change_password(self):
        """
        If new passwords don't match, a failed message is displayed
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:change_password'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Change Password", html=True
        )
        data = {
            "old_password": "admin_password1",
            "new_password1": "something_random",
            "new_password2": "admin_password2"
        }
        form = PasswordChangeForm(
            user=self.user,
            data=data
        )
        self.assertFalse(form.is_valid())

        response = self.client.post(
            reverse('sap:change_password'), data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Could not Update Password !")

    def test_failure_old_pass_wrong_change_password(self):
        """
        If old password is wrong, a failed message is displayed
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:change_password'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Change Password", html=True
        )
        data = {
            "old_password": "something_random",
            "new_password1": "admin_password2",
            "new_password2": "admin_password2"
        }
        form = PasswordChangeForm(
            user=self.user,
            data=data
        )
        self.assertFalse(form.is_valid())
        response = self.client.post(
            reverse('sap:change_password'), data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Could not Update Password !")

    def test_success_change_password(self):
        """
        If old password is right and new password match then change password
        is successfull and a success message is displayed
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:change_password'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Change Password", html=True
        )
        data = {
            "old_password": "admin_password1",
            "new_password1": "admin_password2",
            "new_password2": "admin_password2"
        }
        form = PasswordChangeForm(
            user=self.user,
            data=data
        )
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse('sap:change_password'), data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Password Updated Successfully !")

    def test_correct_update_profile(self):
        """
        If profile is updated, a success message is displayed
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-admin_profile'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Update Admin Profile", html=True
        )

        form = UpdateAdminProfileForm(
            data={"username": "Admin_2", "email": "admin@admin.com"})
        self.assertTrue(form.is_valid())
        response = self.client.post(
            reverse('sap:sap-admin_profile'), data={"username": "Admin_2", "email": "admin@admin.com"}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Profile Updated !")

    def test_fail_update_profile(self):
        """
        If profile is not updated, a failed message is displayed
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-admin_profile'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Update Admin Profile", html=True
        )

        form = UpdateAdminProfileForm(
            data={"username": "Admin_1", "email": "admin@admin.com"})
        self.assertFalse(form.is_valid())
        response = self.client.post(
            "/update_profile/", data={"username": "Admin_1", "email": "admin@admin.com"}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(
            message.message, "Could not Update Profile ! Username already exists")
