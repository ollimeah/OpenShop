from django.utils import timezone
from storefront.models import Basket, BasketCollection, BasketProduct, Device
from staff.models import Address, Category, Collection, Delivery, Order, OrderCollection, OrderCollectionProduct, OrderProduct, Product, Promotion
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
        basket, device = self.create_empty_basket()
        return basket, self.add_products(basket)
    
    def create_collection_basket(self):
        basket, device = self.create_empty_basket()
        return basket, self.add_collections(basket)
    
    def create_full_basket(self):
        basket, device = self.create_empty_basket()
        prices = self.add_collections(basket) + self.add_products(basket)
        return basket, prices
    
    def create_perc_promo_basket(self):
        basket, device = self.create_empty_basket()
        promotion = Promotion.objects.get(id=1)
        promotion.expiry = timezone.now() + timezone.timedelta(days=1)
        promotion.save()
        product = Product.objects.get(id=1)
        quantity = ceil(promotion.min_spend / product.price)
        BasketProduct.objects.create(basket=basket, product=product, quantity=quantity)
        return basket, promotion
    
    def create_fix_promo_basket(self):
        basket, device = self.create_empty_basket()
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
        basket, device = self.create_empty_basket()
        self.assertEqual(basket.num_items, 0)

    def test_num_items(self):
        basket, device = self.create_empty_basket()
        quantities = []
        for product in Product.objects.filter(available=True)[:3]:
            quantities.append(randint(1, 1000))
            BasketProduct.objects.create(basket=basket, product=product, quantity=quantities[-1])
        self.assertEqual(basket.num_items, sum(quantities))

    def test_item_cost_empty(self):
        basket, device = self.create_empty_basket()
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
        basket, device = self.create_empty_basket()
        self.assertEqual(basket.total_cost, 0)
    
    def test_total_cost(self):
        basket, prices = self.create_full_basket()
        delivery = Delivery.objects.create(name='New Delivery', price=Decimal(3.99), available=True)
        basket.delivery = delivery
        basket.save()
        prices.append(delivery.price)
        self.assertEqual(basket.total_cost, sum(prices))

    def test_add_valid_promotion(self):
        basket, promotion = self.create_perc_promo_basket()
        basket.add_promotion(promotion)
        self.assertIsNotNone(basket.promotion)
        self.assertEqual(promotion, basket.promotion)

    def test_add_invalid_promotion(self):
        basket, device = self.create_empty_basket()
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
        basket, device = self.create_empty_basket()
        product = Product.objects.get(id=1)
        bp = BasketProduct.objects.create(basket=basket, product=product, quantity=1)
        bp_id = bp.id
        basket.update_product_quantity(product, product.max)
        self.assertEqual(BasketProduct.objects.get(id=bp_id).quantity, product.max)
        basket.update_product_quantity(product, -1)
        self.assertEqual(len(BasketProduct.objects.filter(id=bp_id)), 0)

    def test_update_collection_quantity(self):
        basket, device = self.create_empty_basket()
        collection = Collection.objects.get(id=1)
        bc = BasketCollection.objects.create(basket=basket, collection=collection, quantity=1)
        bc_id = bc.id
        basket.update_collection_quantity(collection, 13)
        self.assertEqual(BasketCollection.objects.get(id=bc_id).quantity, 13)
        basket.update_collection_quantity(collection, -1)
        self.assertEqual(len(BasketCollection.objects.filter(id=bc_id)), 0)

    def test_get_and_remove_unavailable_items(self):
        basket, device = self.create_empty_basket()
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
        basket, device = self.create_empty_basket()
        product = Product.objects.get(id=1)
        quantity = product.max
        basket.add_product(product, quantity)
        self.assertIn(product, basket.products.all())
        bp = BasketProduct.objects.get(basket=basket, product=product)
        self.assertEqual(bp.quantity, quantity)

    def test_add_collection(self):
        basket, device = self.create_empty_basket()
        collection = Collection.objects.get(id=1)
        quantity = randint(1, 1000)
        basket.add_collection(collection, quantity)
        self.assertIn(collection, basket.collections.all())
        bc = BasketCollection.objects.get(basket=basket, collection=collection)
        self.assertEqual(bc.quantity, quantity)

