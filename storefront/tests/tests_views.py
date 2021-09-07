from django.http import response
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from staff.models import FAQ, Promotion

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
    
    def test_post_new_redirect_if_not_logged_in(self):
        response = self.client.post(reverse('staff-faqs-new'), {'question':'Test', 'answer':'Test'}, follow=True)
        self.assertRedirects(response, '/staff/?next=/staff/faqs/new/')
    
    def test_new_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/faqs/new/')

    def test_new_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-faqs-new'))

    def test_new_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-faqs-new'), 'faqs/view.html')
    
    def test_post_new(self):
        self.login_staff()
        response = self.client.post(reverse('staff-faqs-new'), {'question':'Test', 'answer':'Test'}, follow=True)
        self.assertRedirects(response, reverse('staff-faqs'))
    
    def test_update_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-faq-update', kwargs={'pk':1}), '/staff/?next=/staff/faq/1/update/')
    
    def test_post_update_redirect_if_not_logged_in(self):
        response = self.client.post(reverse('staff-faq-update', kwargs={'pk':1}), {'question':'Test', 'answer':'Test'}, follow=True)
        self.assertRedirects(response, '/staff/?next=/staff/faq/1/update/')
    
    def test_update_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/faq/1/update/')

    def test_update_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-faq-update', kwargs={'pk':1}))

    def test_update_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-faq-update', kwargs={'pk':1}), 'faqs/view.html')
    
    def test_post_update(self):
        self.login_staff()
        response = self.client.post(reverse('staff-faq-update', kwargs={'pk':1}), {'question':'Test', 'answer':'Test'}, follow=True)
        self.assertRedirects(response, reverse('staff-faqs'))
    
    def test_delete_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-faq-delete', kwargs={'pk':1}), '/staff/?next=/staff/faq/1/delete/')
    
    def test_delete_url_exists_at_desired_location(self):
        self.redirect_test_with_login('/staff/faq/1/delete/', '/staff/faqs/')

    def test_delete_url_accessible_by_name(self):
        self.redirect_test_with_login(reverse('staff-faq-delete', kwargs={'pk':1}), '/staff/faqs/')

class PromotionTest(URLTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Promotion.objects.create(code="Test", type=Promotion.FIXED_PRICE, amount=10)
        Promotion.objects.create(code="TestP", type=Promotion.PERCENTAGE, amount=10)

    def test_index_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-promotions'), '/staff/?next=/staff/promotions/')
    
    def test_index_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/promotions/')

    def test_index_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-promotions'))

    def test_index_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-promotions'), 'promotions/index.html')
    
    def test_detail_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-promotion', kwargs={'code':'Test'}), '/staff/?next=/staff/promotion/Test/')
    
    def test_detail_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/promotion/Test/')

    def test_detail_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-promotion', kwargs={'code':'Test'}))

    def test_detail_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-promotion', kwargs={'code':'Test'}), 'promotions/detail.html')
    
    def test_new_fixed_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-promotions-fixed-new'), '/staff/?next=/staff/promotions/fixed/new/')
    
    def test_post_new_fixed_redirect_if_not_logged_in(self):
        response = self.client.post(reverse('staff-promotions-fixed-new'), {'code':"Test2", 'amount':'10'}, follow=True)
        self.assertRedirects(response, '/staff/?next=/staff/promotions/fixed/new/')
    
    def test_new_fixed_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/promotions/fixed/new/')

    def test_new_fixed_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-promotions-fixed-new'))

    def test_new_fixed_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-promotions-fixed-new'), 'promotions/fixed.html')
    
    def test_post_new_fixed(self):
        self.login_staff()
        response = self.client.post(reverse('staff-promotions-fixed-new'), {'code':"Test2", 'amount':'10'}, follow=True)
        self.assertEqual(Promotion.FIXED_PRICE, Promotion.objects.get(code='Test2').type)
        self.assertRedirects(response, reverse('staff-promotion', kwargs={'code':'Test2'}))
    
    def test_new_percentage_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-promotions-percentage-new'), '/staff/?next=/staff/promotions/percentage/new/')
    
    def test_post_new_percentage_redirect_if_not_logged_in(self):
        response = self.client.post(reverse('staff-promotions-percentage-new'), {'code':"Test2", 'amount':'10'}, follow=True)
        self.assertRedirects(response, '/staff/?next=/staff/promotions/percentage/new/')
    
    def test_new_percentage_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/promotions/percentage/new/')

    def test_new_percentage_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-promotions-percentage-new'))

    def test_new_percentage_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-promotions-percentage-new'), 'promotions/percentage.html')
    
    def test_post_new_percentage(self):
        self.login_staff()
        response = self.client.post(reverse('staff-promotions-percentage-new'), {'code':"Test2", 'amount':'10'}, follow=True)
        self.assertEqual(Promotion.PERCENTAGE, Promotion.objects.get(code='Test2').type)
        self.assertRedirects(response, reverse('staff-promotion', kwargs={'code':'Test2'}))
    
    def test_update_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-promotion-update', kwargs={'code':'Test'}), '/staff/?next=/staff/promotion/Test/update/')
    
    def test_post_update_redirect_if_not_logged_in(self):
        response = self.client.post(reverse('staff-promotion-update', kwargs={'code':'Test'}), {'amount':'10'}, follow=True)
        self.assertRedirects(response, '/staff/?next=/staff/promotion/Test/update/')
    
    def test_update_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/promotion/Test/update/')

    def test_update_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-promotion-update', kwargs={'code':'Test'}))

    def test_update_fixed_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-promotion-update', kwargs={'code':'Test'}), 'promotions/fixed.html')
    
    def test_update_fixed_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-promotion-update', kwargs={'code':'TestP'}), 'promotions/percentage.html')
    
    def test_post_update(self):
        self.login_staff()
        response = self.client.post(reverse('staff-promotion-update', kwargs={'code':'Test'}), {'code':'Test', 'amount':'100'}, follow=True)
        self.assertRedirects(response, reverse('staff-promotion', kwargs={'code':'Test'}))
    
    def test_delete_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-promotion-delete', kwargs={'code':'Test'}), '/staff/?next=/staff/promotion/Test/delete/')
    
    def test_delete_url_exists_at_desired_location(self):
        self.redirect_test_with_login('/staff/promotion/Test/delete/', '/staff/promotions/')

    def test_delete_url_accessible_by_name(self):
        self.redirect_test_with_login(reverse('staff-promotion-delete', kwargs={'code':'Test'}), '/staff/promotions/')
    
    def test_disable_all_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-disable-promotions'), '/staff/?next=/staff/promotions/disable-all/')
    
    def test_disable_all_url_exists_at_desired_location(self):
        self.redirect_test_with_login('/staff/promotions/disable-all/', '/staff/promotions/')

    def test_disable_all_url_accessible_by_name(self):
        self.redirect_test_with_login(reverse('staff-disable-promotions'), '/staff/promotions/')
    
    def test_disable_all(self):
        self.login_staff()
        self.client.get(reverse('staff-disable-promotions'))
        for promotion in Promotion.objects.all():
            self.assertFalse(promotion.active)