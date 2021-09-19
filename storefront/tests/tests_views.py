from django.http.cookie import SimpleCookie
from staff.models import Address, Basket, BasketCollection, BasketProduct, Category, Collection, Delivery, Device, Order, Product, Promotion
from django.test import TestCase, override_settings
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

class OrderTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = Device.objects.create()
        category = Category.objects.create(name="Test")
        cls.product = Product.objects.create(name="Test", description='Test', price=10, category=category,
            image=SimpleUploadedFile("test" + '.jpg', b'content'), available=True, hidden=False, min=1, max=12)
        cls.delivery = Delivery.objects.create(name="Test", price=10)
        cls.collection = Collection.objects.create(name="Test", description='Test', price=10,
            image=SimpleUploadedFile("test" + '.jpg', b'content'), available=True, hidden=False)
        cls.address = Address.objects.create(name='Test Name', email='test@test.com', line_1='test road', city='test city', postcode='ab1 cb2')
        return super().setUpTestData()
    
    @classmethod
    def tearDownClass(cls):
        for prod in Product.objects.all(): prod.image.delete()
        for collection in Collection.objects.all(): collection.image.delete()
        return super().tearDownClass()

    def setUp(self):
        self.basket = Basket.objects.create(device=self.device)
        self.client.cookies = SimpleCookie({'device':self.device.code})
        return super().setUp()
    
    def add_basket_product(self):
        BasketProduct.objects.create(basket=self.basket, product=self.product, quantity=3)
    
    def add_basket_collection(self):
        BasketCollection.objects.create(basket=self.basket, collection=self.collection, quantity=3)
    
    def add_shipping(self):
        self.basket.address = self.address
        self.basket.save()
    
    def add_delivery(self):
        self.basket.delivery = self.delivery
        self.basket.save()

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

