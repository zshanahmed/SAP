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

class CreateAdminViewTest(TestCase):

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.c = Client()
        self.user = User.objects.create_user(self.username, 'email@test.com', self.password)
        self.c.login(username=self.username, password=self.password)

    def test_get(self):
        """
        test get create admin page
        """
        response = self.c.get('/create_iba_admin/')
        self.assertEqual(response.status_code, 200)

    def test_post_missing_data(self):
        response = self.c.post('/create_iba_admin/', {'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
                'current_username': ['iba_admin'],
                'current_password': ['iba_sep_1'], 'new_email': [''],
                'new_username': ['iba_admin'], 'new_password': ['iba_sep_1'],
                'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_post_Invalid_credentials(self):
        response = self.c.post('/create_iba_admin/', {'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
                'current_username': ['admin'],
                'current_password': ['admin_assword1'], 'new_email': ['emailGuy@email.com'],
                'new_username': ['iba_admin'], 'new_password': ['iba_sep_1'],
                'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_post_new_username_that_exists(self):
        response = self.c.post('/create_iba_admin/', {'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
                'current_username': ['admin'],
                'current_password': ['admin_password1'], 'new_email': ['emailGuy@email.com'],
                'new_username': ['admin'], 'new_password': ['admin_password1'],
                'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_post_non_matching_new_password(self):
        response = self.c.post('/create_iba_admin/', {'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
                'current_username': ['admin'],
                'current_password': ['admin_password1'], 'new_email': ['emailGuy@email.com'],
                'new_username': ['admin1'], 'new_password': ['admin_password1'],
                'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_good_create_admin(self):
        response = self.c.post('/create_iba_admin/', {'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
                'current_username': ['admin'],
                'current_password': ['admin_password1'], 'new_email': ['emailGuy@email.com'],
                'new_username': ['admin1'], 'new_password': ['admin_password1'],
                'repeat_password': ['admin_password1']})

        url = response.url
        assert url == '/dashboard'
        assert User.objects.filter(username='admin1').exists()

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
