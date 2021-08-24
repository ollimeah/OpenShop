from django.utils import timezone
from storefront.models import Basket, BasketCollection, BasketProduct, Device
from staff.models import Collection, Delivery, Product, Promotion
from django.test import TestCase
import uuid
from random import randint
from decimal import Decimal
from math import ceil

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
        quantity = randint(1, 1000)
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