class BasketTest(URLTestCase, OrderTestCase):
    
    def test_basket_url_exists_at_desired_location(self):
        self.url_ok_test('/basket/')

    def test_basket_url_accessible_by_name(self):
        self.url_ok_test(reverse('basket'))

    def test_basket_uses_correct_template(self):
        self.template_test(reverse('basket'), 'storefront/order/basket.html')
    
    def test_add_product_to_basket_get(self):
        response = self.client.get(reverse('basket-add-product'))
        self.assertEqual(response.status_code, 405)
    
    def test_add_product_to_basket_post_valid(self):
        data = {'product_name':self.product.name, 'quantity':self.product.min}
        response = self.client.post(reverse('basket-add-product'), data, follow=True)
        self.assertEqual(response.status_code, 204)
    
    def test_add_product_to_basket_post_invalid_quantity(self):
        data = {'product_name':self.product.name, 'quantity':'a'}
        response = self.client.post(reverse('basket-add-product'), data, follow=True)
        self.assertEqual(response.status_code, 406)
    
    def test_add_product_to_basket_post_invalid_product(self):
        data = {'product_name':'invalid_name', 'quantity':self.product.min}
        response = self.client.post(reverse('basket-add-product'), data, follow=True)
        self.assertEqual(response.status_code, 404)
    
    def test_add_collection_to_basket_get(self):
        response = self.client.get(reverse('basket-add-collection'))
        self.assertEqual(response.status_code, 405)
    
    def test_add_collection_to_basket_post_valid(self):
        data = {'collection_name':self.collection.name, 'quantity':2}
        response = self.client.post(reverse('basket-add-collection'), data, follow=True)
        self.assertEqual(response.status_code, 204)
    
    def test_add_collection_to_basket_post_invalid_quantity(self):
        data = {'collection_name':self.collection.name, 'quantity':'a'}
        response = self.client.post(reverse('basket-add-collection'), data, follow=True)
        self.assertEqual(response.status_code, 406)
    
    def test_add_collection_to_basket_post_invalid_collection(self):
        data = {'collection_name':'invalid_name', 'quantity':2}
        response = self.client.post(reverse('basket-add-collection'), data, follow=True)
        self.assertEqual(response.status_code, 404)
    
    def test_update_product_quantity_get(self):
        response = self.client.get(reverse('basket-update-product'))
        self.assertEqual(response.status_code, 405)
    
    def test_update_product_quantity_post_valid_zero_quantity(self):
        self.add_basket_product()
        data = {'product_name':self.product.name, 'quantity':0}
        response = self.client.post(reverse('basket-update-product'), data, follow=True)
        self.assertRedirects(response, reverse('basket'))
    
    def test_update_product_quantity_post_valid_non_zero_quantity(self):
        self.add_basket_product()
        quantity = 5
        data = {'product_name':self.product.name, 'quantity':quantity}
        response = self.client.post(reverse('basket-update-product'), data, follow=True)
        price = "{:.2f}".format(self.product.price*quantity)
        json = {'productTotal':price, 'cost':price, 'numItems':quantity}
        self.assertJSONEqual(str(response.content, encoding='utf8'), json)
        self.assertEqual(response.status_code, 200)
    
    def test_update_product_quantity_post_invalid_quantity(self):
        data = {'product_name':self.product.name, 'quantity':'a'}
        response = self.client.post(reverse('basket-update-product'), data, follow=True)
        self.assertEqual(response.status_code, 406)
    
    def test_update_product_quantity_post_invalid_product(self):
        data = {'product_name':'invalid_name', 'quantity':self.product.min}
        response = self.client.post(reverse('basket-update-product'), data, follow=True)
        self.assertEqual(response.status_code, 404)
    
    def test_update_collection_quantity_get(self):
        response = self.client.get(reverse('basket-update-collection'))
        self.assertEqual(response.status_code, 405)
    
    def test_update_collection_quantity_post_valid_zero_quantity(self):
        self.add_basket_collection()
        data = {'collection_name':self.collection.name, 'quantity':0}
        response = self.client.post(reverse('basket-update-collection'), data, follow=True)
        self.assertRedirects(response, reverse('basket'))
    
    def test_update_collection_quantity_post_valid_non_zero_quantity(self):
        self.add_basket_collection()
        quantity = 5
        data = {'collection_name':self.collection.name, 'quantity':quantity}
        response = self.client.post(reverse('basket-update-collection'), data, follow=True)
        price = "{:.2f}".format(self.collection.price*quantity)
        json = {'productTotal':price, 'cost':price, 'numItems':quantity}
        self.assertJSONEqual(str(response.content, encoding='utf8'), json)
        self.assertEqual(response.status_code, 200)
    
    def test_update_product_quantity_post_invalid_quantity(self):
        data = {'collection_name':self.collection.name, 'quantity':'a'}
        response = self.client.post(reverse('basket-update-collection'), data, follow=True)
        self.assertEqual(response.status_code, 406)
    
    def test_update_collection_quantity_post_invalid_collection(self):
        data = {'collection_name':'invalid_name', 'quantity':2}
        response = self.client.post(reverse('basket-update-collection'), data, follow=True)
        self.assertEqual(response.status_code, 404)

class ShippingTest(URLTestCase, OrderTestCase):
    
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
        basket = Basket.objects.get(device=self.device)
        self.assertIsNotNone(basket.address)
        self.assertIsNotNone(basket.delivery)
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
    
class CheckoutTest(URLTestCase, OrderTestCase):
    
    def test_redirects_with_empty_basket(self):
        self.redirect_test('/checkout/', reverse('basket'))
    
    def test_redirects_with_unavailable_basket(self):
        self.add_basket_product()
        self.product.available = False
        self.product.save()
        self.redirect_test('/checkout/', reverse('basket'))
    
    def test_redirects_with_no_address(self):
        self.add_basket_product()
        self.add_delivery()
        response = self.client.get(reverse('checkout'))
        self.assertRedirects(response, reverse('shipping'))
    
    def test_redirects_with_no_delivery(self):
        self.add_basket_product()
        self.add_shipping()
        response = self.client.get(reverse('checkout'))
        self.assertRedirects(response, reverse('shipping'))
    
    def test_redirects_with_no_delivery_and_no_shipping(self):
        self.add_basket_product()
        response = self.client.get(reverse('checkout'))
        self.assertRedirects(response, reverse('shipping'))

    def test_checkout_url_exists_at_desired_location(self):
        self.add_basket_product()
        self.add_shipping()
        self.add_delivery()
        self.url_ok_test('/checkout/')

    def test_checkout_url_accessible_by_name(self):
        self.add_basket_product()
        self.add_shipping()
        self.add_delivery()
        self.url_ok_test(reverse('checkout'))

    def test_checkout_uses_correct_template(self):
        self.add_basket_product()
        self.add_shipping()
        self.add_delivery()
        self.template_test(reverse('checkout'), 'storefront/order/checkout.html')
    
    def test_post_valid_promo(self):
        promotion = Promotion.objects.create(code="Test", type=Promotion.FIXED_PRICE, amount=5)
        self.add_basket_product()
        self.add_shipping()
        self.add_delivery()
        self.client.post(reverse('checkout'), data={'code':promotion.code})
        basket = Basket.objects.get(device=self.device)
        self.assertEqual(basket.promotion, promotion)
    
    def test_post_invalid_promo(self):
        self.add_basket_product()
        self.add_shipping()
        self.add_delivery()
        self.client.post(reverse('checkout'), data={'code':'invalid'})
        basket = Basket.objects.get(device=self.device)
        self.assertIsNone(basket.promotion)

