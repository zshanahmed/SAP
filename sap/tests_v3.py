"""
contains unit tests for sap app
"""
import os
import io
from datetime import datetime
from http import HTTPStatus
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, Client  # tests file
import pandas as pd
import numpy as np
import sap.views as views
import sap.views_v2 as views_v2
from .models import Ally, StudentCategories, AllyStudentCategoryRelation, Event, EventInviteeRelation
from .tests import create_ally

User = get_user_model()


def wack_test_db():
    """
    Delete users/allies/categories from the database
    """
    User.objects.all().delete()
    Ally.objects.all().delete()
    StudentCategories.objects.all().delete()
    AllyStudentCategoryRelation.objects.all().delete()


userFields = views_v2.userFields
allyFields = views_v2.allyFields
categoryFields = views_v2.categoryFields


def make_big_undergrad():
    """
    Makes 4 undergrads - one of each type (fresh, soph, jun, sen)
    """
    big_user = User.objects.create_user(username="big_user", password="bigPassword", email="bigEmail@uiowa.edu")
    big_ally = Ally.objects.create(user=big_user, user_id=big_user.id, user_type='Undergraduate Student',
                                  hawk_id=big_user.username, major='biomedical engineering', year='Freshman',
                                  interested_in_joining_lab=True, has_lab_experience=False,
                                  interested_in_mentoring=False, information_release=True)
    big_category = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=False,
                                                   lgbtq=True, low_income=False, disabled=True)
    AllyStudentCategoryRelation.objects.create(ally_id=big_ally.id, student_category_id=big_category.id)

    big_user1 = User.objects.create_user(username="big_user1", password="bigPassword", email="bigEmail1@uiowa.edu")
    big_ally1 = Ally.objects.create(user=big_user1, user_id=big_user1.id, user_type='Undergraduate Student',
                                  hawk_id=big_user1.username, major='biomedical engineering', year='Sophomore',
                                  interested_in_joining_lab=True, has_lab_experience=False,
                                  interested_in_mentoring=False, information_release=True)
    big_category1 = StudentCategories.objects.create(rural=False, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=False,
                                                   lgbtq=True, low_income=False, disabled=True)
    AllyStudentCategoryRelation.objects.create(ally_id=big_ally1.id, student_category_id=big_category1.id)

    big_user2 = User.objects.create_user(username="big_user2", password="bigPassword", email="bigEmail2@uiowa.edu")
    big_ally2 = Ally.objects.create(user=big_user2, user_id=big_user2.id, user_type='Undergraduate Student',
                                  hawk_id=big_user2.username, major='biomedical engineering', year='Junior',
                                  interested_in_joining_lab=True, has_lab_experience=False,
                                  interested_in_mentoring=False, information_release=True)
    big_category2 = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=False,
                                                   lgbtq=True, low_income=False, disabled=True)
    AllyStudentCategoryRelation.objects.create(ally_id=big_ally2.id, student_category_id=big_category2.id)

    big_user3 = User.objects.create_user(username="big_user3", password="bigPassword", email="bigEmail3@uiowa.edu")
    big_ally3 = Ally.objects.create(user=big_user3, user_id=big_user3.id, user_type='Undergraduate Student',
                                  hawk_id=big_user3.username, major='biomedical engineering', year='Senior',
                                  interested_in_joining_lab=True, has_lab_experience=False,
                                  interested_in_mentoring=False, information_release=True)
    big_category3 = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=False,
                                                   lgbtq=True, low_income=False, disabled=True)
    AllyStudentCategoryRelation.objects.create(ally_id=big_ally3.id, student_category_id=big_category3.id)