class BasketProductTest(TestCase):
    fixtures = ['categories.json', 'products.json']

    def create_basket_product(self, product, quantity):
        device = Device.objects.create()
        basket = Basket.objects.create(device=device)
        bp = BasketProduct.objects.create(basket=basket, quantity=quantity, product=product)
        return bp

    def test_total_cost(self):
        product = Product.objects.get(id=1)
        quantity = randint(1, 1000)
        bp = self.create_basket_product(product, quantity)
        self.assertEqual(product.price * quantity, bp.total_cost)
    
    def test_update_quantity_less_than_min(self):
        product = Product.objects.get(id=1)
        bp = self.create_basket_product(product, randint(1, 1000))
        bp.update_quantity(product.min - randint(1, 1000))
        self.assertEqual(product.min, bp.quantity)
    
    def test_update_quantity_equal_min(self):
        product = Product.objects.get(id=1)
        bp = self.create_basket_product(product, randint(1, 1000))
        bp.update_quantity(product.min)
        self.assertEqual(product.min, bp.quantity)
    
    def test_update_quantity_valid(self):
        product = Product.objects.get(id=1)
        quantity = product.min + 1
        bp = self.create_basket_product(product, randint(1, 1000))
        bp.update_quantity(quantity)
        self.assertEqual(quantity, bp.quantity)
    
    def test_update_quantity_equal_max(self):
        product = Product.objects.get(id=1)
        bp = self.create_basket_product(product, randint(1, 1000))
        bp.update_quantity(product.max)
        self.assertEqual(product.max, bp.quantity)
    
    def test_update_quantity_greater_than_max(self):
        product = Product.objects.get(id=1)
        bp = self.create_basket_product(product, randint(1, 1000))
        bp.update_quantity(product.max + randint(1, 1000))
        self.assertEqual(product.max, bp.quantity)
    
    def test_add_quantity_negative(self):
        product = Product.objects.get(id=1)
        bp = self.create_basket_product(product, product.min)
        bp.add_quantity(-1)
        self.assertEqual(product.min, bp.quantity)
    
    def test_add_quantity_valid(self):
        product = Product.objects.get(id=1)
        bp = self.create_basket_product(product, product.min)
        bp.add_quantity(1)
        self.assertEqual(product.min + 1, bp.quantity)
    
    def test_add_quantity_greater_than_max(self):
        product = Product.objects.get(id=1)
        bp = self.create_basket_product(product, product.max)
        bp.add_quantity(1)
        self.assertEqual(product.max, bp.quantity)

class BasketCollectionTest(TestCase):
    fixtures = ['categories.json', 'products.json', 'collections.json']

    def create_basket_collection(self, collection, quantity):
        device = Device.objects.create()
        basket = Basket.objects.create(device=device)
        bc = BasketCollection.objects.create(basket=basket, collection=collection, quantity=quantity)
        return bc
    
    def test_total_cost(self):
        collection = Collection.objects.get(id=1)
        quantity = randint(1, 1000)
        bc = self.create_basket_collection(collection, quantity)
        self.assertEqual(collection.price * quantity, bc.total_cost)
    
    def test_add_quantity(self):
        collection = Collection.objects.get(id=1)
        quantity = randint(1, 1000)
        bc = self.create_basket_collection(collection, quantity)
        bc.add_quantity(3)
        self.assertEqual(quantity + 3, bc.quantity)