@override_settings(DEBUG=True)
class OrderTest(URLTestCase, OrderTestCase):

    def test_place_order_get(self):
        response = self.client.get(reverse('place-order'), status=405)
        self.assertEqual(response.status_code, 405)

    def test_place_order_get_debug_false(self):
        with self.settings(DEBUG=False):
            response = self.client.get(reverse('place-order'))
            self.assertRedirects(response, reverse('basket'))
    
    def test_place_order_post_debug_false(self):
        self.add_basket_product()
        self.add_shipping()
        self.add_delivery()
        num_orders = Order.objects.count()
        with self.settings(DEBUG=False):
            response = self.client.post(reverse('place-order'), follow=True)
            self.assertRedirects(response, reverse('basket'))
        self.assertEqual(num_orders, Order.objects.count())
    
    def test_place_order_post_valid_basket(self):
        self.add_basket_product()
        self.add_shipping()
        self.add_delivery()
        num_orders = Order.objects.count()
        response = self.client.post(reverse('place-order'), follow=True)
        self.assertRedirects(response, reverse('order-success'))
        self.assertEqual(num_orders + 1, Order.objects.count())
    
    def test_place_order_post_empty_basket(self):
        num_orders = Order.objects.count()
        response = self.client.post(reverse('place-order'), follow=True)
        self.assertRedirects(response, reverse('basket'))
        self.assertEqual(num_orders, Order.objects.count())
    
    def test_place_order_post_no_address(self):
        self.add_basket_product()
        self.add_delivery()
        num_orders = Order.objects.count()
        response = self.client.post(reverse('place-order'), follow=True)
        self.assertRedirects(response, reverse('shipping'))
        self.assertEqual(num_orders, Order.objects.count())
    
    def test_place_order_post_no_delivery(self):
        self.add_basket_product()
        self.add_shipping()
        num_orders = Order.objects.count()
        response = self.client.post(reverse('place-order'), follow=True)
        self.assertRedirects(response, reverse('shipping'))
        self.assertEqual(num_orders, Order.objects.count())

    def test_order_success_url_exists_at_desired_location(self):
        self.url_ok_test('/success/')

    def test_order_success_url_accessible_by_name(self):
        self.url_ok_test(reverse('order-success'))

    def test_order_success_uses_correct_template(self):
        self.template_test(reverse('order-success'), 'storefront/order/success.html')
    
    def test_order_failed_url_exists_at_desired_location(self):
        self.url_ok_test('/failed/')

    def test_order_failed_url_accessible_by_name(self):
        self.url_ok_test(reverse('order-failed'))

    def test_order_failed_uses_correct_template(self):
        self.template_test(reverse('order-failed'), 'storefront/order/failed.html')

class MaintenanceTest(URLTestCase):
    
    def test_maintenance_url_exists_at_desired_location(self):
        self.url_ok_test('/maintenance/')

    def test_maintenance_url_accessible_by_name(self):
        self.url_ok_test(reverse('maintenance'))

    def test_maintenance_uses_correct_template(self):
        self.template_test(reverse('maintenance'), 'storefront/maintenance.html')