def make_big_other():
    """
    Makes 3 of the other type of user (staff, grad, faculty)
    """
    big_user4 = User.objects.create_user(username="big_user4", password="bigPassword", email="bigEmail4@uiowa.edu")
    big_ally4 = Ally.objects.create(user=big_user4, user_id=big_user4.id, user_type='Staff',
                                  hawk_id=big_user4.username, major='biomedical engineering', year='Senior',
                                  interested_in_joining_lab=True, has_lab_experience=False,
                                  interested_in_mentoring=False, information_release=True)
    big_category4 = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=False,
                                                   lgbtq=True, low_income=False, disabled=True)
    AllyStudentCategoryRelation.objects.create(ally_id=big_ally4.id, student_category_id=big_category4.id)

    big_user5 = User.objects.create_user(username="big_user5", password="bigPassword", email="bigEmail5@uiowa.edu")
    big_ally5 = Ally.objects.create(user=big_user5, user_id=big_user5.id, user_type='Faculty',
                                  hawk_id=big_user5.username, major='biomedical engineering', year='Senior',
                                  interested_in_joining_lab=True, has_lab_experience=False,
                                  interested_in_mentoring=False, information_release=True)
    big_category5 = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=False,
                                                   lgbtq=True, low_income=False, disabled=True)
    AllyStudentCategoryRelation.objects.create(ally_id=big_ally5.id, student_category_id=big_category5.id)

    big_user6 = User.objects.create_user(username="big_user6", password="bigPassword", email="bigEmail6@uiowa.edu")
    big_ally6 = Ally.objects.create(user=big_user6, user_id=big_user6.id, user_type='Graduate Student',
                                  hawk_id=big_user6.username, major='biomedical engineering', year='Senior',
                                  interested_in_joining_lab=True, has_lab_experience=False,
                                  interested_in_mentoring=False, information_release=True)
    big_category6 = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=False,
                                                   lgbtq=True, low_income=False, disabled=True)
    AllyStudentCategoryRelation.objects.create(ally_id=big_ally6.id, student_category_id=big_category6.id)

