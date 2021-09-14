from django.http.cookie import SimpleCookie
from staff.models import Basket, BasketProduct, Category, Collection, Delivery, Device, Product
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from http.cookies import SimpleCookie

class URLTestCase(TestCase):
    def redirect_test(self, get_url, redirect_url):
        response = self.client.get(get_url)
        self.assertRedirects(response, redirect_url)
    
    def url_ok_test(self, get_url):
        response = self.client.get(get_url)
        self.assertEqual(response.status_code, 200)
    
    def template_test(self, get_url, template):
        response = self.client.get(get_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template)

class HomeTest(URLTestCase):

    def test_home_url_exists_at_desired_location(self):
        self.url_ok_test('')

    def test_home_url_accessible_by_name(self):
        self.url_ok_test(reverse('home'))

    def test_home_uses_correct_template(self):
        self.template_test(reverse('home'), 'storefront/home.html')

class ShopTest(URLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Test")
        return super().setUpTestData()

    def test_shop_url_exists_at_desired_location(self):
        self.url_ok_test('/shop/')

    def test_shop_url_accessible_by_name(self):
        self.url_ok_test(reverse('shop'))

    def test_shop_uses_correct_template(self):
        self.template_test(reverse('shop'), 'storefront/shop.html')
    
    def test_shop_category_url_exists_at_desired_location(self):
        self.url_ok_test('/shop/'+self.category.name+'/')

    def test_shop_category_url_accessible_by_name(self):
        self.url_ok_test(reverse('shop-category', kwargs={'category':self.category.name}))

    def test_shop_category_uses_correct_template(self):
        self.template_test(reverse('shop-category', kwargs={'category':self.category.name}), 'storefront/shop.html')

class ProductTest(URLTestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Test")
        cls.product = Product.objects.create(name="Test", description='Test', price=10, category=category,
        image=SimpleUploadedFile("test" + '.jpg', b'content'), available=True, hidden=False, min=1, max=12)
        return super().setUpTestData()
    
    @classmethod
    def tearDownClass(cls):
        for prod in Product.objects.all(): prod.image.delete()
        return super().tearDownClass()

    def test_product_url_exists_at_desired_location(self):
        self.url_ok_test('/shop/product/'+self.product.name+'/')

    def test_product_url_accessible_by_name(self):
        self.url_ok_test(reverse('product', kwargs={'name':self.product.name}))

    def test_product_uses_correct_template(self):
        self.template_test(reverse('product', kwargs={'name':self.product.name}), 'storefront/product.html')

class CollectionTest(URLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.collection = Collection.objects.create(name="Test", description='Test', price=10,
        image=SimpleUploadedFile("test" + '.jpg', b'content'), available=True, hidden=False)
        return super().setUpTestData()
    
    @classmethod
    def tearDownClass(cls):
        for collection in Collection.objects.all(): collection.image.delete()
        return super().tearDownClass()

    def test_collection_url_exists_at_desired_location(self):
        self.url_ok_test('/collections/'+self.collection.name+'/')

    def test_collection_url_accessible_by_name(self):
        self.url_ok_test(reverse('collection', kwargs={'name':self.collection.name}))

    def test_collection_uses_correct_template(self):
        self.template_test(reverse('collection', kwargs={'name':self.collection.name}), 'storefront/collection.html')

class ContactTest(URLTestCase):

    def test_contact_url_exists_at_desired_location(self):
        self.url_ok_test('/contact/')

    def test_contact_url_accessible_by_name(self):
        self.url_ok_test(reverse('contact'))

    def test_contact_uses_correct_template(self):
        self.template_test(reverse('contact'), 'storefront/contact/contact.html')
    
    def test_post_message(self):
        response = self.client.post(reverse('contact'), {'name':'Test', 'email':'test@test.com', 'subject':'test', 'message':'test'}, follow=True)
        self.assertRedirects(response, reverse('message-sent'))
    
    def test_message_sent_url_exists_at_desired_location(self):
        self.url_ok_test('/contact/sent/')

    def test_message_sent_url_accessible_by_name(self):
        self.url_ok_test(reverse('message-sent'))

    def test_message_sent_uses_correct_template(self):
        self.template_test(reverse('message-sent'), 'storefront/contact/sent.html')

class BasketTest(URLTestCase):
    
    def test_basket_url_exists_at_desired_location(self):
        self.url_ok_test('/basket/')

    def test_basket_url_accessible_by_name(self):
        self.url_ok_test(reverse('basket'))

    def test_basket_uses_correct_template(self):
        self.template_test(reverse('basket'), 'storefront/order/basket.html')

class ShippingTest(URLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = Device.objects.create()
        category = Category.objects.create(name="Test")
        cls.product = Product.objects.create(name="Test", description='Test', price=10, category=category,
        image=SimpleUploadedFile("test" + '.jpg', b'content'), available=True, hidden=False, min=1, max=12)
        Delivery.objects.create(name="Test", price=10)
        cls.basket = Basket.objects.create(device=cls.device)
        return super().setUpTestData()
    
    @classmethod
    def tearDownClass(cls):
        for prod in Product.objects.all(): prod.image.delete()
        return super().tearDownClass()

    def setUp(self):
        self.client.cookies = SimpleCookie({'device':self.device.code})
        return super().setUp()
    
    def add_basket_product(self):
        BasketProduct.objects.create(basket=self.basket, product=self.product, quantity=3)
    
    def test_redirects_with_empty_basket(self):
        self.redirect_test('/shipping/', reverse('basket'))
    
    def test_shipping_url_exists_at_desired_location(self):
        self.add_basket_product()
        self.url_ok_test('/shipping/')

    def test_shipping_url_accessible_by_name(self):
        self.add_basket_product()
        self.url_ok_test(reverse('shipping'))

    def test_shipping_uses_correct_template(self):
        self.add_basket_product()
        self.template_test(reverse('shipping'), 'storefront/order/shipping.html')
    
    def test_post_redirect(self):
        self.add_basket_product()
        data = {'name':'Test Name', 'email':'test@test.com', 'line_1':'test road', 'city':'test city', 'postcode':'ab1 cb2', 'delivery':'1'}
        response = self.client.post(reverse('shipping'), data, follow=True)
        self.assertRedirects(response, reverse('checkout'))
    
    def test_post_invalid_delivery(self):
        self.add_basket_product()
        data = {'name':'Test Name', 'email':'test@test.com', 'line_1':'test road', 'city':'test city', 'postcode':'ab1 cb2', 'delivery':'3'}
        response = self.client.post(reverse('shipping'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'storefront/order/shipping.html')
    
    def test_post_invalid_address(self):
        self.add_basket_product()
        data = {'name':'Test Name', 'email':'test@test.com', 'city':'test city', 'postcode':'ab1 cb2', 'delivery':'1'}
        response = self.client.post(reverse('shipping'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'storefront/order/shipping.html')
    
class CheckoutTest(URLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = Device.objects.create()
        category = Category.objects.create(name="Test")
        cls.product = Product.objects.create(name="Test", description='Test', price=10, category=category,
        image=SimpleUploadedFile("test" + '.jpg', b'content'), available=True, hidden=False, min=1, max=12)
        Delivery.objects.create(name="Test", price=10)
        cls.basket = Basket.objects.create(device=cls.device)
        return super().setUpTestData()
    
    @classmethod
    def tearDownClass(cls):
        for prod in Product.objects.all(): prod.image.delete()
        return super().tearDownClass()

    def setUp(self):
        self.client.cookies = SimpleCookie({'device':self.device.code})
        return super().setUp()
    
    def add_basket_product(self):
        BasketProduct.objects.create(basket=self.basket, product=self.product, quantity=3)
    
    def test_redirects_with_empty_basket(self):
        self.redirect_test('/checkout/', reverse('basket'))
    
    def test_redirects_with_unavailable_basket(self):
        self.add_basket_product()
        self.product.available = False
        self.product.save()
        self.redirect_test('/checkout/', reverse('basket'))

    def test_checkout_url_exists_at_desired_location(self):
        self.add_basket_product()
        self.url_ok_test('/checkout/')

    def test_checkout_url_accessible_by_name(self):
        self.add_basket_product()
        self.url_ok_test(reverse('checkout'))

    def test_checkout_uses_correct_template(self):
        self.add_basket_product()
        self.template_test(reverse('checkout'), 'storefront/order/checkout.html')

    def test_order_success_url_exists_at_desired_location(self):
        self.url_ok_test('/success/')

    def test_order_success_url_accessible_by_name(self):
        self.url_ok_test(reverse('order-success'))

    def test_order_success_uses_correct_template(self):
        self.template_test(reverse('order-success'), 'storefront/order/success.html')