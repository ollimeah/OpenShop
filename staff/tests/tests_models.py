from django.utils import timezone
from staff.models import *
from django.test import TestCase
import uuid
from random import randint
from decimal import Decimal
from math import ceil
from django.core.files.uploadedfile import SimpleUploadedFile
from os.path import exists as path_exists

class DeviceTest(TestCase):

    def test_new_device_id(self):
        num_devices = len(Device.objects.all())
        code = Device.get_new_device_id()
        self.assertTrue(isinstance(code, uuid.UUID))
        self.assertEqual(num_devices + 1, len(Device.objects.all()))

class BasketTest(TestCase):
    fixtures = ['categories.json', 'products.json', 'collections.json', 'promotions.json']

    def create_empty_basket(self):
        device = Device.objects.create()
        return Basket.objects.create(device=device), device
    
    def add_products(self, basket):
        prices = []
        for product in Product.objects.filter(available=True)[:3]:
            quantity = randint(1, 1000)
            prices.append(product.price * quantity)
            BasketProduct.objects.create(basket=basket, product=product, quantity=quantity)
        return prices
    
    def add_collections(self, basket):
        prices = []
        for collection in Collection.objects.filter(available=True)[:3]:
            quantity = randint(1, 1000)
            prices.append(collection.price * quantity)
            BasketCollection.objects.create(basket=basket, collection=collection, quantity=quantity)
        return prices
    
    def create_product_basket(self):
        basket, _ = self.create_empty_basket()
        return basket, self.add_products(basket)
    
    def create_collection_basket(self):
        basket, _ = self.create_empty_basket()
        return basket, self.add_collections(basket)
    
    def create_full_basket(self):
        basket, _ = self.create_empty_basket()
        prices = self.add_collections(basket) + self.add_products(basket)
        return basket, prices
    
    def create_perc_promo_basket(self):
        basket, _ = self.create_empty_basket()
        promotion = Promotion.objects.get(id=1)
        promotion.expiry = timezone.now() + timezone.timedelta(days=1)
        promotion.save()
        product = Product.objects.get(id=1)
        quantity = ceil(promotion.min_spend / product.price)
        BasketProduct.objects.create(basket=basket, product=product, quantity=quantity)
        return basket, promotion
    
    def create_fix_promo_basket(self):
        basket, _ = self.create_empty_basket()
        promotion = Promotion.objects.get(id=2)
        promotion.expiry = timezone.now() + timezone.timedelta(days=1)
        promotion.save()
        product = Product.objects.get(id=1)
        quantity = ceil(promotion.min_spend / product.price)
        BasketProduct.objects.create(basket=basket, product=product, quantity=quantity)
        return basket, promotion

    def test_get_existing_basket(self):
        new_basket, device = self.create_empty_basket()
        num_baskets = len(Basket.objects.all())
        basket = Basket.get_basket(device_code=device.code)
        self.assertTrue(isinstance(basket, Basket))
        self.assertEqual(basket, new_basket)
        self.assertEqual(device, basket.device)
        self.assertEqual(num_baskets, len(Basket.objects.all()))

    def test_get_new_basket(self):
        device = Device.objects.create()
        num_baskets = len(Basket.objects.all())
        basket = Basket.get_basket(device.code)
        self.assertTrue(isinstance(basket, Basket))
        self.assertEqual(num_baskets + 1, len(Basket.objects.all()))
        self.assertEqual(device, basket.device)

    def test_num_items_empty(self):
        basket, _ = self.create_empty_basket()
        self.assertEqual(basket.num_items, 0)

    def test_num_items(self):
        basket, _ = self.create_empty_basket()
        quantities = []
        for product in Product.objects.filter(available=True)[:3]:
            quantities.append(randint(1, 1000))
            BasketProduct.objects.create(basket=basket, product=product, quantity=quantities[-1])
        self.assertEqual(basket.num_items, sum(quantities))

    def test_item_cost_empty(self):
        basket, _ = self.create_empty_basket()
        self.assertEqual(basket.item_cost, 0)

    def test_item_cost_products(self):
        basket, prices = self.create_product_basket()
        self.assertEqual(basket.item_cost, sum(prices))
    
    def test_item_cost_collections(self):
        basket, prices = self.create_collection_basket()
        self.assertEqual(basket.item_cost, sum(prices))

    def test_item_cost_full(self):
        basket, prices = self.create_full_basket()
        self.assertEqual(basket.item_cost, sum(prices))

    def test_total_cost_empty(self):
        basket, _ = self.create_empty_basket()
        self.assertEqual(basket.total_cost, 0)
    
    def test_total_cost(self):
        basket, prices = self.create_full_basket()
        delivery = Delivery.objects.create(name='New Delivery', price=Decimal(3.99), available=True)
        basket.delivery = delivery
        basket.save()
        prices.append(delivery.price)
        self.assertEqual(basket.total_cost, sum(prices))
    
    def test_final_price_no_promotion(self):
        basket, prices = self.create_full_basket()
        delivery = Delivery.objects.create(name='New Delivery', price=Decimal(3.99), available=True)
        basket.delivery = delivery
        basket.save()
        prices.append(delivery.price)
        self.assertEqual(basket.final_price, sum(prices))
    
    def test_final_price_with_promotion(self):
        basket, promotion = self.create_perc_promo_basket()
        delivery = Delivery.objects.create(name='New Delivery', price=Decimal(3.99), available=True)
        basket.delivery = delivery
        basket.save()
        basket.promotion = promotion
        total = 0
        for bp in basket.basketproduct_set.all():
            total += bp.quantity * bp.product.price
        for bc in basket.basketcollection_set.all():
            total += bc.quantity * bp.collection.price
        promo_amount = Decimal(promotion.amount/100) * total
        total += delivery.price
        promo_amount = min(promotion.max_discount, round(promo_amount, 2))
        self.assertEqual(basket.final_price, total - promo_amount) 

    def test_add_valid_promotion(self):
        basket, promotion = self.create_perc_promo_basket()
        basket.add_promotion(promotion)
        self.assertIsNotNone(basket.promotion)
        self.assertEqual(promotion, basket.promotion)

    def test_add_invalid_promotion(self):
        basket, _ = self.create_empty_basket()
        promotion = Promotion.objects.get(id=1)
        promotion.min_spend = 10
        promotion.save()
        basket.add_promotion(promotion)
        self.assertIsNone(basket.promotion)
    
    def test_fixed_promotion_amount(self):
        basket, promotion = self.create_fix_promo_basket()
        basket.promotion = promotion
        total = 0
        for bp in basket.basketproduct_set.all():
            total += bp.quantity * bp.product.price
        for bc in basket.basketcollection_set.all():
            total += bc.quantity * bp.collection.price
        self.assertEqual(basket.promotion_amount, promotion.amount) 
        self.assertEqual(basket.promotion_cost, total - promotion.amount)    
    
    def test_percentage_promotion(self):
        basket, promotion = self.create_perc_promo_basket()
        basket.promotion = promotion
        total = 0
        for bp in basket.basketproduct_set.all():
            total += bp.quantity * bp.product.price
        for bc in basket.basketcollection_set.all():
            total += bc.quantity * bp.collection.price
        promo_amount = Decimal(promotion.amount/100) * total
        promo_amount = min(promotion.max_discount, round(promo_amount, 2))
        self.assertEqual(basket.promotion_amount, promo_amount) 
        self.assertEqual(basket.promotion_cost, total - promo_amount)     
    
    def test_update_product_quantity(self):
        basket, _ = self.create_empty_basket()
        product = Product.objects.get(id=1)
        bp = BasketProduct.objects.create(basket=basket, product=product, quantity=1)
        bp_id = bp.id
        basket.update_product_quantity(product, product.max)
        self.assertEqual(BasketProduct.objects.get(id=bp_id).quantity, product.max)
        basket.update_product_quantity(product, -1)
        self.assertEqual(len(BasketProduct.objects.filter(id=bp_id)), 0)

    def test_update_collection_quantity(self):
        basket, _ = self.create_empty_basket()
        collection = Collection.objects.get(id=1)
        bc = BasketCollection.objects.create(basket=basket, collection=collection, quantity=1)
        bc_id = bc.id
        basket.update_collection_quantity(collection, 13)
        self.assertEqual(BasketCollection.objects.get(id=bc_id).quantity, 13)
        basket.update_collection_quantity(collection, -1)
        self.assertEqual(len(BasketCollection.objects.filter(id=bc_id)), 0)

    def test_get_and_remove_unavailable_items(self):
        basket, _ = self.create_empty_basket()
        product = Product.objects.filter(available=False)[:1]
        BasketProduct.objects.create(basket=basket, product=product[0], quantity=2)
        collection = Collection.objects.filter(available=False)[:1]
        BasketCollection.objects.create(basket=basket, collection=collection[0], quantity=2)
        unavailable = basket.get_and_remove_unavailable_items()
        self.assertNotIn(product[0], basket.products.all())
        self.assertNotIn(collection[0], basket.collections.all())
        self.assertIn(product[0], unavailable)
        self.assertIn(collection[0], unavailable)

    def test_add_product(self):
        basket, _ = self.create_empty_basket()
        product = Product.objects.get(id=1)
        quantity = product.max
        basket.add_product(product, quantity)
        self.assertIn(product, basket.products.all())
        bp = BasketProduct.objects.get(basket=basket, product=product)
        self.assertEqual(bp.quantity, quantity)

    def test_add_collection(self):
        basket, _ = self.create_empty_basket()
        collection = Collection.objects.get(id=1)
        quantity = randint(1, 1000)
        basket.add_collection(collection, quantity)
        self.assertIn(collection, basket.collections.all())
        bc = BasketCollection.objects.get(basket=basket, collection=collection)
        self.assertEqual(bc.quantity, quantity)
    
    def test_contains_available_empty(self):
        basket, _ = self.create_empty_basket()
        self.assertFalse(basket.contains_available())
    
    def test_contains_available_with_available_products(self):
        basket, _ = self.create_product_basket()
        self.assertTrue(basket.contains_available())
    
    def test_contains_available_with_available_collections(self):
        basket, _ = self.create_collection_basket()
        self.assertTrue(basket.contains_available())
    
    def test_contains_available_with_unavailable_collections(self):
        basket, _ = self.create_collection_basket()
        basket.collections.all().update(available=False)
        self.assertFalse(basket.contains_available())
    
    def test_contains_available_with_unavailable_products(self):
        basket, _ = self.create_product_basket()
        basket.products.all().update(available=False)
        self.assertFalse(basket.contains_available())