class DownloadAlliesTest(TestCase):
    """
    Unit tests for download csv feature
    """

    @staticmethod
    def fields_helper(model, columns):
        """
        helper function for the download csv feature test
        """
        for field in model._meta.get_fields():
            fields = str(field).split(".")[-1]
            if fields in userFields or fields in allyFields or fields in categoryFields:
                columns.append(fields)

        return columns

    @staticmethod
    def cleanup(dictionary):
        """
        function to facilitate cleanup of data
        """
        ar_list = []
        for item in dictionary.items():
            if item[0] in userFields or item[0] in allyFields or item[0] in categoryFields:
                if item[0] == 'date_joined':
                    ar_list.append(item[1].strftime("%b-%d-%Y"))
                else:
                    ar_list.append(item[1])
        return ar_list

    def setUp(self):
        wack_test_db()

        self.client = Client()

        self.loginuser = User.objects.create_user(username='glib', password='macaque', email='staff@uiowa.edu',
                                                  first_name='charlie', last_name='hebdo', is_staff=True)

        self.user1 = User.objects.create_user(username='staff', password='123', email='staff@uiowa.edu',
                                              first_name='charlie', last_name='hebdo')
        self.user2 = User.objects.create_user(username='grad', password='123', email='gradf@uiowa.edu',
                                              first_name='wolfgang', last_name='kremple')
        self.user3 = User.objects.create_user(username='faculty', password='123', email='faculty@uiowa.edu',
                                              first_name='Elias', last_name='Shaeffer')
        self.user4 = User.objects.create_user(username='undergrad', password='123', email='undergrad@uiowa.edu',
                                              first_name='Zeeshan', last_name='Ahmed')

        self.ally1 = Ally.objects.create(user=self.user1, user_type='Staff', hawk_id=self.user1.username,
                                         people_who_might_be_interested_in_iba=True,
                                         how_can_science_ally_serve_you='help_me 0:')
        self.ally2 = Ally.objects.create(user=self.user2, user_type='Graduate Student', hawk_id=self.user2.username,
                                         area_of_research='Bioinformatics',
                                         interested_in_mentoring=False,
                                         willing_to_offer_lab_shadowing=True,
                                         interested_in_connecting_with_other_mentors=False,
                                         willing_to_volunteer_for_events=True,
                                         interested_in_mentor_training=False
                                         )
        self.ally3 = Ally.objects.create(user=self.user3, user_type='Faculty', hawk_id=self.user3.username,
                                         area_of_research='Biology',
                                         openings_in_lab_serving_at=True,
                                         description_of_research_done_at_lab='Big biology my guy',
                                         interested_in_mentoring=True,
                                         willing_to_volunteer_for_events=True,
                                         interested_in_mentor_training=True
                                         )
        self.ally4 = Ally.objects.create(user=self.user4, user_type='Undergraduate Student', hawk_id=self.user4.username,
                                         major='biomedical engineering', year='Freshman',
                                         interested_in_joining_lab=True, has_lab_experience=False,
                                         interested_in_mentoring=False,
                                         information_release=True
                                         )

        self.categories2 = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                            under_represented_racial_ethnic=True, transfer_student=True,
                                                            lgbtq=True, low_income=True, disabled=True)
        self.categories3 = StudentCategories.objects.create(rural=True, first_gen_college_student=False,
                                                            under_represented_racial_ethnic=True, transfer_student=True,
                                                            lgbtq=True, low_income=False, disabled=True)
        self.categories4 = StudentCategories.objects.create(rural=True, first_gen_college_student=False,
                                                            under_represented_racial_ethnic=True, transfer_student=False,
                                                            lgbtq=True, low_income=False, disabled=True)

        AllyStudentCategoryRelation.objects.create(ally_id=self.ally2.id, student_category_id=self.categories2.id)
        AllyStudentCategoryRelation.objects.create(ally_id=self.ally3.id, student_category_id=self.categories3.id)
        AllyStudentCategoryRelation.objects.create(ally_id=self.ally4.id, student_category_id=self.categories4.id)

        columns = []
        columns = DownloadAlliesTest.fields_helper(User, columns)
        columns = DownloadAlliesTest.fields_helper(Ally, columns)
        columns = DownloadAlliesTest.fields_helper(StudentCategories, columns)

        data = []
        user1 = DownloadAlliesTest.cleanup(self.user1.__dict__) + \
                DownloadAlliesTest.cleanup(self.ally1.__dict__) + [None, None, None, None, None, None, None]
        user2 = DownloadAlliesTest.cleanup(self.user2.__dict__) + \
                DownloadAlliesTest.cleanup(self.ally2.__dict__) + DownloadAlliesTest.cleanup(self.categories2.__dict__)

        user3 = DownloadAlliesTest.cleanup(self.user3.__dict__) + \
                DownloadAlliesTest.cleanup(self.ally3.__dict__) + DownloadAlliesTest.cleanup(self.categories3.__dict__)
        user4 = DownloadAlliesTest.cleanup(self.user4.__dict__) + \
                DownloadAlliesTest.cleanup(self.ally4.__dict__) + DownloadAlliesTest.cleanup(self.categories4.__dict__)

        data.append(user1)
        data.append(user2)
        data.append(user3)
        data.append(user4)

        data_frame = pd.DataFrame(data=data, columns=columns)
        data_frame = data_frame.replace(0, False)
        data_frame = data_frame.replace(1, True)
        data_frame.fillna(value=np.nan, inplace=True)
        data_frame = data_frame.replace('', np.nan)
        self.data_frame = data_frame

    def test_download_data(self):
        """
        Testing the download data feature. If I create 4 allies in the database - one of each type, complete with
        ally categories then they should each appear in the CSV
        """
        self.client.login(username='glib', password='macaque')
        response = self.client.get(reverse('sap:download_allies'))
        file_content = io.BytesIO(response.content)
        retrieved_data_frame = pd.read_csv(file_content)
        pd.testing.assert_frame_equal(retrieved_data_frame, self.data_frame)

    def test_try_download_as_ally(self):
        """
        Testing the download data feature. I should get a 403 response if I try to get the path as regular user
        """
        self.client.login(username='staff', password='123')
        response = self.client.get(reverse('sap:download_allies'))
        self.assertEqual(response.status_code, 403)


