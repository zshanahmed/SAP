"""
contains unit tests for sap app
"""
import os
import io
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, Client  # tests file
import pandas as pd
import numpy as np
import sap.views as views
from .models import Ally, StudentCategories, AllyStudentCategoryRelation, Event, EventAllyRelation


User = get_user_model()


def wack_test_db():
    """
    Delete everything from the database
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
categoryFields = ['under_represented_racial_ethnic', 'first_gen_college_student', 'transfer_student', 'lgbtq', 'low_income', 'rural']


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
                                                            lgbtq=True, low_income=True)
        self.categories3 = StudentCategories.objects.create(rural=True, first_gen_college_student=False,
                                                            under_represented_racial_ethnic=True, transfer_student=True,
                                                            lgbtq=True, low_income=False)
        self.categories4 = StudentCategories.objects.create(rural=True, first_gen_college_student=False,
                                                            under_represented_racial_ethnic=True, transfer_student=False,
                                                            lgbtq=True, low_income=False)

        AllyStudentCategoryRelation.objects.create(ally_id=self.ally2.id, student_category_id=self.categories2.id)
        AllyStudentCategoryRelation.objects.create(ally_id=self.ally3.id, student_category_id=self.categories3.id)
        AllyStudentCategoryRelation.objects.create(ally_id=self.ally4.id, student_category_id=self.categories4.id)

        columns = []
        columns = DownloadAlliesTest.fields_helper(User, columns)
        columns = DownloadAlliesTest.fields_helper(Ally, columns)
        columns = DownloadAlliesTest.fields_helper(StudentCategories, columns)

        data = []
        user1 = DownloadAlliesTest.cleanup(self.user1.__dict__) + \
                DownloadAlliesTest.cleanup(self.ally1.__dict__) + [None, None, None, None, None, None]
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
        upload test for file that has correct inputs
        """
        self.client.login(username='glib', password='macaque')
        name = './pytests/assets/allies.csv'
        abs_path = os.path.abspath(name)

        with open(abs_path, 'rb') as file_name:
            headers = {
                'HTTP_CONTENT_TYPE': 'multipart/form-data',
                'HTTP_CONTENT_DISPOSITION': 'attachment; filename=' + 'allies.csv'}
            #            request = factory.post(reverse(string, args=[args]), {'file': data},
            #                                   **headers)
            response = self.client.post(reverse('sap:upload_allies'), {'file': file_name}, **headers)

        self.assertEqual(response.status_code, 200)

        allies = Ally.objects.all()
        self.assertEqual(len(allies), 5)

        local_df = UploadFileTest.make_frame()

        pd.testing.assert_frame_equal(local_df, self.data_frame)

    def test_add_allies_file_type_two(self):
        """
        upload test for file that has correct inputs
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
            #            request = factory.post(reverse(string, args=[args]), {'file': data},
            #                                   **headers)
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

        self.ally_user = User.objects.create_user(username='john',
                                                  email='john@uiowa.edu',
                                                  password='johndoe',
                                                  first_name='John',
                                                  last_name='Doe')

        self.ally = Ally.objects.create(
            user=self.ally_user,
            hawk_id='johndoe',
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
                                 'Underrepresented racial/ethnic minority', 'Transfer Student', 'LGBTQ'],
        })

        url = response.url
        event = Event.objects.filter(title='title of the event 3')
        assert url == '/dashboard'
        assert event.exists()
        assert EventAllyRelation.objects.filter(event=event[0], ally=self.ally).exists()
