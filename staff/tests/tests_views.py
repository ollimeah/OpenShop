from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from staff.models import FAQ, Basket, Category, Collection, Delivery, Device, Message, Order, Product, Promotion, Settings

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
    
    def test_update_percentage_uses_correct_template(self):
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

class DeliveryTest(URLTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Delivery.objects.create(name="Test", price="10")
    
    def test_index_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-deliveries'), '/staff/?next=/staff/deliveries/')
    
    def test_index_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/deliveries/')

    def test_index_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-deliveries'))

    def test_index_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-deliveries'), 'delivery/index.html')
    
    def test_new_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-deliveries-new'), '/staff/?next=/staff/deliveries/new/')
    
    def test_post_new_redirect_if_not_logged_in(self):
        response = self.client.post(reverse('staff-deliveries-new'), {'name':'Test', 'price':'10'}, follow=True)
        self.assertRedirects(response, '/staff/?next=/staff/deliveries/new/')
    
    def test_new_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/deliveries/new/')

    def test_new_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-deliveries-new'))

    def test_new_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-deliveries-new'), 'delivery/view.html')
    
    def test_post_new(self):
        self.login_staff()
        response = self.client.post(reverse('staff-deliveries-new'), {'name':'Test2', 'price':'10'}, follow=True)
        self.assertRedirects(response, reverse('staff-deliveries'))
    
    def test_update_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-delivery-update', kwargs={'pk':1}), '/staff/?next=/staff/delivery/1/update/')
    
    def test_post_update_redirect_if_not_logged_in(self):
        response = self.client.post(reverse('staff-delivery-update', kwargs={'pk':1}), {'name':'Test2', 'price':'10'}, follow=True)
        self.assertRedirects(response, '/staff/?next=/staff/delivery/1/update/')
    
    def test_update_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/delivery/1/update/')

    def test_update_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-delivery-update', kwargs={'pk':1}))

    def test_update_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-delivery-update', kwargs={'pk':1}), 'delivery/view.html')
    
    def test_post_update(self):
        self.login_staff()
        response = self.client.post(reverse('staff-delivery-update', kwargs={'pk':1}), {'name':'Test2', 'price':'10'}, follow=True)
        self.assertRedirects(response, reverse('staff-deliveries'))
    
    def test_delete_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-delivery-delete', kwargs={'pk':1}), '/staff/?next=/staff/delivery/1/delete/')
    
    def test_delete_url_exists_at_desired_location(self):
        self.redirect_test_with_login('/staff/delivery/1/delete/', '/staff/deliveries/')

    def test_delete_url_accessible_by_name(self):
        self.redirect_test_with_login(reverse('staff-delivery-delete', kwargs={'pk':1}), '/staff/deliveries/')

class OrderTest(URLTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Order.objects.create()
    
    def test_index_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-orders'), '/staff/?next=/staff/orders/')
    
    def test_index_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/orders/')

    def test_index_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-orders'))

    def test_index_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-orders'), 'staff/orders/index.html')
    
    def test_detail_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-order', kwargs={'pk':'1'}), '/staff/?next=/staff/order/1/')
    
    def test_detail_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/order/1/')

    def test_detail_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-order', kwargs={'pk':'1'}))

    def test_detail_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-order', kwargs={'pk':'1'}), 'staff/orders/detail.html')
    
    def test_toggle_shipped_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-order-toggle', kwargs={'pk':'1'}), '/staff/?next=/staff/order/1/toggle-shipped/')
    
    def test_toggle_shipped_url_exists_at_desired_location(self):
        self.redirect_test_with_login('/staff/order/1/toggle-shipped/', '/staff/order/1/')

    def test_toggle_shipped_url_accessible_by_name(self):
        self.redirect_test_with_login(reverse('staff-order-toggle', kwargs={'pk':'1'}), '/staff/order/1/')
    
    def test_toggle_shipped(self):
        self.login_staff()
        self.client.get(reverse('staff-order-toggle', kwargs={'pk':'1'}))
        self.assertTrue(Order.objects.get(id=1).shipped)

class CategoryTest(URLTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Category.objects.create(name="Test")
    
    def tearDown(self):
        for prod in Product.objects.all(): prod.image.delete()
        return super().tearDown()
    
    def create_product(self, name='Test', available=True, hidden=False, file_name='test'):
        category = Category.objects.get(id=1)
        prod = Product.objects.create(name=name, description='Test', price=10, category=category,
        image=SimpleUploadedFile(file_name + '.jpg', b'content'), available=available, hidden=hidden, min=1, max=12)
        return prod

    def test_index_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-categories'), '/staff/?next=/staff/categories/')
    
    def test_index_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/categories/')

    def test_index_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-categories'))

    def test_index_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-categories'), 'categories/index.html')
    
    def test_detail_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-category', kwargs={'name':'Test'}), '/staff/?next=/staff/category/Test/')
    
    def test_detail_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/category/Test/')

    def test_detail_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-category', kwargs={'name':'Test'}))

    def test_detail_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-category', kwargs={'name':'Test'}), 'categories/detail.html')
    
    def test_new_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-categories-new'), '/staff/?next=/staff/categories/new/')
    
    def test_post_new_redirect_if_not_logged_in(self):
        response = self.client.post(reverse('staff-categories-new'), {'name':"Test2"}, follow=True)
        self.assertRedirects(response, '/staff/?next=/staff/categories/new/')
    
    def test_new_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/categories/new/')

    def test_new_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-categories-new'))

    def test_new_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-categories-new'), 'categories/view.html')
    
    def test_post_new(self):
        self.login_staff()
        response = self.client.post(reverse('staff-categories-new'), {'name':"Test2"}, follow=True)
        self.assertRedirects(response, reverse('staff-category', kwargs={'name':'Test2'}))
    
    def test_update_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-category-update', kwargs={'name':'Test'}), '/staff/?next=/staff/category/Test/update/')
    
    def test_post_update_redirect_if_not_logged_in(self):
        response = self.client.post(reverse('staff-category-update', kwargs={'name':'Test'}), {'name':'Test'}, follow=True)
        self.assertRedirects(response, '/staff/?next=/staff/category/Test/update/')
    
    def test_update_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/category/Test/update/')

    def test_update_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-category-update', kwargs={'name':'Test'}))

    def test_update_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-category-update', kwargs={'name':'Test'}), 'categories/view.html')
    
    def test_post_update(self):
        self.login_staff()
        response = self.client.post(reverse('staff-category-update', kwargs={'name':'Test'}), {'name':'Test'}, follow=True)
        self.assertRedirects(response, reverse('staff-category', kwargs={'name':'Test'}))
    
    def test_delete_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-category-delete', kwargs={'name':'Test'}), '/staff/?next=/staff/category/Test/delete/')
    
    def test_delete_url_exists_at_desired_location(self):
        self.redirect_test_with_login('/staff/category/Test/delete/', '/staff/categories/')

    def test_delete_url_accessible_by_name(self):
        self.redirect_test_with_login(reverse('staff-category-delete', kwargs={'name':'Test'}), '/staff/categories/')
    
    def test_add_products_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-category-products', kwargs={'name':'Test'}), '/staff/?next=/staff/category/Test/products/')
    
    def test_add_products_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/category/Test/products/')

    def test_add_products_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-category-products', kwargs={'name':'Test'}))
    
    def test_add_products_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-category-products', kwargs={'name':'Test'}), 'categories/products.html')
    
    def test_add_products(self):
        self.login_staff()
        category = Category.objects.create(name="Test2")
        for i in range(1, 4):
            self.create_product(name="Test"+str(i), file_name="Test"+str(i))
        self.client.post(reverse('staff-category-products', kwargs={'name':'Test2'}), {"products":[1,2]})
        self.client.post(reverse('staff-category-products', kwargs={'name':'Test2'}), {"products":[1]})
        self.assertEqual(Product.objects.filter(category=category).count(), 2)
        self.assertEqual(Product.objects.filter(category=Category.objects.get(name="Test")).count(), 1)
        self.assertFalse(Product.objects.get(id=2).available)
        self.assertTrue(Product.objects.get(id=2).hidden)

class CollectionTest(URLTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Category.objects.create(name="Test")
        Collection.objects.create(name="Test", price=10, image=SimpleUploadedFile('test.jpg', b'content'))
    
    def tearDown(self):
        for prod in Product.objects.all(): prod.image.delete()
        for collection in Collection.objects.all(): collection.image.delete()
        return super().tearDown()
    
    def create_product(self, name='Test', available=True, hidden=False, file_name='test'):
        category = Category.objects.get(id=1)
        prod = Product.objects.create(name=name, description='Test', price=10, category=category,
        image=SimpleUploadedFile(file_name + '.jpg', b'content'), available=available, hidden=hidden, min=1, max=12)
        return prod

    def test_index_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-collections'), '/staff/?next=/staff/collections/')
    
    def test_index_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/collections/')

    def test_index_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-collections'))

    def test_index_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-collections'), 'collections/index.html')
    
    def test_detail_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-collection', kwargs={'name':'Test'}), '/staff/?next=/staff/collection/Test/')
    
    def test_detail_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/collection/Test/')

    def test_detail_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-collection', kwargs={'name':'Test'}))

    def test_detail_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-collection', kwargs={'name':'Test'}), 'collections/detail.html')
    
    def test_new_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-collections-new'), '/staff/?next=/staff/collections/new/')
    
    def test_post_new_redirect_if_not_logged_in(self):
        self.create_product(name="TestL")
        response = self.client.post(reverse('staff-collections-new'), {'name':"Test2", 'price':'10', 'product':['1']}, follow=True)
        self.assertRedirects(response, '/staff/?next=/staff/collections/new/')
    
    def test_new_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/collections/new/')

    def test_new_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-collections-new'))

    def test_new_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-collections-new'), 'collections/view.html')
    
    # def test_post_new(self):
    #     self.login_staff()
    #     self.create_product(name="TestP")
    #     response = self.client.post(reverse('staff-collections-new'), {'name':'Test2', 'price':'10', 'products':['1'], 'image':SimpleUploadedFile('img.jpg', b'content')}, follow=True)
    #     self.assertRedirects(response, reverse('staff-collection', kwargs={'name':'Test2'}))
    
    def test_update_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-collection-update', kwargs={'name':'Test'}), '/staff/?next=/staff/collection/Test/update/')
    
    def test_post_update_redirect_if_not_logged_in(self):
        response = self.client.post(reverse('staff-collection-update', kwargs={'name':'Test'}), {'name':'Test', 'price':'10', 'products':['1']}, follow=True)
        self.assertRedirects(response, '/staff/?next=/staff/collection/Test/update/')
    
    def test_update_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/collection/Test/update/')

    def test_update_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-collection-update', kwargs={'name':'Test'}))

    def test_update_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-collection-update', kwargs={'name':'Test'}), 'collections/view.html')
    
    def test_post_update(self):
        self.login_staff()
        self.create_product(name="TestU")
        response = self.client.post(reverse('staff-collection-update', kwargs={'name':'Test'}), {'name':'Test', 'price':'10', 'products':['1']}, follow=True)
        self.assertRedirects(response, reverse('staff-collection', kwargs={'name':'Test'}))
    
    def test_delete_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-collection-delete', kwargs={'name':'Test'}), '/staff/?next=/staff/collection/Test/delete/')
    
    def test_delete_url_exists_at_desired_location(self):
        self.redirect_test_with_login('/staff/collection/Test/delete/', '/staff/collections/')

    def test_delete_url_accessible_by_name(self):
        self.redirect_test_with_login(reverse('staff-collection-delete', kwargs={'name':'Test'}), '/staff/collections/')
    
    def test_add_products_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-collection-products', kwargs={'name':'Test'}), '/staff/?next=/staff/collection/Test/products/')
    
    def test_add_products_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/collection/Test/products/')

    def test_add_products_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-collection-products', kwargs={'name':'Test'}))
    
    def test_add_products_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-collection-products', kwargs={'name':'Test'}), 'collections/products.html')
    
    def test_add_products(self):
        self.login_staff()
        collection = Collection.objects.create(name="Test2", price=10)
        for i in range(1, 4):
            self.create_product(name="Test"+str(i), file_name="Test"+str(i))
        self.client.post(reverse('staff-collection-products', kwargs={'name':'Test2'}), {"products":[1,2]})
        self.client.post(reverse('staff-collection-products', kwargs={'name':'Test2'}), {"products":[1]})
        self.assertIn(Product.objects.get(id=1), collection.products.all())
        self.assertNotIn(Product.objects.get(id=2), collection.products.all())
    
class ProductTest(URLTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        category = Category.objects.create(name="Test")
        Product.objects.create(name="Test", description='Test', price=10, category=category,
        image=SimpleUploadedFile("test" + '.jpg', b'content'), available=True, hidden=False, min=1, max=12)
    
    def tearDown(self):
        for prod in Product.objects.all(): prod.image.delete()
        return super().tearDown()
    
    def create_product(self, name='Prod', available=True, hidden=False, file_name='prod'):
        category = Category.objects.get(id=1)
        prod = Product.objects.create(name=name, description='Test', price=10, category=category,
        image=SimpleUploadedFile(file_name + '.jpg', b'content'), available=available, hidden=hidden, min=1, max=12)
        return prod

    def test_index_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-products'), '/staff/?next=/staff/products/')
    
    def test_index_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/products/')

    def test_index_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-products'))

    def test_index_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-products'), 'products/index.html')
    
    def test_detail_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-product', kwargs={'name':'Test'}), '/staff/?next=/staff/product/Test/')
    
    def test_detail_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/product/Test/')

    def test_detail_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-product', kwargs={'name':'Test'}))

    def test_detail_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-product', kwargs={'name':'Test'}), 'products/detail.html')
    
    # def test_post_extra_image(self):
    #     self.login_staff()
    #     image = SimpleUploadedFile('test_add.jpg', b'content', content_type="image/jpeg")
    #     data = {'product':1, 'image':image}
    #     response = self.client.post(reverse('staff-product', kwargs={'name':'Test'}), data, follow=True)
    #     self.assertRedirects(response, reverse('staff-product', kwargs={'name':'Test'}))

    # def test_delete_extra_image(self):
    #     pass
    
    def test_new_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-products-new'), '/staff/?next=/staff/products/new/')
    
    def test_post_new_redirect_if_not_logged_in(self):
        data = {'name':"Test2", 'price':'10', 'description':'Test2', 'category':'1', 'image':'',
                'available':'True', 'hidden':'False', 'min':1, 'max':4}
        response = self.client.post(reverse('staff-products-new'), data, follow=True)
        self.assertRedirects(response, '/staff/?next=/staff/products/new/')
    
    def test_new_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/products/new/')

    def test_new_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-products-new'))

    def test_new_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-products-new'), 'products/view.html')
    
    # def test_post_new(self):
    #     self.login_staff()
    #     p = self.create_product(name='Prod3')
    #     with open(Product.objects.get(name='Prod3').image.url) as img:
    #         data = {'name':"Test", 'price':'13', 'description':'Test2', 'category':'1', 'image':img,
    #                 'available':'True', 'hidden':'False', 'min':1, 'max':4}
    #         print(data)
    #         response = self.client.post(reverse('staff-products-new'), data, follow=True)
    #         self.assertRedirects(response, reverse('staff-product', kwargs={'name':'Test2'}))
    
    def test_update_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-product-update', kwargs={'name':'Test'}), '/staff/?next=/staff/product/Test/update/')
    
    def test_post_update_redirect_if_not_logged_in(self):
        data = {'name':"Test", 'price':'13', 'description':'Test2', 'category':'1', 'image':'',
                'available':'True', 'hidden':'False', 'min':1, 'max':4}
        response = self.client.post(reverse('staff-product-update', kwargs={'name':'Test'}), data, follow=True)
        self.assertRedirects(response, '/staff/?next=/staff/product/Test/update/')
    
    def test_update_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/product/Test/update/')

    def test_update_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-product-update', kwargs={'name':'Test'}))

    def test_update_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-product-update', kwargs={'name':'Test'}), 'products/view.html')
    
    def test_post_update(self):
        self.login_staff()
        data = {'name':"Test", 'price':'13', 'description':'Test2', 'category':'1', 'image':'',
                'available':'True', 'hidden':'False', 'min':1, 'max':4}
        response = self.client.post(reverse('staff-product-update', kwargs={'name':'Test'}), data, follow=True)
        self.assertRedirects(response, reverse('staff-product', kwargs={'name':'Test'}))
    
    def test_delete_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-product-delete', kwargs={'name':'Test'}), '/staff/?next=/staff/product/Test/delete/')
    
    def test_delete_url_exists_at_desired_location(self):
        self.redirect_test_with_login('/staff/product/Test/delete/', '/staff/products/')

    def test_delete_url_accessible_by_name(self):
        self.redirect_test_with_login(reverse('staff-product-delete', kwargs={'name':'Test'}), '/staff/products/')
    
    def test_manage_products_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-products-manage'), '/staff/?next=/staff/products/manage/')
    
    def test_manage_products_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/products/manage/')

    def test_manage_products_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-products-manage'))
    
    def test_manage_products_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-products-manage'), 'products/manage.html')
    
    def test_manage_products_hide(self):
        for i in range(1, 4):
            self.create_product(name="Test"+str(i), file_name="Test"+str(i))
        self.login_staff()
        response = self.client.post(reverse('staff-products-manage'), {'action':'hide', 'products':['1','2','3']})
        for i in range(1,4):
            self.assertTrue(Product.objects.get(id=i).hidden)
        self.assertRedirects(response, reverse('staff-products'))

    def test_manage_products_delete(self):
        for i in range(1, 4):
            self.create_product(name="Test"+str(i), file_name="Test"+str(i))
        self.login_staff()
        response = self.client.post(reverse('staff-products-manage'), {'action':'delete', 'products':['1','2','3']})
        for i in range(1,4):
            self.assertEqual(0, Product.objects.filter(id=i).count())
        self.assertRedirects(response, reverse('staff-products'))

    def test_manage_products_available(self):
        for i in range(1, 4):
            self.create_product(name="Test"+str(i), file_name="Test"+str(i))
        self.login_staff()
        response = self.client.post(reverse('staff-products-manage'), {'action':'available', 'products':['1','2','3']})
        for i in range(1,4):
            self.assertTrue(Product.objects.get(id=i).available)
        self.assertRedirects(response, reverse('staff-products'))

    def test_manage_products_unavailable(self):
        for i in range(1, 4):
            self.create_product(name="Test"+str(i), file_name="Test"+str(i))
        self.login_staff()
        response = self.client.post(reverse('staff-products-manage'), {'action':'unavailable', 'products':['1','2','3']})
        for i in range(1,4):
            self.assertFalse(Product.objects.get(id=i).available)
        self.assertRedirects(response, reverse('staff-products'))
    
class BasketTest(URLTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        device = Device.objects.create()
        Basket.objects.create(device=device)
    
    def test_index_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-baskets'), '/staff/?next=/staff/baskets/')
    
    def test_index_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/baskets/')

    def test_index_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-baskets'))

    def test_index_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-baskets'), 'staff/baskets/index.html')
    
    def test_detail_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-basket', kwargs={'pk':'1'}), '/staff/?next=/staff/basket/1/')
    
    def test_detail_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/basket/1/')

    def test_detail_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-basket', kwargs={'pk':'1'}))

    def test_detail_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-basket', kwargs={'pk':'1'}), 'staff/baskets/detail.html')

class MessageTest(URLTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Message.objects.create(name="Test", email="test@test.com", subject="test", message="test")
    
    def test_index_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-messages'), '/staff/?next=/staff/messages/')
    
    def test_index_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/messages/')

    def test_index_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-messages'))

    def test_index_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-messages'), 'staff/messages/index.html')
    
    def test_delete_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-message-delete', kwargs={'pk':1}), '/staff/?next=/staff/message/1/delete/')
    
    def test_delete_url_exists_at_desired_location(self):
        self.redirect_test_with_login('/staff/message/1/delete/', '/staff/messages/')

    def test_delete_url_accessible_by_name(self):
        self.redirect_test_with_login(reverse('staff-message-delete', kwargs={'pk':1}), '/staff/messages/')

class SettingsTest(URLTestCase):
    
    def test_settings_redirect_if_not_logged_in(self):
        self.redirect_test(reverse('staff-settings'), '/staff/?next=/staff/settings/')
    
    def test_settings_url_exists_at_desired_location(self):
        self.url_ok_test_with_login('/staff/settings/')

    def test_settings_url_accessible_by_name(self):
        self.url_ok_test_with_login(reverse('staff-settings'))

    def test_settings_uses_correct_template(self):
        self.template_test_with_login(reverse('staff-settings'), 'staff/settings.html')
    
    def test_post_settings_redirect_if_not_logged_in(self):
        response = self.client.post(reverse('staff-settings'), {"shop_name": "Test Shop", "primary_colour": "#01254b", "secondary_colour": "#fee331", "logo": False, "carousel": True}, follow=True)
        self.assertRedirects(response, '/staff/?next=/staff/settings/')
    
    def test_post_settings(self):
        self.login_staff()
        response = self.client.post(reverse('staff-settings'), {"shop_name": "Test Shop", "primary_colour": "#01254b", "secondary_colour": "#fee331", "logo": False, "carousel": True}, follow=True)
        self.assertTemplateUsed(response, 'staff/settings.html')