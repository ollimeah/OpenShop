from staff.models import Category, Product
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

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