class UploadFileTest(TestCase):
    """
    Unit tests for upload feature
    """

    @staticmethod
    def make_frame():
        """
        helper function for upload file test
        """
        columns = []
        columns = DownloadAlliesTest.fields_helper(User, columns)
        columns = DownloadAlliesTest.fields_helper(Ally, columns)
        columns = DownloadAlliesTest.fields_helper(StudentCategories, columns)

        allies = Ally.objects.all()
        data = []
        for user in allies:
            if user.user_type != "Staff":
                categories = StudentCategories.objects.filter(
                    id=AllyStudentCategoryRelation.objects.filter(ally_id=user.id)[0].student_category_id)[0]
                data.append(DownloadAlliesTest.cleanup(User.objects.filter(id=user.user_id)[0].__dict__) +
                            DownloadAlliesTest.cleanup(user.__dict__) + DownloadAlliesTest.cleanup(categories.__dict__))
            else:
                data.append(DownloadAlliesTest.cleanup(User.objects.filter(id=user.user_id)[0].__dict__) +
                            DownloadAlliesTest.cleanup(user.__dict__) + [None, None, None, None, None, None])

        data_frame = pd.DataFrame(columns=columns, data=data)
        data_frame = data_frame.replace(0, False)
        data_frame = data_frame.replace(1, True)
        data_frame.fillna(value=np.nan, inplace=True)
        data_frame = data_frame.replace('', np.nan)
        return data_frame

    def setUp(self):
        """
        Set up the test
        """
        wack_test_db()
        self.client = Client()
        self.login_user = User.objects.create_user(username='glib', password='macaque', email='staff@uiowa.edu',
                                                   first_name='charlie', last_name='hebdo', is_staff=True)

        self.bad_guy = User.objects.create_user(username='bad', password='badguy1234', email='badguy@uiowa.edu',
                                                first_name='reallyBadGuy', last_name='I\'m bad')

        self.data_frame = pd.read_csv('./pytests/assets/allies.csv')
        self.data_frame_1 = pd.read_excel('./pytests/assets/allies2.xlsx')

    def test_post_not_staff(self):
        """
        upload file: testing files that has inappropriate input
        """
        self.client.login(username='bad', password='badguy1234')
        with open('./pytests/assets/allies.csv', 'r') as input_file:
            response = self.client.post(reverse('sap:upload_allies'), {'attachment': input_file})
        self.assertEqual(response.status_code, 403)

    def test_add_allies_file_type_one(self):
        """
        Test the first filetype which has the same format as the file found in the DownloadAllies view.
        """
        self.client.login(username='glib', password='macaque')
        name = './pytests/assets/allies.csv'
        abs_path = os.path.abspath(name)

        with open(abs_path, 'rb') as file_name:
            headers = {
                'HTTP_CONTENT_TYPE': 'multipart/form-data',
                'HTTP_CONTENT_DISPOSITION': 'attachment; filename=' + 'allies.csv'}
            response = self.client.post(reverse('sap:upload_allies'), {'file': file_name}, **headers)

        self.assertEqual(response.status_code, 200)

        allies = Ally.objects.all()
        self.assertEqual(len(allies), 5)

        local_df = UploadFileTest.make_frame()

        pd.testing.assert_frame_equal(local_df, self.data_frame)

    def test_add_allies_file_type_two(self):
        """
        Test the second file type, which is actually the one which the customer is using to store data.
        """
        wack_test_db()
        self.login_user = User.objects.create_user(username='glib', password='macaque', email='staff@uiowa.edu',
                                                   first_name='charlie', last_name='hebdo', is_staff=True)
        self.client.login(username='glib', password='macaque')

        name = './pytests/assets/allies2.xlsx'
        abs_path = os.path.abspath(name)
        with open(abs_path, 'rb') as file_name:
            headers = {
                'HTTP_CONTENT_TYPE': 'multipart/form-data',
                'HTTP_CONTENT_DISPOSITION': 'attachment; filename=' + 'allies2.xlsx'}
            response = self.client.post(reverse('sap:upload_allies'), {'file': file_name}, **headers)
        self.assertEqual(response.status_code, 200)

        local_df = UploadFileTest.make_frame()
        local_df1, _ = views_v2.UploadAllies.cleanup_frame(self.data_frame_1)
        local_df1 = local_df1[userFields + allyFields + categoryFields]
        local_df['last_login'] = ''
        for category in categoryFields:
            local_df[category][3] = False
        local_df = local_df.fillna(value='')
        pd.testing.assert_frame_equal(local_df, local_df1)