class CategoryTest(TestCase):
    fixtures = ['categories.json', 'products.json']

    def test_string(self):
        category = Category.objects.create(name='Test')
        self.assertEqual('Test', str(category))
    
    def test_delete(self):
        category = Category.objects.create(name='Test')
        for product in Product.objects.all()[:2]:
            product.category = category
            product.save()
        num_products = Product.objects.count()
        num_categories = Category.objects.count()
        category.delete()
        self.assertEqual(num_categories - 1, Category.objects.count())
        self.assertEqual(num_products - 2, Product.objects.count())
    
    def test_items(self):
        category = Category.objects.create(name='Test')
        products = []
        for product in Product.objects.all()[:2]:
            product.category = category
            product.save()
            products.append(product)
        items = category.items()
        for product in products:
            self.assertIn(product, items)
    
    def test_item_count(self):
        category = Category.objects.create(name='Test')
        self.assertEqual(0, category.item_count)
        for product in Product.objects.all()[:2]:
            product.category = category
            product.save()
        self.assertEqual(2, category.item_count)
    
    def test_add_products(self):
        category = Category.objects.create(name='Test')
        category.add_products(Product.objects.all()[:2])
        for product in Product.objects.all()[:2]:
            self.assertEqual(category, product.category)
        self.assertEqual(2, len(Product.objects.filter(category=category)))

class ProductTest(TestCase):
    fixtures = ['categories.json']
    test_products = []

    def tearDown(self):
        for prod in self.test_products: prod.image.delete()
        return super().tearDown()
    
    def create_product(self, name='Test', available=True, hidden=False, file_name='test'):
        category = Category.objects.get(id=1)
        prod = Product.objects.create(name=name, description='Test', price=10, category=category,
        image=SimpleUploadedFile(file_name + '.jpg', b'content'), available=available, hidden=hidden, min=1, max=12)
        self.test_products.append(prod)
        return prod

    def test_str(self):
        product = self.create_product('test')
        self.assertEqual('test', str(product))
    
    def test_hide(self):
        product = self.create_product()
        product.hide()
        self.assertTrue(product.hidden)
    
    def test_delete(self):
        product = self.create_product()
        img_path = product.image.path
        product.delete()
        self.assertFalse(path_exists(img_path))
    
    def test_set_available(self):
        product = self.create_product(available=False, hidden=True)
        product.set_available()
        self.assertTrue(product.available)
        self.assertFalse(product.hidden)
    
    def test_set_unavailable(self):
        product = self.create_product(available=True, hidden=False)
        product.set_unavailable()
        self.assertFalse(product.available)
    
    def test_hide_products(self):
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
        Product.make_products_available(products)
        for product in products:
            self.assertFalse(product.available)

class CollectionTest(TestCase):
    fixtures = ['collections.json', 'categories.json', 'products.json']

    def test_add_products(self):
        collection = Collection.objects.get(id=1)
        collection.add_products(Product.objects.all())
        for product in Product.objects.all():
            self.assertIn(product, collection.products.all())
    
    def test_get_visible(self):
        collections = Collection.get_visible()
        for collection in collections:
            self.assertFalse(collection.hidden)

class PromotionTest(TestCase):
    fixtures = ['promotions.json']

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
        promo = self.get_active_perc_promotion()
        promo.used = promo.max_uses
        eligible = promo.is_eligible(50)
        self.assertFalse(promo.active)
        self.assertFalse(eligible)
    
    def test_is_eligible_expired(self):
        promo = self.get_active_perc_promotion()
        promo.expiry = timezone.now() - timezone.timedelta(days=1)
        eligible = promo.is_eligible(50)
        self.assertFalse(promo.active)
        self.assertFalse(eligible)
    
    def test_is_eligible_inactive(self):
        promo = self.get_active_perc_promotion()
        promo.active = False
        self.assertFalse(promo.is_eligible(50))
    
    def test_is_eligible_active(self):
        promo = self.get_active_perc_promotion()
        self.assertTrue(promo.is_eligible(promo.min_spend))

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
        promo = self.get_active_perc_promotion()
        used = promo.used
        promo.set_used()
        self.assertEqual(used + 1, promo.used)
    
    def test_get_discount_fixed(self):
        promo = self.get_active_fixed_promotion()
        self.assertEqual(promo.get_discount(promo.min_spend + 5), promo.amount)    
    
    def test_get_discount_percentage_less_than_max(self):
        promo = self.get_active_perc_promotion()
        total = promo.min_spend + promo.max_discount - 1
        promo_amount = Decimal(promo.amount/100) * total
        self.assertEqual(promo.get_discount(total), round(promo_amount, 2))
    
    def test_get_discount_percentage_equal_to_max(self):
        promo = self.get_active_perc_promotion()
        total = promo.min_spend + promo.max_discount
        promo_amount = Decimal(promo.amount/100) * total
        self.assertEqual(promo.get_discount(total), round(promo_amount, 2))
    
    def test_get_discount_percentage_greater_than_max(self):
        promo = self.get_active_perc_promotion()
        total = promo.min_spend + promo.max_discount + 1
        promo_amount = Decimal(promo.max_discount/100) * total
        self.assertEqual(promo.get_discount(total), round(promo_amount, 2))