class BasketProductTest(TestCase):
    fixtures = ['categories.json', 'products.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = Product.objects.get(id=1)
        device = Device.objects.create()
        basket = Basket.objects.create(device=device)
        cls.bp = BasketProduct.objects.create(basket=basket, quantity=randint(1, 1000), product=cls.product)

    def create_basket_product(self, quantity):
        self.bp.quantity = quantity
        self.bp.save()
        return self.bp

    def test_total_cost(self):
        quantity = randint(1, 1000)
        bp = self.create_basket_product(quantity)
        self.assertEqual(self.product.price * quantity, bp.total_cost)
    
    def test_update_quantity_less_than_min(self):
        self.bp.update_quantity(self.product.min - randint(1, 1000))
        self.assertEqual(self.product.min, self.bp.quantity)
    
    def test_update_quantity_equal_min(self):
        self.bp.update_quantity(self.product.min)
        self.assertEqual(self.product.min, self.bp.quantity)
    
    def test_update_quantity_valid(self):
        quantity = self.product.min + 1
        self.bp.update_quantity(quantity)
        self.assertEqual(quantity, self.bp.quantity)
    
    def test_update_quantity_equal_max(self):
        self.bp.update_quantity(self.product.max)
        self.assertEqual(self.product.max, self.bp.quantity)
    
    def test_update_quantity_greater_than_max(self):
        self.bp.update_quantity(self.product.max + randint(1, 1000))
        self.assertEqual(self.product.max, self.bp.quantity)
    
    def test_add_quantity_negative(self):
        bp = self.create_basket_product(self.product.min)
        bp.add_quantity(-1)
        self.assertEqual(self.product.min, bp.quantity)
    
    def test_add_quantity_valid(self):
        bp = self.create_basket_product(self.product.min)
        bp.add_quantity(1)
        self.assertEqual(self.product.min + 1, bp.quantity)
    
    def test_add_quantity_greater_than_max(self):
        bp = self.create_basket_product(self.product.max)
        bp.add_quantity(1)
        self.assertEqual(self.product.max, bp.quantity)

class BasketCollectionTest(TestCase):
    fixtures = ['categories.json', 'products.json', 'collections.json']
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.collection = Collection.objects.get(id=1)
        device = Device.objects.create()
        basket = Basket.objects.create(device=device)
        cls.bc = BasketCollection.objects.create(basket=basket, collection=cls.collection, quantity=randint(1, 1000))
    
    def test_total_cost(self):
        self.assertEqual(self.collection.price * self.bc.quantity, self.bc.total_cost)
    
    def test_add_quantity(self):
        quantity = self.bc.quantity
        self.bc.add_quantity(3)
        self.assertEqual(quantity + 3, self.bc.quantity)

class CategoryTest(TestCase):
    fixtures = ['categories.json', 'products.json']
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = Category.objects.create(name='Test')

    def test_string(self):
        self.assertEqual(self.category.name, str(self.category))
    
    def test_delete(self):
        category = Category.objects.create(name='TestDel')
        for product in Product.objects.all()[:2]:
            product.category = category
            product.save()
        num_products = Product.objects.count()
        num_categories = Category.objects.count()
        category.delete()
        self.assertEqual(num_categories - 1, Category.objects.count())
        self.assertEqual(num_products - 2, Product.objects.count())
    
    def test_items(self):
        products = []
        for product in Product.objects.all()[:2]:
            product.category = self.category
            product.save()
            products.append(product)
        items = self.category.items()
        for product in products:
            self.assertIn(product, items)
    
    def test_item_count(self):
        self.assertEqual(0, self.category.item_count)
        for product in Product.objects.all()[:2]:
            product.category = self.category
            product.save()
        self.assertEqual(2, self.category.item_count)
    
    def test_add_products(self):
        self.category.add_products(Product.objects.all()[:2])
        for product in Product.objects.all()[:2]:
            self.assertEqual(self.category, product.category)
        self.assertEqual(2, Product.objects.filter(category=self.category).count())

class ProductTest(TestCase):
    fixtures = ['categories.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = Category.objects.get(id=1)
        cls.product = Product.objects.create(name="TestP", description='Test', price=10, category=cls.category,
            image=SimpleUploadedFile('test.jpg', b'content'), available=True, hidden=False, min=1, max=12)

    def tearDown(self):
        for prod in Product.objects.all(): prod.image.delete()
        return super().tearDown()
    
    def create_product(self, name='Test', available=True, hidden=False, file_name='test'):
        prod = Product.objects.create(name=name, description='Test', price=10, category=self.category,
            image=SimpleUploadedFile(file_name + '.jpg', b'content'), available=available, hidden=hidden, min=1, max=12)
        return prod

    def test_str(self):
        self.assertEqual(self.product.name, str(self.product))
    
    def test_hide(self):
        self.product.hide()
        self.assertTrue(self.product.hidden)
    
    def test_delete(self):
        product = self.create_product()
        img_path = product.image.path
        product.delete()
        self.assertFalse(path_exists(img_path))
    
    def test_set_available(self):
        self.product.available = False
        self.product.hidden = True
        self.product.set_available()
        self.assertTrue(self.product.available)
        self.assertFalse(self.product.hidden)
    
    def test_set_unavailable(self):
        self.product.available = True
        self.product.set_unavailable()
        self.assertFalse(self.product.available)
    
    def test_hide_products(self):
        self.create_product()
        products = Product.objects.all()[:3]
        for product in products:
            product.hidden = False
        Product.hide_products(products)
        for product in products:
            self.assertTrue(product.hidden)
    
    def test_delete_products(self):
        paths = []
        products = []
        for i in range(1,4):
            product = self.create_product(name='test' + str(i), file_name='test' + str(i))
            products.append(product)
            paths.append(product.image.path)
        Product.delete_products(products)
        for path in paths:
            self.assertFalse(path_exists(path))
    
    def test_make_products_available(self):
        products = Product.objects.all()[:3]
        for product in products:
            product.available = False
        Product.make_products_available(products)
        for product in products:
            self.assertTrue(product.available)
            self.assertFalse(product.hidden)
    
    def test_make_products_unavailable(self):
        products = Product.objects.all()[:3]
        for product in products:
            product.available = True
        Product.make_products_unavailable(products)
        for product in products:
            self.assertFalse(product.available)
    
    def test_num_available(self):
        for i in range(randint(1, 20)):
            self.create_product(name='Test'+str(i))
        self.assertEqual(Product.num_available(), Product.objects.filter(available=True, hidden=False).count())
    
    def test_num_sold(self):
        num_sold = 0
        for i in range(randint(3, 20)):
            order = Order.objects.create()
            quantity = randint(1, 1000)
            num_sold += quantity
            OrderProduct.objects.create(order=order, product_name=self.product.name, quantity=quantity, price=self.product.price)
        self.assertEqual(num_sold, self.product.num_sold)
    
    def test_num_sold_today(self):
        num_sold = 0
        for i in range(randint(3, 20)):
            order = Order.objects.create()
            quantity = randint(1, 1000)
            num_sold += quantity
            OrderProduct.objects.create(order=order, product_name=self.product.name, quantity=quantity, price=self.product.price)
        self.assertEqual(num_sold, self.product.num_sold_today)

    def test_num_in_basket(self):
        device = Device.objects.create()
        basket = Basket.objects.create(device=device) 
        num = 0
        for i in range(randint(2, 10)):
            quantity = randint(1, 100)
            num += quantity
            BasketProduct.objects.create(basket=basket, product=self.product, quantity=quantity)
        self.assertEqual(num, self.product.num_in_basket)
    
    def test_total_sales(self):
        total = 0
        for i in range(randint(3, 20)):
            order = Order.objects.create()
            quantity = randint(1, 1000)
            total += quantity * self.product.price
            OrderProduct.objects.create(order=order, product_name=self.product.name, quantity=quantity, price=self.product.price)
        self.assertEqual(total, self.product.total_sales)
    
    def test_best_sellers(self):
        products = []
        for i in range(1,6):
            product = self.create_product(name='Test'+str(i))
            order = Order.objects.create()
            OrderProduct.objects.create(order=order, product_name=product.name, quantity=6-i, price=product.price)
            products.append(product)
        self.assertEqual(products, Product.best_sellers(5))

class ProductImageTest(TestCase):
    fixtures = ['categories.json']

    def tearDown(self):
        for prod in Product.objects.all(): prod.image.delete()
        return super().tearDown()
    
    def create_product_image(self):
        category = Category.objects.get(id=1)
        prod = Product.objects.create(name='Test', description='Test', price=10, category=category,
            image=SimpleUploadedFile('test' + '.jpg', b'content'), available=True, hidden=False, min=1, max=12)
        prod_img = ProductImage.objects.create(product=prod, image=SimpleUploadedFile('test2' + '.jpg', b'content'))
        return prod_img
    
    def test_delete(self):
        product_image = self.create_product_image()
        img_path = product_image.image.path
        product_image.delete()
        self.assertFalse(path_exists(img_path))

class CollectionTest(TestCase):
    fixtures = ['collections.json', 'categories.json', 'products.json']
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.collection = Collection.objects.create(name='name', price=10, available=True, hidden=False)

    def create_collection(self, name='Test', price=10, available=True, hidden=False):
        collection = Collection.objects.create(name=name, price=price, available=available, hidden=hidden)
        return collection

    def test_add_products(self):
        self.collection.add_products(Product.objects.all())
        for product in Product.objects.all():
            self.assertIn(product, self.collection.products.all())
    
    def test_get_visible(self):
        for collection in Collection.get_visible():
            self.assertFalse(collection.hidden)

    def test_num_sold(self):
        num_sold = 0
        for i in range(randint(3, 20)):
            order = Order.objects.create()
            quantity = randint(1, 1000)
            num_sold += quantity
            OrderCollection.objects.create(order=order, collection_name=self.collection.name, quantity=quantity, price=self.collection.price)
        self.assertEqual(num_sold, self.collection.num_sold)
    
    def test_num_sold_today(self):
        num_sold = 0
        for i in range(randint(3, 20)):
            order = Order.objects.create()
            quantity = randint(1, 1000)
            num_sold += quantity
            OrderCollection.objects.create(order=order, collection_name=self.collection.name, quantity=quantity, price=self.collection.price)
        self.assertEqual(num_sold, self.collection.num_sold_today)

    def test_num_in_basket(self):
        device = Device.objects.create()
        basket = Basket.objects.create(device=device) 
        num = 0
        for i in range(randint(2, 10)):
            quantity = randint(1, 100)
            num += quantity
            BasketCollection.objects.create(basket=basket, collection=self.collection, quantity=quantity)
        self.assertEqual(num, self.collection.num_in_basket)
    
    def test_total_sales(self):
        total = 0
        for i in range(randint(3, 20)):
            order = Order.objects.create()
            quantity = randint(1, 1000)
            total += quantity * self.collection.price
            OrderCollection.objects.create(order=order, collection_name=self.collection.name, quantity=quantity, price=self.collection.price)
        self.assertEqual(total, self.collection.total_sales)

class PromotionTest(TestCase):
    fixtures = ['promotions.json']
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fix = Promotion.objects.get(id=2)
        cls.fix.expiry = timezone.now() + timezone.timedelta(days=1)
        cls.fix.active = True
        cls.fix.used = 0
        cls.perc = Promotion.objects.get(id=1)
        cls.perc.expiry = timezone.now() + timezone.timedelta(days=1)
        cls.perc.active = True
        cls.perc.used = 0

    def get_active_perc_promotion(self):
        promo = Promotion.objects.get(id=1)
        promo.expiry = timezone.now() + timezone.timedelta(days=1)
        promo.active = True
        promo.used = 0
        return promo

    def get_active_fixed_promotion(self):
        promo = Promotion.objects.get(id=2)
        promo.expiry = timezone.now() + timezone.timedelta(days=1)
        promo.active = True
        promo.used = 0
        return promo

    def test_is_eligible_max_used(self):
        self.perc.used = self.perc.max_uses
        eligible = self.perc.is_eligible(50)
        self.assertFalse(self.perc.active)
        self.assertFalse(eligible)
    
    def test_is_eligible_expired(self):
        self.perc.expiry = timezone.now() - timezone.timedelta(days=1)
        eligible = self.perc.is_eligible(50)
        self.assertFalse(self.perc.active)
        self.assertFalse(eligible)
    
    def test_is_eligible_inactive(self):
        self.perc.active = False
        self.assertFalse(self.perc.is_eligible(50))
    
    def test_is_eligible_active(self):
        self.assertTrue(self.perc.is_eligible(self.perc.min_spend))

    def test_is_eligible_less_than_min(self):
        promo = self.get_active_perc_promotion()
        promo.min_spend = 30
        self.assertFalse(promo.is_eligible(promo.min_spend - 5))
    
    def test_is_eligible_equal_to_min(self):
        promo = self.get_active_perc_promotion()
        self.assertTrue(promo.is_eligible(promo.min_spend))
    
    def test_is_eligible_greater_than_min(self):
        promo = self.get_active_perc_promotion()
        promo.min_spend = 30
        self.assertTrue(promo.is_eligible(promo.min_spend + 5))
    
    def test_set_used(self):
        used = self.perc.used
        self.perc.set_used()
        self.assertEqual(used + 1, self.perc.used)
    
    def test_get_discount_fixed(self):
        self.assertEqual(self.fix.get_discount(self.fix.min_spend + 5), self.fix.amount)    
    
    def test_get_discount_percentage_less_than_max(self):
        total = self.perc.min_spend + self.perc.max_discount - 1
        promo_amount = Decimal(self.perc.amount/100) * total
        self.assertEqual(self.perc.get_discount(total), round(promo_amount, 2))
    
    def test_get_discount_percentage_equal_to_max(self):
        total = self.perc.min_spend + self.perc.max_discount
        promo_amount = Decimal(self.perc.amount/100) * total
        self.assertEqual(self.perc.get_discount(total), round(promo_amount, 2))
    
    def test_get_discount_percentage_greater_than_max(self):
        total = self.perc.min_spend + self.perc.max_discount + 1
        promo_amount = Decimal(self.perc.max_discount/100) * total
        self.assertEqual(self.perc.get_discount(total), round(promo_amount, 2))
    
    def test_disable_all(self):
        Promotion.objects.all().update(active=True)
        Promotion.disable_all()
        for promo in Promotion.objects.all():
            self.assertFalse(promo.active)
    
    def test_total_saved(self):
        total = 0
        for i in range(randint(1, 10)):
            amount = randint(1, 1000)
            total += amount
            Order.objects.create(promotion_code=self.perc.code, discount_amount=amount)
        self.assertEqual(total, self.perc.total_saved)

class DeliveryTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.delivery = Delivery.objects.create(name="name", price=10)
    
    def test_to_string(self):
        self.assertEqual(self.delivery.name, str(self.delivery))
    
    def test_num_used(self):
        orders = randint(1, 10)
        for i in range(orders):
            OrderShipping.objects.create(order=Order.objects.create(), address_name='Test Name', line_1='Test Line 1', 
                city='Test City', postcode='A12 3BC', delivery_name=self.delivery.name, delivery_price=self.delivery.price)
        self.assertEqual(orders, self.delivery.num_used)

class OrderTest(TestCase):
    fixtures = ['categories.json', 'products.json', 'collections.json', 'promotions.json']

    def create_empty_basket(self):
        Device.objects.all().delete()
        device = Device.objects.create()
        return Basket.objects.create(device=device), device
    
    def create_address(self, name='Test Name', line_1='Test Line 1', line_2='Test Line 2', city='Test City', county='Test County', postcode='A12 3BC'):
        address = Address.objects.create(name=name, line_1=line_1, line_2=line_2, city=city, county=county, postcode=postcode)
        return address
    
    def create_delivery(self, name='Test Delivery'):
        delivery = Delivery.objects.create(name=name, price=10)
        return delivery

    def add_products(self, basket):
        prices = []
        for product in Product.objects.filter(available=True)[:3]:
            quantity = randint(1, 1000)
            prices.append(product.price * quantity)
            BasketProduct.objects.create(basket=basket, product=product, quantity=quantity)
        return prices
    
    def add_collections(self, basket):
        prices = []
        for collection in Collection.objects.filter(available=True)[:3]:
            quantity = randint(1, 1000)
            prices.append(collection.price * quantity)
            BasketCollection.objects.create(basket=basket, collection=collection, quantity=quantity)
        return prices
    
    def get_promotion(self):
        promo = Promotion.objects.get(id=1)
        promo.expiry = timezone.now() + timezone.timedelta(days=1)
        promo.active = True
        promo.used = 0
        return promo

    def create_full_basket(self):
        basket, _ = self.create_empty_basket()
        prices = self.add_collections(basket) + self.add_products(basket)
        basket.address = self.create_address()
        basket.delivery = self.create_delivery()
        basket.promotion = self.get_promotion()
        return basket, prices
    
    def test_create_order(self):
        basket, _ = self.create_full_basket()
        num_orders = Order.objects.count()
        Order.create_order_and_empty_basket(basket)
        self.assertEqual(num_orders + 1, Order.objects.count())

    def test_create_promotion(self):
        basket, _ = self.create_full_basket()
        discount = basket.promotion_amount
        order = Order.create_order_and_empty_basket(basket)
        self.assertEqual(basket.promotion.code, order.promotion_code)
        self.assertEqual(discount, order.discount_amount)
    
    def test_create_order_shipping(self):
        basket, _ = self.create_full_basket()
        order = Order.create_order_and_empty_basket(basket)
        self.assertEqual(basket.address.name, order.ordershipping.address_name)
        self.assertEqual(basket.address.line_1, order.ordershipping.line_1)
        self.assertEqual(basket.address.line_2, order.ordershipping.line_2)
        self.assertEqual(basket.address.city, order.ordershipping.city)
        self.assertEqual(basket.address.county, order.ordershipping.county)
        self.assertEqual(basket.address.postcode, order.ordershipping.postcode)
    
    def test_create_order_products(self):
        basket, _ = self.create_full_basket()
        order = Order.create_order_and_empty_basket(basket)
        for bp in basket.basketproduct_set.all():
            op = OrderProduct.objects.filter(order=order, product_name=bp.product.name, quantity=bp.quantity, price=bp.product.price).count()
            self.assertEqual(1, op)
    
    def test_create_order_collections(self):
        basket, _ = self.create_full_basket()
        order = Order.create_order_and_empty_basket(basket)
        for bc in basket.basketcollection_set.all():
            oc = OrderCollection.objects.filter(order=order, collection_name=bc.collection.name, quantity=bc.quantity, price=bc.collection.price).count()
            self.assertEqual(1, oc)
            for product in bc.collection.products.all():
                ocp = OrderCollectionProduct.objects.filter(order_collection=oc, product_name=product.name).count()
                self.assertEqual(1, ocp)
    
    def test_delete_address(self):
        basket, _ = self.create_full_basket()
        num_addresses = Address.objects.count()
        Order.create_order_and_empty_basket(basket)
        self.assertIsNone(basket.address.id)
        self.assertEqual(num_addresses - 1, Address.objects.count())
    
    def test_delete_basket(self):
        basket, _ = self.create_full_basket()
        num_baskets = Basket.objects.count()
        Order.create_order_and_empty_basket(basket)
        self.assertEqual(num_baskets - 1, Basket.objects.count())
    
    def test_num_orders_today(self):
        num_orders = randint(1, 20)
        for i in range(num_orders):
            basket, _ = self.create_full_basket()
            Order.create_order_and_empty_basket(basket)
        self.assertEqual(num_orders, Order.num_orders_today())
    
    def test_item_total_cost(self):
        basket, prices = self.create_full_basket()
        order = Order.create_order_and_empty_basket(basket)
        self.assertEqual(order.item_total_cost, sum(prices))
    
    def test_item_total_with_discount(self):
        basket, prices = self.create_full_basket()
        total = sum(prices) - basket.promotion_amount
        order = Order.create_order_and_empty_basket(basket)
        self.assertEqual(order.item_total_with_discount, total)
    
    def test_final_price(self):
        basket, prices = self.create_full_basket()
        total = sum(prices) - basket.promotion_amount
        total += Delivery.objects.get(name='Test Delivery').price
        order = Order.create_order_and_empty_basket(basket)
        self.assertEqual(order.final_price, total)
    
    def test_sales_today(self):
        num_orders = randint(1, 20)
        total = 0
        for i in range(num_orders):
            basket, prices = self.create_full_basket()
            total += sum(prices) - basket.promotion_amount
            Order.create_order_and_empty_basket(basket)
        self.assertEqual(total, Order.sales_today())
    
    def test_recent_orders(self):
        num_orders = randint(1, 20)
        orders = []
        for i in range(num_orders):
            basket, _ = self.create_full_basket()
            order = Order.create_order_and_empty_basket(basket)
            orders.append(order)
        orders.reverse()
        self.assertEqual(orders, list(Order.recent_orders(num_orders)))

    def test_num_items(self):
        basket, _ = self.create_full_basket()
        order = Order.create_order_and_empty_basket(basket)
        items = 0
        for op in OrderProduct.objects.filter(order=order): items += op.quantity
        for oc in OrderCollection.objects.filter(order=order): items += oc.quantity
        self.assertEqual(items, order.num_items)
    
    def test_toggle_shipped(self):
        order = Order.objects.create()
        self.assertFalse(order.shipped)
        order.toggle_shipped()
        self.assertTrue(order.shipped)
        order.toggle_shipped()
        self.assertFalse(order.shipped)

class OrderProductTest(TestCase):

    def test_total_cost(self):
        order = Order.objects.create()
        quantity = randint(1, 1000)
        price = randint(1, 10000) / 100
        op = OrderProduct.objects.create(order=order, product_name='Test', quantity=quantity, price=price)
        self.assertEqual(quantity * price, op.total_cost)

class OrderCollectionTest(TestCase):

    def test_total_cost(self):
        order = Order.objects.create()
        quantity = randint(1, 1000)
        price = randint(1, 10000) / 100
        oc = OrderCollection.objects.create(order=order, collection_name='Test', quantity=quantity, price=price)
        self.assertEqual(quantity * price, oc.total_cost)