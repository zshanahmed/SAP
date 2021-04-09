"""
contains unit tests for sap app
"""
import os
import io
from datetime import datetime
from django.db.models import Q
from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, Client  # tests file
import pandas as pd
import numpy as np
import sap.views as views
from .models import Ally, StudentCategories, AllyStudentCategoryRelation, Event, EventAllyRelation
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


userFields = ['last_login', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined']
allyFields = ['user_type', 'area_of_research', 'openings_in_lab_serving_at', 'description_of_research_done_at_lab',
              'interested_in_mentoring', 'interested_in_mentor_training', 'willing_to_offer_lab_shadowing',
              'interested_in_connecting_with_other_mentors', 'willing_to_volunteer_for_events', 'works_at',
              'people_who_might_be_interested_in_iba', 'how_can_science_ally_serve_you', 'year', 'major',
              'information_release', 'interested_in_being_mentored', 'interested_in_joining_lab',
              'has_lab_experience']
categoryFields = ['under_represented_racial_ethnic', 'first_gen_college_student',
                  'transfer_student', 'lgbtq', 'low_income', 'rural', 'disabled']


def make_big_user():

    bigUser = User.objects.create_user(username="bigUser", password="bigPassword", email="bigEmail@uiowa.edu")
    bigAlly = Ally.objects.create(user=bigUser, user_id=bigUser.id, user_type='Undergraduate Student',
                                  hawk_id=bigUser.username, major='biomedical engineering', year='Freshman',
                                  interested_in_joining_lab=True, has_lab_experience=False,
                                  interested_in_mentoring=False, information_release=True)
    bigCategory = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=False,
                                                   lgbtq=True, low_income=False, disabled=True)
    AllyStudentCategoryRelation.objects.create(ally_id=bigAlly.id, student_category_id=bigCategory.id)

    bigUser1 = User.objects.create_user(username="bigUser1", password="bigPassword", email="bigEmail1@uiowa.edu")
    bigAlly1 = Ally.objects.create(user=bigUser1, user_id=bigUser1.id, user_type='Undergraduate Student',
                                  hawk_id=bigUser1.username, major='biomedical engineering', year='Sophomore',
                                  interested_in_joining_lab=True, has_lab_experience=False,
                                  interested_in_mentoring=False, information_release=True)
    bigCategory1 = StudentCategories.objects.create(rural=False, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=False,
                                                   lgbtq=True, low_income=False, disabled=True)
    AllyStudentCategoryRelation.objects.create(ally_id=bigAlly1.id, student_category_id=bigCategory1.id)

    bigUser2 = User.objects.create_user(username="bigUser2", password="bigPassword", email="bigEmail2@uiowa.edu")
    bigAlly2 = Ally.objects.create(user=bigUser2, user_id=bigUser2.id, user_type='Undergraduate Student',
                                  hawk_id=bigUser2.username, major='biomedical engineering', year='Junior',
                                  interested_in_joining_lab=True, has_lab_experience=False,
                                  interested_in_mentoring=False, information_release=True)
    bigCategory2 = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=False,
                                                   lgbtq=True, low_income=False, disabled=True)
    AllyStudentCategoryRelation.objects.create(ally_id=bigAlly2.id, student_category_id=bigCategory2.id)

    bigUser3 = User.objects.create_user(username="bigUser3", password="bigPassword", email="bigEmail3@uiowa.edu")
    bigAlly3 = Ally.objects.create(user=bigUser3, user_id=bigUser3.id, user_type='Undergraduate Student',
                                  hawk_id=bigUser3.username, major='biomedical engineering', year='Senior',
                                  interested_in_joining_lab=True, has_lab_experience=False,
                                  interested_in_mentoring=False, information_release=True)
    bigCategory3 = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=False,
                                                   lgbtq=True, low_income=False, disabled=True)
    AllyStudentCategoryRelation.objects.create(ally_id=bigAlly3.id, student_category_id=bigCategory3.id)

    bigUser4 = User.objects.create_user(username="bigUser4", password="bigPassword", email="bigEmail4@uiowa.edu")
    bigAlly4 = Ally.objects.create(user=bigUser4, user_id=bigUser4.id, user_type='Staff',
                                  hawk_id=bigUser4.username, major='biomedical engineering', year='Senior',
                                  interested_in_joining_lab=True, has_lab_experience=False,
                                  interested_in_mentoring=False, information_release=True)
    bigCategory4 = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=False,
                                                   lgbtq=True, low_income=False, disabled=True)
    AllyStudentCategoryRelation.objects.create(ally_id=bigAlly4.id, student_category_id=bigCategory4.id)

    bigUser5 = User.objects.create_user(username="bigUser5", password="bigPassword", email="bigEmail5@uiowa.edu")
    bigAlly5 = Ally.objects.create(user=bigUser5, user_id=bigUser5.id, user_type='Faculty',
                                  hawk_id=bigUser5.username, major='biomedical engineering', year='Senior',
                                  interested_in_joining_lab=True, has_lab_experience=False,
                                  interested_in_mentoring=False, information_release=True)
    bigCategory5 = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=False,
                                                   lgbtq=True, low_income=False, disabled=True)
    AllyStudentCategoryRelation.objects.create(ally_id=bigAlly5.id, student_category_id=bigCategory5.id)

    bigUser6 = User.objects.create_user(username="bigUser6", password="bigPassword", email="bigEmail6@uiowa.edu")
    bigAlly6 = Ally.objects.create(user=bigUser6, user_id=bigUser6.id, user_type='Graduate Student',
                                  hawk_id=bigUser6.username, major='biomedical engineering', year='Senior',
                                  interested_in_joining_lab=True, has_lab_experience=False,
                                  interested_in_mentoring=False, information_release=True)
    bigCategory6 = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=False,
                                                   lgbtq=True, low_income=False, disabled=True)
    AllyStudentCategoryRelation.objects.create(ally_id=bigAlly6.id, student_category_id=bigCategory6.id)

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
        local_df1, _ = views.UploadAllies.cleanupFrame(self.data_frame_1)
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
        self.user.save()
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

        self.ally_user = User.objects.create_user(username='john2',
                                                  email='john2@uiowa.edu',
                                                  password='johndoe2',
                                                  first_name='John2',
                                                  last_name='Doe')

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

    def test_get(self):
        """
        test to check if the create event page is rendered properly
        """
        response = self.client.get('/create_event/')
        self.assertEqual(response.status_code, 200)

    def test_invite_all(self):
        """
        test to check if every ally is invited if the admin decides to invite all
        """
        response = self.client.post('/create_event/', {
            'csrfmiddlewaretoken': ['gr9bKWMJLFrJZfcdKkdRhlyKLI0JeTh2ZefMhjulIFuY05e6romNm1CvLZUKa0zG'],
            'event_title': ['title of the event'],
            'event_description': ['description of the event'],
            'event_location': ['https://zoom.us/abc123edf'],
            'event_date_time': ['2021-03-31T15:32'],
            'invite_all': 'true'
        })

        url = response.url
        event = Event.objects.filter(title='title of the event')
        assert url == '/dashboard'
        assert event.exists()
        assert EventAllyRelation.objects.filter(event=event[0], ally=self.ally).exists()

    def test_invite_biochem_student(self):
        """
        test to check invited if the admin decides to only biochem students
        """
        response = self.client.post('/create_event/', {
            'csrfmiddlewaretoken': ['gr9bKWMJLFrJZfcdKkdRhlyKLI0JeTh2ZefMhjulIFuY05e6romNm1CvLZUKa0zG'],
            'event_title': ['title of the event 2'],
            'event_description': ['description of the event 2'],
            'event_location': ['https://zoom.us/abc123edf2'],
            'event_date_time': ['2021-03-31T15:32'],
            'role_selected': ['Graduate Student'],
            'mentor_status': ['Mentors', 'Mentees'],
            'research_area': ['Biochemistry']
        })

        url = response.url
        event = Event.objects.filter(title='title of the event 2')
        assert url == '/dashboard'
        assert event.exists()
        assert EventAllyRelation.objects.filter(event=event[0], ally=self.ally).exists()

    def test_invite_special_category_student(self):
        """
        test to check if only allies belonging to special categories are invited for an event
        """
        response = self.client.post('/create_event/', {
            'csrfmiddlewaretoken': ['gr9bKWMJLFrJZfcdKkdRhlyKLI0JeTh2ZefMhjulIFuY05e6romNm1CvLZUKa0zG'],
            'event_title': ['title of the event 3'],
            'event_description': ['description of the event 3'],
            'event_location': ['https://zoom.us/abc123edf2'],
            'event_date_time': ['2021-03-31T15:32'],
            'special_category': ['First generation college-student', 'Rural', 'Low-income',
                                 'Underrepresented racial/ethnic minority', 'Disabled', 'Transfer Student', 'LGBTQ'],
        })

        url = response.url
        event = Event.objects.filter(title='title of the event 3')
        assert url == '/dashboard'
        assert event.exists()
        assert EventAllyRelation.objects.filter(event=event[0], ally=self.ally).exists()


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
        self.assertEqual(response.status_code, HTTPStatus.OK)


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

