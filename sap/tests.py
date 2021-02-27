from django.test import TestCase, Client
from .models import Ally
from django.urls import reverse
from django.contrib.auth.models import User


# Create your tests here.
class DummyTests(TestCase):

    def test_true(self):
        self.assertIs(True, True)

    def test_false(self):
        self.assertIs(False, False)


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


class AlliesIndexViewTests(TestCase):

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()

        User.objects.create_user(self.username, 'email@test.com', self.password)

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
            ['<Ally: hawk_id_2>', '<Ally: hawk_id_1>'] # Need to return in the descending order (When the ally record was created in the table)
        )

    '''
    TODO: Once we do performance enhancement - pagination, this test will be useful
    def test_51_allies(self):
        """
        Only 50 allies should be displayed on the home page even if there are more than 50 allies in the database
        """
        self.client.login(username=self.username, password=self.password)

        for i in range(52):
            create_ally('username_{}'.format(str(i)), 'hawk_id_{}'.format(str(i)))

        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertQuerysetEqual(
            len(response.context['allies_list'].count()),
            50
        )
        '''


class AdminAccessTests(TestCase):

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
        self.assertEqual(response.status_code, 200)

    def test_analytics_access_for_admin(self):
        """
        Admin users can access Analytics
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-analytics'))
        self.assertEqual(response.status_code, 200)


class LoginRedirectTests(TestCase):

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()

        user1 = User.objects.create_user(username ='admin', email='email@test.com', password='admin_password1',
                                         is_staff=True)
        user1 = User.objects.create_user(username='nonadmin', email='email@test.com', password='admin_password2',
                                         is_staff=False)

    def test_login_for_admin(self):
        """
        Admin users can access Dashboard
        """
        self.client.login(username='admin', password='admin_password1')
        response = self.client.get(reverse('sap:login_success'))
        self.assertEqual(response.status_code, 302)
        self.client.logout()

    def test_login_for_nonadmin(self):
        """
        Admin users can access Analytics
        """
        self.client.login(username='nonadmin', password='admin_password2')
        response = self.client.get(reverse('sap:sap-admin_profile'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()


'''class NonAdminAccessTests(TestCase):

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
        self.assertEqual(response.status_code, 403)

    def test_analytics_access_for_nonadmin(self):
        """
        Admin users can access Dashboard
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-analytics'))
        self.assertEqual(response.status_code, 403)
'''