class CreateEventTests(TestCase):
    """
    Unit tests for create events feature
    """

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.user = User.objects.create_user(self.username, 'email@test.com', self.password)
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

        self.ally_user = User.objects.create_user(username='john2',
                                                  email='john2@uiowa.edu',
                                                  password='johndoe2',
                                                  first_name='John2',
                                                  last_name='Doe',
                                                  is_active=True,
                                                  )

        self.ally = Ally.objects.create(
            user=self.ally_user,
            hawk_id='johndoe2',
            user_type='Graduate Student',
            works_at='College of Engineering',
            area_of_research='Biochemistry',
            major='Electrical Engineering',
            willing_to_volunteer_for_events=True
        )

        self.category = StudentCategories.objects.create(lgbtq=True)
        self.student_ally_rel = AllyStudentCategoryRelation.objects.create(
            ally=self.ally,
            student_category=self.category,
        )

    def test_get_is_staff(self):
        """
        test to check if the create event page is rendered properly, staff permission
        """
        response = self.client.get('/create_event/')
        self.assertEqual(response.status_code, 200)

    def test_get_not_is_staff(self):
        """
        test to check if the create event page is rendered properly
        """
        self.user.is_staff = False
        self.user.save()
        response = self.client.get('/create_event/')
        self.assertEqual(response.status_code, 403)

    def test_invite_all(self):
        """
        test to check if every ally is invited if the admin decides to invite all
        """
        response = self.client.post('/create_event/', {
            'csrfmiddlewaretoken': ['gr9bKWMJLFrJZfcdKkdRhlyKLI0JeTh2ZefMhjulIFuY05e6romNm1CvLZUKa0zG'],
            'event_title': ['title of the event'],
            'event_description': ['description of the event'],
            'event_location': ['https://zoom.us/abc123edf'],
            'event_start_time': ['2021-03-31T15:32'],
            'event_end_time': ['2021-04-30T15:32'],
            'invite_all': 'true',
        })

        url = response.url
        event = Event.objects.filter(title='title of the event')
        assert url == '/calendar'
        assert event.exists()
        assert EventInviteeRelation.objects.filter(event=event[0], ally=self.ally).exists()

    def test_invite_biochem_student(self):
        """
        test to check invited if the admin decides to only biochem students
        """
        response = self.client.post('/create_event/', {
            'csrfmiddlewaretoken': ['gr9bKWMJLFrJZfcdKkdRhlyKLI0JeTh2ZefMhjulIFuY05e6romNm1CvLZUKa0zG'],
            'event_title': ['title of the event 2'],
            'event_description': ['description of the event 2'],
            'event_location': ['https://zoom.us/abc123edf2'],
            'event_start_time': ['2021-03-31T15:32'],
            'event_end_time': ['2021-04-30T15:32'],
            'role_selected': ['Graduate Student'],
            'school_year_selected': ['Sophomore'],
            'mentor_status': ['Mentors', 'Mentees'],
            'research_area': ['Biochemistry']
        })

        url = response.url
        event = Event.objects.filter(title='title of the event 2')
        assert url == '/calendar'
        assert event.exists()
        assert EventInviteeRelation.objects.filter(event=event[0], ally=self.ally).exists()

    def test_invite_special_category_student(self):
        """
        test to check if only allies belonging to special categories are invited for an event
        """
        response = self.client.post('/create_event/', {
            'csrfmiddlewaretoken': ['gr9bKWMJLFrJZfcdKkdRhlyKLI0JeTh2ZefMhjulIFuY05e6romNm1CvLZUKa0zG'],
            'event_title': ['title of the event 3'],
            'event_description': ['description of the event 3'],
            'event_location': ['https://zoom.us/abc123edf2'],
            'event_start_time': ['2021-03-31T15:32'],
            'event_end_time': ['2021-04-30T15:32'],
            'special_category': ['First generation college-student', 'Rural', 'Low-income',
                                 'Underrepresented racial/ethnic minority', 'Disabled', 'Transfer Student', 'LGBTQ'],
        })

        url = response.url
        event = Event.objects.filter(title='title of the event 3')
        assert url == '/calendar'
        assert event.exists()
        assert EventInviteeRelation.objects.filter(event=event[0], ally=self.ally).exists()

    def test_end_date_less_than_start_date(self):
        """
        Checks if the post function validates that start time < end time
        """
        response = self.client.post('/create_event/',
            {'csrfmiddlewaretoken': ['nhfQKKeiz3GSWp10SsXcVciNJiIm50yLc5vX81YXodQNB8ynsI6aeVFeF70b0580'],
             'event_title': ['Hackathon UIOWA'],
             'event_description': ['Hackathon for competition in different areas'],
             'event_start_time': ['2021-04-09T14:38'],
             'event_end_time': ['2021-04-07T14:38'],
             'event_allday': ['event_allday'],
             'event_location': ['Seamans Hall'],
             'invite_all': ['invite_all'],
             'role_selected': ['Staff', 'Graduate Student', 'Undergraduate Student', 'Faculty'],
             'mentor_status': ['Mentors', 'Mentees'],
             'special_category': ['First generation college-student', 'Rural', 'Low-income',
                                  'Underrepresented racial/ethnic minority',
                                  'Disabled', 'Transfer Student', 'LGBTQ'],
             'research_area': ['Biochemistry', 'Bioinformatics', 'Biology',
                               'Biomedical Engineering', 'Chemical Engineering', 'Chemistry',
                               'Computer Science and Engineering', 'Environmental Science',
                               'Health and Human Physiology', 'Mathematics', 'Microbiology',
                               'Neuroscience', 'Nursing', 'Physics', 'Psychology']
             }, follow= True)
        self.assertContains(
            response, "End time cannot be less than start time!", html=True
        )

