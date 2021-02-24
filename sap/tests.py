from django.test import TestCase
from django.urls import reverse
from .models import Message


# Create your tests here.

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
