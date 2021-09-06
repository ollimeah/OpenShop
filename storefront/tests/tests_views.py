from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from staff.models import FAQ

class LoginTest(TestCase):

    def test_login_url_exists_at_desired_location(self):
        response = self.client.get('/staff/')
        self.assertEqual(response.status_code, 200)

    def test_login_url_accessible_by_name(self):
        response = self.client.get(reverse('staff-login'))
        self.assertEqual(response.status_code, 200)

    def test_login_uses_correct_template(self):
        response = self.client.get(reverse('staff-login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/login.html')

    def test_logout_url_exists_at_desired_location(self):
        response = self.client.get('/staff/logout/')
        self.assertEqual(response.status_code, 200)

    def test_logout_url_accessible_by_name(self):
        response = self.client.get(reverse('staff-logout'))
        self.assertEqual(response.status_code, 200)
    
    def test_logout_uses_correct_template(self):
        response = self.client.get(reverse('staff-logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/login.html')

class DashboardTest(TestCase):

    def setUp(self):
        username = 'staff'
        password = 'test_password'
        staff = User.objects.create_user(username=username, password=password)
        staff.save()
        group = Group.objects.create(name='Staff')
        group.user_set.add(staff)
    
    def login_staff(self):
        return self.client.login(username='staff', password='test_password')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('staff-dashboard'))
        self.assertRedirects(response, '/staff/?next=/staff/dashboard/')
    
    def test_dashboard_url_exists_at_desired_location(self):
        self.login_staff()
        response = self.client.get('/staff/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_url_accessible_by_name(self):
        self.login_staff()
        response = self.client.get(reverse('staff-dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_uses_correct_template(self):
        self.login_staff()
        response = self.client.get(reverse('staff-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/dashboard.html')

class FAQTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        username = 'staff'
        password = 'test_password'
        staff = User.objects.create_user(username=username, password=password)
        staff.save()
        group = Group.objects.create(name='Staff')
        group.user_set.add(staff)
        FAQ.objects.create(question="Test", answer="Test")
    
    def login_staff(self):
        return self.client.login(username='staff', password='test_password')
    
    def test_index_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('staff-faqs'))
        self.assertRedirects(response, '/staff/?next=/staff/faqs/')
    
    def test_index_url_exists_at_desired_location(self):
        self.login_staff()
        response = self.client.get('/staff/faqs/')
        self.assertEqual(response.status_code, 200)

    def test_index_url_accessible_by_name(self):
        self.login_staff()
        response = self.client.get(reverse('staff-faqs'))
        self.assertEqual(response.status_code, 200)

    def test_index_uses_correct_template(self):
        self.login_staff()
        response = self.client.get(reverse('staff-faqs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'faqs/index.html')
    
    def test_new_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('staff-faqs-new'))
        self.assertRedirects(response, '/staff/?next=/staff/faqs/new/')
    
    def test_new_url_exists_at_desired_location(self):
        self.login_staff()
        response = self.client.get('/staff/faqs/new/')
        self.assertEqual(response.status_code, 200)

    def test_new_url_accessible_by_name(self):
        self.login_staff()
        response = self.client.get(reverse('staff-faqs-new'))
        self.assertEqual(response.status_code, 200)

    def test_new_uses_correct_template(self):
        self.login_staff()
        response = self.client.get(reverse('staff-faqs-new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'faqs/new.html')
    
    def test_update_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('staff-faq-update', kwargs={'pk':1}))
        self.assertRedirects(response, '/staff/?next=/staff/faq/1/update/')
    
    def test_update_url_exists_at_desired_location(self):
        self.login_staff()
        response = self.client.get('/staff/faq/1/update/')
        self.assertEqual(response.status_code, 200)

    def test_update_url_accessible_by_name(self):
        self.login_staff()
        response = self.client.get(reverse('staff-faq-update', kwargs={'pk':1}))
        self.assertEqual(response.status_code, 200)

    def test_update_uses_correct_template(self):
        self.login_staff()
        response = self.client.get(reverse('staff-faq-update', kwargs={'pk':1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'faqs/update.html')
    
    def test_delete_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('staff-faq-delete', kwargs={'pk':1}))
        self.assertRedirects(response, '/staff/?next=/staff/faq/1/delete/')
    
    def test_delete_url_exists_at_desired_location(self):
        self.login_staff()
        response = self.client.get('/staff/faq/1/delete/')
        self.assertEqual(response.status_code, 200)

    def test_delete_url_accessible_by_name(self):
        self.login_staff()
        response = self.client.get(reverse('staff-faq-delete', kwargs={'pk':1}))
        self.assertEqual(response.status_code, 200)

    def test_delete_uses_correct_template(self):
        self.login_staff()
        response = self.client.get(reverse('staff-faq-delete', kwargs={'pk':1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'faqs/index.html')