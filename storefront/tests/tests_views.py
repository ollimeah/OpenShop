from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from staff.models import FAQ

class URLTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        username = 'staff'
        password = 'test_password'
        staff = User.objects.create_user(username=username, password=password)
        staff.save()
        group = Group.objects.create(name='Staff')
        group.user_set.add(staff)
    
    def login_staff(self):
        return self.client.login(username='staff', password='test_password')
    
    def redirect_test(self, get_url, redirect_url):
        response = self.client.get(get_url)
        self.assertRedirects(response, redirect_url)
    
    def redirect_test_with_login(self, get_url, redirect_url):
        self.login_staff()
        response = self.client.get(get_url)
        self.assertRedirects(response, redirect_url)
    
    def url_ok_test_with_login(self, get_url):
        self.login_staff()
        response = self.client.get(get_url)
        self.assertEqual(response.status_code, 200)
    
    def template_test_with_login(self, get_url, template):
        self.login_staff()
        response = self.client.get(get_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template)

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

class DashboardTest(URLTestCase):

    def test_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-dashboard'), '/staff/?next=/staff/dashboard/')
    
    def test_dashboard_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/dashboard/')

    def test_dashboard_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-dashboard'))

    def test_dashboard_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-dashboard'), 'staff/dashboard.html')

class FAQTest(URLTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        FAQ.objects.create(question="Test", answer="Test")
    
    def test_index_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-faqs'), '/staff/?next=/staff/faqs/')
    
    def test_index_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/faqs/')

    def test_index_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-faqs'))

    def test_index_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-faqs'), 'faqs/index.html')
    
    def test_new_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-faqs-new'), '/staff/?next=/staff/faqs/new/')
    
    def test_new_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/faqs/new/')

    def test_new_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-faqs-new'))

    def test_new_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-faqs-new'), 'faqs/view.html')
    
    def test_update_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-faq-update', kwargs={'pk':1}), '/staff/?next=/staff/faq/1/update/')
    
    def test_update_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/faq/1/update/')

    def test_update_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-faq-update', kwargs={'pk':1}))

    def test_update_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-faq-update', kwargs={'pk':1}), 'faqs/view.html')
    
    def test_delete_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-faq-delete', kwargs={'pk':1}), '/staff/?next=/staff/faq/1/delete/')
    
    def test_delete_url_exists_at_desired_location(self):
        self.redirect_test_with_login('/staff/faq/1/delete/', '/staff/faqs/')

    def test_delete_url_accessible_by_name(self):
        self.redirect_test_with_login(reverse('staff-faq-delete', kwargs={'pk':1}), '/staff/faqs/')