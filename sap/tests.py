from django.test import TestCase, Client
from .models import Ally, StudentCategories, AllyStudentCategoryRelation
from django.urls import reverse
from django.contrib.auth.models import User
from http import HTTPStatus
from .forms import UpdateAdminProfileForm
from django.contrib.auth.forms import PasswordChangeForm

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



class AdminUpdateProfileAndPasswordTests(TestCase):
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
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        
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
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

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

class AlliesIndexViewTests(TestCase):

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
            ['<Ally: hawk_id_2>', '<Ally: hawk_id_1>'] # Need to return in the descending order (When the ally record was created in the table)
        )

class CreateAdminViewTest(TestCase):

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.c = Client()
        self.user = User.objects.create_user(self.username, 'email@test.com', self.password)
        self.c.login(username=self.username, password=self.password)
        self.user.is_staff = True
        self.user.save()

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
        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.client.logout()

    def test_login_for_nonadmin(self):
        """
        Non-admin users are redirected to About page
        """
        self.client.login(username='nonadmin', password='admin_password2')
        response = self.client.get(reverse('sap:sap-about'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.client.logout()


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
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_analytics_access_for_admin(self):
        """
        Admin users can access Analytics
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-analytics'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

class SignUpTests(TestCase):
    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.user = User.objects.create_user(self.username, 'email@test.com', self.password)
        self.c = Client()

    def test_get(self):
        response = self.c.get('/sign-up/')
        self.assertEqual(response.status_code, 200)

    def test_entered_existing_user(self):
        response = self.c.post('/sign-up/', {'csrfmiddlewaretoken': ['MIyNUVJILbLGKrHXjz4m4fWt4d13TUOkkvRtCpStSmxkW8PKomuz3ESTYF8VVQil'],
                                  'firstName': ['Elias'], 'lastName': ['Shaeffer'], 'new_username': ['admin'],
                                  'new_email': ['eshaeffer@uiowa.edu'], 'new_password': ['ddd'], 'repeat_password':
                                      ['dddd'], 'roleSelected': ['Graduate Student'],
                                  'stemGradCheckboxes': ['Biochemistry'], 'mentoringGradRadios': ['Yes'],
                                  'mentoringGradCheckboxes': ['First generation college-student'],
                                  'labShadowRadios': ['Yes'], 'connectingRadios': ['Yes'],
                                  'volunteerGradRadios': ['Yes'], 'gradTrainingRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/sign-up')
        self.assertEqual(response.status_code, 302)

    def test_entered_existing_email(self):
        response = self.c.post('/sign-up/', {'csrfmiddlewaretoken': ['MIyNUVJILbLGKrHXjz4m4fWt4d13TUOkkvRtCpStSmxkW8PKomuz3ESTYF8VVQil'],
                                  'firstName': ['Elias'], 'lastName': ['Shaeffer'], 'new_username': ['admin1'],
                                  'new_email': ['email@test.com'], 'new_password': ['ddd'], 'repeat_password':
                                      ['dddd'], 'roleSelected': ['Graduate Student'],
                                  'stemGradCheckboxes': ['Biochemistry'], 'mentoringGradRadios': ['Yes'],
                                  'mentoringGradCheckboxes': ['First generation college-student'],
                                  'labShadowRadios': ['Yes'], 'connectingRadios': ['Yes'],
                                  'volunteerGradRadios': ['Yes'], 'gradTrainingRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/sign-up')
        self.assertEqual(response.status_code, 302)

    def test_password_not_same(self):
        response = self.c.post('/sign-up/', {'csrfmiddlewaretoken': ['MIyNUVJILbLGKrHXjz4m4fWt4d13TUOkkvRtCpStSmxkW8PKomuz3ESTYF8VVQil'],
                                  'firstName': ['Elias'], 'lastName': ['Shaeffer'], 'new_username': ['admin1123'],
                                  'new_email': ['email123@test.com'], 'new_password': ['ddd'], 'repeat_password':
                                      ['ddddd'], 'roleSelected': ['Graduate Student'],
                                  'stemGradCheckboxes': ['Biochemistry'], 'mentoringGradRadios': ['Yes'],
                                  'mentoringGradCheckboxes': ['First generation college-student'],
                                  'labShadowRadios': ['Yes'], 'connectingRadios': ['Yes'],
                                  'volunteerGradRadios': ['Yes'], 'gradTrainingRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/sign-up')
        self.assertEqual(response.status_code, 302)

    def test_create_Undergrad(self):
        response = self.c.post('/sign-up/', { 'csrfmiddlewaretoken': ['At4HFZNsApVRWNye2Jcj4RVcWYf1fviv1kFbSZevLnNmJrWz4OyZhcAPn0JeaknZ'],
                                              'firstName': ['Zeeshan'], 'lastName': ['Ahmed'], 'new_username': ['zeeahmed'],
                                              'new_email': ['zeeahmed@uiowa.edu'], 'new_password': ['bigchungus'],
                                              'repeat_password': ['bigchungus'], 'roleSelected': ['Undergraduate Student'],
                                              'undergradRadios': ['Senior'], 'idUnderGradCheckboxes': ['First generation college-student'],
                                              'major': ['Computer Science'], 'interestRadios': ['Yes'],
                                              'experienceRadios': ['Yes'], 'interestedRadios': ['Yes'],
                                              'agreementRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="zeeahmed")
        ally = Ally.objects.filter(user_id=user[0].id)
        categoryRelation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=categoryRelation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(categoryRelation.exists())
        self.assertTrue(categories.exists())

    def test_create_Undergrad(self):
        response = self.c.post('/sign-up/', { 'csrfmiddlewaretoken': ['At4HFZNsApVRWNye2Jcj4RVcWYf1fviv1kFbSZevLnNmJrWz4OyZhcAPn0JeaknZ'],
                                              'firstName': ['Zeeshan'], 'lastName': ['Ahmed'], 'new_username': ['zeeahmed1'],
                                              'new_email': ['zeeahmed@uiowa.edu'], 'new_password': ['bigchungus'],
                                              'repeat_password': ['bigchungus'], 'roleSelected': ['Undergraduate Student'],
                                              'undergradRadios': ['Senior'], 'major': ['Computer Science'], 'interestRadios': ['Yes'],
                                              'experienceRadios': ['Yes'], 'interestedRadios': ['Yes'],
                                              'agreementRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="zeeahmed1")
        ally = Ally.objects.filter(user_id=user[0].id)
        categoryRelation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=categoryRelation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(categoryRelation.exists())
        self.assertTrue(categories.exists())

    def test_create_Grad(self):
        response = self.c.post('/sign-up/', {'csrfmiddlewaretoken': ['TFosu1rFWp6S4SsYIV5Rb9FtBzoTavgrCsu31o9hTp975IuRpZeNgPJeBQiU6Cy5'], 
        'firstName': ['glumpy'], 'lastName': ['guy'], 'new_username': ['big_guy1'], 
        'new_email': ['eshaeffer@uiowa.edu'], 'new_password': ['123'], 'repeat_password': ['123'], 
        'roleSelected': ['Graduate Student'], 
        'stemGradCheckboxes': ['Biochemistry', 'Biology', 'Biomedical Engineering', 'Chemical Engineering'], 
        'mentoringGradRadios': ['Yes'], 'mentoringGradCheckboxes': ['First generation college-student', 'Low-income', 'Underrepresented racial/ethnic minority', 'Transfer student', 'LGBTQ'], 
        'labShadowRadios': ['Yes'], 'connectingRadios': ['Yes'], 'volunteerGradRadios': ['No'], 'gradTrainingRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="big_guy1")
        ally = Ally.objects.filter(user_id=user[0].id)
        categoryRelation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=categoryRelation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(categoryRelation.exists())
        self.assertTrue(categories.exists())

    def test_create_Grad_noBoxes(self):
        response = self.c.post('/sign-up/', {
            'csrfmiddlewaretoken': ['TFosu1rFWp6S4SsYIV5Rb9FtBzoTavgrCsu31o9hTp975IuRpZeNgPJeBQiU6Cy5'],
            'firstName': ['glumpy'], 'lastName': ['guy'], 'new_username': ['big_guy12'],
            'new_email': ['eshaeffer@uiowa.edu'], 'new_password': ['123'], 'repeat_password': ['123'],
            'roleSelected': ['Graduate Student'],
            'mentoringGradRadios': ['Yes'],
            'labShadowRadios': ['Yes'], 'connectingRadios': ['Yes'], 'volunteerGradRadios': ['No'],
            'gradTrainingRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="big_guy12")
        ally = Ally.objects.filter(user_id=user[0].id)
        categoryRelation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=categoryRelation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(categoryRelation.exists())
        self.assertTrue(categories.exists())


    def test_Faculty(self):
        response = self.c.post('/sign-up/', {'csrfmiddlewaretoken': ['gr9bKWMJLFrJZfcdKkdRhlyKLI0JeTh2ZefMhjulIFuY05e6romNm1CvLZUKa0zG'], 'firstName': ['Terry'], 'lastName': ['Braun'], 
        'new_username': ['tbraun'], 'new_email': ['tbraun@uiowa.edu'], 'new_password': ['123'], 
        'repeat_password': ['123'], 'roleSelected': ['Faculty'], 
        'stemCheckboxes': ['Bioinformatics', 'Biomedical Engineering'], 'research-des': ['Me make big variant :)'], 
        'openingRadios': ['Yes'], 'mentoringCheckboxes': ['First generation college-student', 'Underrepresented racial/ethnic minority', 'Transfer student'], 
        'volunteerRadios': ['Yes'],'mentoringFacultyRadios':['Yes'], 'trainingRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="tbraun")
        ally = Ally.objects.filter(user_id=user[0].id)
        categoryRelation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=categoryRelation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(categoryRelation.exists())
        self.assertTrue(categories.exists())

    def test_Faculty_noSelect(self):
        response = self.c.post('/sign-up/', {
            'csrfmiddlewaretoken': ['gr9bKWMJLFrJZfcdKkdRhlyKLI0JeTh2ZefMhjulIFuY05e6romNm1CvLZUKa0zG'],
            'firstName': ['Terry'], 'lastName': ['Braun'],
            'new_username': ['tbraun2'], 'new_email': ['tbraun@uiowa.edu'], 'new_password': ['123'],
            'repeat_password': ['123'], 'roleSelected': ['Faculty'],
            'research-des': ['Me make big variant :)'],
            'openingRadios': ['Yes'],
            'volunteerRadios': ['Yes'], 'mentoringFacultyRadios': ['Yes'], 'trainingRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="tbraun2")
        ally = Ally.objects.filter(user_id=user[0].id)
        categoryRelation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=categoryRelation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(categoryRelation.exists())
        self.assertTrue(categories.exists())

    def test_Staff(self):
        response = self.c.post('/sign-up/', {'csrfmiddlewaretoken': ['K5dFCUih0K6ZYklAemhvIWSpCebK86zdx4ric6ucIPLUQhAdtdT7hhp4r5etxoJY'], 
        'firstName': ['hawk'], 'lastName': ['herky'], 'new_username': ['hawkherky'], 'new_email': ['hawkherky@uiowa.edu'], 
        'new_password': ['hawk'], 'repeat_password': ['hawk'], 'roleSelected': ['Staff'], 
        'studentsInterestedRadios': ['Yes'], 'howCanWeHelp': ['sasdasdasd']})
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="hawkherky")
        ally = Ally.objects.filter(user_id=user[0].id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())

    
    # def test_Staff(self):
    #     response = self.c.post('/sign-up/', {'csrfmiddlewaretoken': ['PoY77CUhmZ70AsUF3C1nISUsVErkhMjLyb4IEZCTjZafBiWyKGajNyYdVVlldTBp'], 
    #     'firstName': ['chongu'], 'lastName': ['gumpy'], 'new_username': ['chonguG'], 
    #     'new_email': ['chongu@uiowa.edu'], 'new_password': ['123'], 'repeat_password': ['123'], 
    #     'roleSelected': ['Staff'], 'studentsInterestedRadios': ['Yes'], 'howCanWeHelp': ['give me $10000000']})
    #     url = response.url
    #     self.assertEqual(url, '/')
    #     self.assertEqual(response.status_code, 302)
    #     user = User.objects.filter(username="chonguG")
    #     ally = Ally.objects.filter(user_id=user[0].id)
    #     categoryRelation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
    #     categories = StudentCategories.objects.filter(id=categoryRelation[0].student_category_id)
    #     self.assertTrue(user.exists())
    #     self.assertTrue(ally.exists())
    #     self.assertTrue(categoryRelation.exists())
    #     self.assertTrue(categories.exists())


class NonAdminAccessTests(TestCase):

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


