from django.test import TestCase, Client
from .models import Ally, Message
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

class MessageModelTest(TestCase):
    def setUp(self):
        Message.objects.create(text='test case for Chat Feature')

    def test_chat_content(self):
        entry = Message.objects.get(id=1)
        expected_object_name = f'{entry.text}'
        self.assertEqual(expected_object_name, 'test case for Chat Feature')


class MessageBoardViewTest(TestCase):  # new
    def setUp(self):
        Message.objects.create(text='test case for Message Board view')

    def test_view_url_exists_at_proper_location(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_by_name(self):
        resp = self.client.get(reverse('message_board'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('message_board'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'sap/message_board.html')
