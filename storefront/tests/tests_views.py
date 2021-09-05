from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group

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