class DeliveryTest(TestCase):

    def create_delivery(self, name='Test'):
        delivery = Delivery.objects.create(name=name, price=10)
        return delivery
    
    def test_to_string(self):
        delivery = self.create_delivery()
        self.assertEqual('Test', str(delivery))

class OrderTest(TestCase):
    fixtures = ['categories.json', 'products.json', 'collections.json', 'promotions.json']

    def create_empty_basket(self):
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
        basket, device = self.create_empty_basket()
        prices = self.add_collections(basket) + self.add_products(basket)
        basket.address = self.create_address()
        basket.delivery = self.create_delivery()
        basket.promotion = self.get_promotion()
        return basket, prices
    
    def test_create_order(self):
        basket, prices = self.create_full_basket()
        num_orders = Order.objects.count()
        Order.create_order_and_empty_basket(basket)
        self.assertEqual(num_orders + 1, Order.objects.count())

    def test_create_promotion(self):
        basket, prices = self.create_full_basket()
        discount = basket.promotion_amount
        order = Order.create_order_and_empty_basket(basket)
        self.assertEqual(basket.promotion.code, order.promotion_code)
        self.assertEqual(discount, order.discount_amount)
    
    def test_create_order_shipping(self):
        basket, prices = self.create_full_basket()
        order = Order.create_order_and_empty_basket(basket)
        self.assertEqual(basket.address.name, order.ordershipping.address_name)
        self.assertEqual(basket.address.line_1, order.ordershipping.line_1)
        self.assertEqual(basket.address.line_2, order.ordershipping.line_2)
        self.assertEqual(basket.address.city, order.ordershipping.city)
        self.assertEqual(basket.address.county, order.ordershipping.county)
        self.assertEqual(basket.address.postcode, order.ordershipping.postcode)
    
    def test_create_order_products(self):
        basket, prices = self.create_full_basket()
        order = Order.create_order_and_empty_basket(basket)
        for bp in basket.basketproduct_set.all():
            op = OrderProduct.objects.filter(order=order, product_name=bp.product.name, quantity=bp.quantity, price=bp.product.price).count()
            self.assertEqual(1, op)
    
    def test_create_order_collections(self):
        basket, prices = self.create_full_basket()
        order = Order.create_order_and_empty_basket(basket)
        for bc in basket.basketcollection_set.all():
            oc = OrderCollection.objects.filter(order=order, collection_name=bc.collection.name, quantity=bc.quantity, price=bc.collection.price).count()
            self.assertEqual(1, oc)
            for product in bc.collection.products.all():
                ocp = OrderCollectionProduct.objects.filter(order_collection=oc, product_name=product.name).count()
                self.assertEqual(1, ocp)
    
    def test_delete_address(self):
        basket, prices = self.create_full_basket()
        num_addresses = Address.objects.count()
        Order.create_order_and_empty_basket(basket)
        self.assertIsNone(basket.address.id)
        self.assertEqual(num_addresses - 1, Address.objects.count())
    
    def test_delete_basket(self):
        basket, prices = self.create_full_basket()
        num_baskets = Basket.objects.count()
        Order.create_order_and_empty_basket(basket)
        self.assertEqual(num_baskets - 1, Basket.objects.count())
    
    def test_num_orders_today(self):
        num_orders = randint(1, 20)
        for i in range(num_orders):
            basket, prices = self.create_full_basket()
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
    
    def test_sales_today(self):
        num_orders = randint(1, 20)
        total = 0
        for i in range(num_orders):
            basket, prices = self.create_full_basket()
            total += sum(prices) - basket.promotion_amount
            Order.create_order_and_empty_basket(basket)
        self.assertEqual(total, Order.sales_today())

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