class CreateAdminViewTest(TestCase):
    """
    Unit tests for creating new IBA admins
    """

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()
        self.user = User.objects.create_user(self.username, 'email@test.com', self.password)
        self.client.login(username=self.username, password=self.password)
        self.user.is_staff = True
        self.user.save()

    def test_get(self):
        """
        test get create admin page
        """
        response = self.client.get('/create_iba_admin/')
        self.assertEqual(response.status_code, 200)

    def test_post_missing_data(self):
        """
        Check if email entered for new admin is non empty
        """
        response = self.client.post('/create_iba_admin/', {
            'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
            'current_username': ['iba_admin'],
            'current_password': ['iba_sep_1'], 'new_email': [''],
            'new_username': ['iba_admin'], 'new_password': ['iba_sep_1'],
            'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_post_invalid_credentials(self):
        """
        check if the current iba admin username and password are valid
        """
        response = self.client.post('/create_iba_admin/', {
            'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
            'current_username': ['admin'],
            'current_password': ['admin_assword1'], 'new_email': ['emailGuy@email.com'],
            'new_username': ['iba_admin'], 'new_password': ['iba_sep_1'],
            'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_post_new_username_that_exists(self):
        """
        check if the new admin's name is unique
        """
        response = self.client.post('/create_iba_admin/', {
            'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
            'current_username': ['admin'],
            'current_password': ['admin_password1'], 'new_email': ['emailGuy@email.com'],
            'new_username': ['admin'], 'new_password': ['admin_password1'],
            'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_post_non_matching_new_password(self):
        """
        verify if the password and confirm password fields have the same value
        """
        response = self.client.post('/create_iba_admin/', {
            'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
            'current_username': ['admin'],
            'current_password': ['admin_password1'], 'new_email': ['emailGuy@email.com'],
            'new_username': ['admin1'], 'new_password': ['admin_password1'],
            'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_good_create_admin(self):
        """
        Test if new admin is created in user table if all fields are valid
        """
        response = self.client.post('/create_iba_admin/', {
            'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
            'current_username': ['admin'],
            'current_password': ['admin_password1'], 'new_email': ['emailGuy@email.com'],
            'new_username': ['admin1'], 'new_password': ['admin_password1'],
            'repeat_password': ['admin_password1']})

        url = response.url
        assert url == '/dashboard'
        assert User.objects.filter(username='admin1').exists()


class LoginRedirectTests(TestCase):
    """
    Unit tests to verify if the users are redirected to proper page after login
    """

    def setUp(self):
        self.username = 'user'
        self.password = 'user_password1'
        self.email = 'email@test.com'
        self.client = Client()

        self.user = User.objects.create_user(self.username, self.email, self.password)

    def test_login_for_admin(self):
        """
        Admin users are redirected to Dashboard after logging in
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse("sap:login_success"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_login_for_admin_fail(self):
        """
        Invalid password error for admin
        """
        self.client.post("/", {"username": "adm", "password": "admin"})
        response = self.client.get(reverse("sap:home"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_for_nonadmin(self):
        """
        Non-admin users are redirected to About page
        """
        self.user.is_staff = False
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse("sap:login_success"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)


class LogoutRedirectTests(TestCase):
    """
    Unit tests to verify if logout happens properly
    """

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()
        self.user = User.objects.create_user(self.username, 'email@test.com', self.password, is_staff=True)

    def test_logout_for_admin(self):
        """
        test if admin is logged out on click of logout button
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:logout'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, '/')

    def test_logout_for_ally(self):
        """
        test if admin is logged out on click of logout button
        """
        self.user.is_staff = False
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:logout'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, '/')


class AdminAccessTests(TestCase):
    """
    Tests to ensure admin is able to access all the pages on the site
    """

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()

        User.objects.create_user(self.username, 'email@test.com', self.password, is_staff=True)

    def test_dashboard_access_for_admin(self):
        """
        Admin users can access Dashboard
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_analytics_access_for_admin(self):
        """
        Admin users can access Analytics
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-analytics'))
        self.assertEqual(response.status_code, 302)


class NonAdminAccessTests(TestCase):
    """
    Testing allies view of the dashboard
    """

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()

        User.objects.create_user(self.username, 'email@test.com', self.password, is_staff=False)

    def test_dashboard_access_for_nonadmin(self):
        """
        Admin users can access Dashboard
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_analytics_access_for_nonadmin(self):
        """
        Admin users can access Dashboard
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-analytics'))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class AlliesIndexViewTests(TestCase):
    """
    Unit tests for the dashboard an admin views
    """

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()

        user = User.objects.create_user(self.username, 'email@test.com', self.password)
        user.is_staff = True
        user.save()

    def test_no_ally(self):
        """
        If no allies exist, an appropriate message is displayed.
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No allies are available.")
        self.assertQuerysetEqual(response.context['allies_list'], [])

    def test_one_ally(self):
        """
        Only one ally should be displayed on the home page
        """
        self.client.login(username=self.username, password=self.password)
        create_ally('username_1', 'hawk_id_1')
        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertQuerysetEqual(
            response.context['allies_list'],
            ['<Ally: hawk_id_1>']
        )

    def test_two_allies(self):
        """
        Only two allies should be displayed on the home page
        """
        self.client.login(username=self.username, password=self.password)
        create_ally('username_1', 'hawk_id_1')
        create_ally('username_2', 'hawk_id_2')
        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertQuerysetEqual(
            response.context['allies_list'],
            ['<Ally: hawk_id_2>', '<Ally: hawk_id_1>']  # Need to return in the descending order
        )

class CalendarViewTests(TestCase):
    """
    Unit tests for calendar view
    """
    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()

        self.user = User.objects.create_user(self.username, 'email@test.com', self.password)
        self.event = Event.objects.create(title='Internship', description='Internship',
                                          start_time='2021-04-20 21:05:00',
                                          end_time='2021-04-26 21:05:00', location='MacLean')

        self.ally_user = User.objects.create_user('allytesting', 'allyemail@test.com', 'ally_password1')
        self.ally_user.is_staff = False

        self.ally = Ally.objects.create(
            user=self.ally_user,
            hawk_id='johndoe2',
            user_type='Graduate Student',
            works_at='College of Engineering',
            area_of_research='Biochemistry',
            major='Electrical Engineering',
            willing_to_volunteer_for_events=True
        )

        self.category = StudentCategories.objects.create(lgbtq=True)
        self.student_ally_rel = AllyStudentCategoryRelation.objects.create(
            ally=self.ally,
            student_category=self.category
        )

        self.user.is_staff = True
        self.user.save()

        self.event_ally_rel = EventInviteeRelation.objects.create(ally_id=self.ally.id, event_id=self.event.id)

    def test_calendar_access_admin(self):
        """
        Unit tests for admin view on calendar
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:calendar'))
        self.assertContains(response, "Calendar")

    def test_calendar_access_non_admin(self):
        """
        Unit tests for ally view for calendar
        """
        self.client.login(username=self.ally_user, password='ally_password1')
        response = self.client.get(reverse('sap:calendar'))
        self.assertContains(response, "Calendar")
        self.assertContains(response, self.event.title)

    def test_delete_event_admin(self):
        """
        Unit tests for admin to delete event
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get('/delete_event/', {'event_id': self.event.id}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotContains(response, self.event.title, html=True)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Event deleted successfully!")

    def test_delete_event_admin_fail(self):
        """
        Unit tests for admin to delete event
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get('/delete_event/', {'event_id': -1}, follow=True)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Event doesn't exist!")


class TestAnalyticsPage(TestCase):
    """
    Test the analytics page methods/get function
    """
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='admin_password1')
        self.big_category = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=True,
                                                   lgbtq=True, low_income=True, disabled=True)
        make_big_undergrad()
        make_big_other()
        self.undergrads = [Ally.objects.filter(hawk_id="big_user")[0],
                           Ally.objects.filter(hawk_id="big_user1")[0],
                           Ally.objects.filter(hawk_id="big_user2")[0],
                           Ally.objects.filter(hawk_id="big_user3")[0],]

        self.big_users = Ally.objects.filter(Q(hawk_id__startswith='big_user'))

    def test_get_analytics(self):
        """
        Test good response from the Analytics page.
        """
        response = self.client.get(reverse('sap:sap-analytics'))
        self.assertEqual(response.status_code, 302)

    def test_num_per_category(self):
        """
        Test ability of determine num per category to get the number of people per ally category
        """
        category_list = [self.big_category]

        category_list = views.AnalyticsView.determine_num_per_category(category_list)

        self.assertEqual(category_list, [1, 1, 1, 1, 1, 1, 1])

    def test_find_category(self):
        """
        Checks if the category appended to the list of find categories coressponds to correct user
        """
        ally = [Ally.objects.filter(hawk_id="big_user")[0]]
        relation = AllyStudentCategoryRelation.objects.all()
        categories = StudentCategories.objects.all()
        category_relation = relation.filter(ally_id=ally[0].id)
        category = categories.filter(id=category_relation[0].student_category_id)
        categories = views.AnalyticsView.find_the_categories(ally, relation, categories)

        self.assertEqual(category[0].id, categories[0].id)

    def test_num_undergrad(self):
        """
        Looks if the undergrad per year function is returning the right number per year in school
        """
        num_per_year = views.AnalyticsView.undergrad_per_year(self.undergrads)
        self.assertEqual(num_per_year, [1, 1, 1, 1])

    def test_get_year(self):
        """
        Checks if the function that makes the inital dict is working correctly
        """
        years, years_undergrad = views.AnalyticsView.find_years(self.big_users)
        year_dict = {datetime.strftime(datetime.now(), "%Y"): [0, 0, 0]}
        year_dict1 = {datetime.strftime(datetime.now(), "%Y"): 0}
        self.assertEqual(years, year_dict)
        self.assertEqual(years_undergrad, year_dict1)

    def test_user_type_per_year(self):
        """
        Checks if the function is getting the correct number who signed up per year
        """
        year_dict = {datetime.strftime(datetime.now(), "%Y"): [0, 0, 0]}
        year_dict1 = {datetime.strftime(datetime.now(), "%Y"): 0}
        years, undergrad_years = views.AnalyticsView.user_type_per_year(self.big_users, year_dict, year_dict1)
        year_dict = {datetime.strftime(datetime.now(), "%Y"): [1, 1, 1]}
        year_dict1 = {datetime.strftime(datetime.now(), "%Y"): 4}
        self.assertEqual(years, year_dict)
        self.assertEqual(undergrad_years, year_dict1)

    def test_clean_undergrad_dic(self):
        """
        Checks if the dict being cleaned is returned correctly (yearsignedup: numbersigned up that year) for undergrad
        """
        year_dict = {datetime.strftime(datetime.now(), "%Y"): [0, 0, 0]}
        year_dict1 = {datetime.strftime(datetime.now(), "%Y"): 0}
        years, undergrad_years = views.AnalyticsView.user_type_per_year(self.undergrads, year_dict, year_dict1)
        years, numbers = views.AnalyticsView.clean_undergrad_dic(undergrad_years)
        self.assertEqual(years, [int(datetime.strftime(datetime.now(), "%Y"))])
        self.assertEqual(numbers, [4])

    def test_clean_other_dic(self):
        """
        Checks if the dict being cleaned is returned correctly (yearsignedup: numbersigned up that year) for other user
        """
        year_dict = {datetime.strftime(datetime.now(), "%Y"): [0, 0, 0]}
        year_dict1 = {datetime.strftime(datetime.now(), "%Y"): 0}
        years, undergrad_years = views.AnalyticsView.user_type_per_year(self.big_users, year_dict, year_dict1)
        self.assertEqual(undergrad_years, {datetime.strftime(datetime.now(), "%Y"): 4})
        cleaned_years, cleaned_other = views.AnalyticsView.clean_other_dic(years)
        self.assertEqual(cleaned_years, [int(datetime.strftime(datetime.now(), "%Y"))])
        self.assertEqual(cleaned_other, [[1], [1], [1]])