class TestAnalyticsPage(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='admin_password1')
        self.bigCategory = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                   under_represented_racial_ethnic=True, transfer_student=True,
                                                   lgbtq=True, low_income=True, disabled=True)
        make_big_user()
        self.undergrads = [Ally.objects.filter(hawk_id="bigUser")[0],
                           Ally.objects.filter(hawk_id="bigUser1")[0],
                           Ally.objects.filter(hawk_id="bigUser2")[0],
                           Ally.objects.filter(hawk_id="bigUser3")[0],]

        self.bigUsers = Ally.objects.filter(Q(hawk_id__startswith='bigUser'))

    def test_get_analytics(self):
        """
        Test good respone from the Analytics page.
        """
        response = self.client.get(reverse('sap:sap-analytics'))
        self.assertEqual(response.status_code, 302)

    def test_num_per_Category(self):
        categoryList = [self.bigCategory]

        categoryList = views.AnalyticsView.determineNumPerCategory(categoryList)

        self.assertEqual(categoryList, [1, 1, 1, 1, 1, 1, 1])

    def test_find_category(self):
        ally = [Ally.objects.filter(hawk_id="bigUser")[0]]
        relation = AllyStudentCategoryRelation.objects.all()
        categories = StudentCategories.objects.all()
        categoryRelation = relation.filter(ally_id=ally[0].id)
        category = categories.filter(id=categoryRelation[0].student_category_id)
        categories = views.AnalyticsView.findTheCategories(ally, relation, categories)

        self.assertEqual(category[0].id, categories[0].id)

    def test_numUndergrad(self):
        numPerYear = views.AnalyticsView.undergradPerYear(self.undergrads)
        self.assertEqual(numPerYear, [1, 1, 1, 1])

    def test_getYear(self):
        years, yearsUndergrad = views.AnalyticsView.findYears(self.bigUsers)
        yearDict = {datetime.strftime(datetime.now(), "%Y"): [0, 0, 0]}
        yearDict1 = {datetime.strftime(datetime.now(), "%Y"): 0}
        self.assertEqual(years, yearDict)
        self.assertEqual(yearsUndergrad, yearDict1)

    def test_userTypePerYear(self):
        yearDict = {datetime.strftime(datetime.now(), "%Y"): [0, 0, 0]}
        yearDict1 = {datetime.strftime(datetime.now(), "%Y"): 0}
        years, undergradYears = views.AnalyticsView.userTypePerYear(self.bigUsers, yearDict, yearDict1)
        yearDict = {datetime.strftime(datetime.now(), "%Y"): [1, 1, 1]}
        yearDict1 = {datetime.strftime(datetime.now(), "%Y"): 4}
        self.assertEqual(years, yearDict)
        self.assertEqual(undergradYears, yearDict1)

    def test_cleanUndergradDic(self):
        yearDict = {datetime.strftime(datetime.now(), "%Y"): [0, 0, 0]}
        yearDict1 = {datetime.strftime(datetime.now(), "%Y"): 0}
        years, undergradYears = views.AnalyticsView.userTypePerYear(self.undergrads, yearDict, yearDict1)
        years, numbers = views.AnalyticsView.cleanUndergradDic(undergradYears)
        self.assertEqual(years, [int(datetime.strftime(datetime.now(), "%Y"))])
        self.assertEqual(numbers, [4])

    def test_cleanOtherDic(self):
        yearDict = {datetime.strftime(datetime.now(), "%Y"): [0, 0, 0]}
        yearDict1 = {datetime.strftime(datetime.now(), "%Y"): 0}
        years, undergradYears = views.AnalyticsView.userTypePerYear(self.bigUsers, yearDict, yearDict1)
        cleanedYears, cleanedOther = views.AnalyticsView.cleanOtherDic(years)
        self.assertEqual(cleanedYears, [int(datetime.strftime(datetime.now(), "%Y"))])
        self.assertEqual(cleanedOther, [[1], [1], [1]])