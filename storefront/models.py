from staff.models import Collection, Delivery, Product, Promotion, Address
from django.db import models
import uuid

class Device(models.Model):
    code = models.UUIDField(primary_key=True, default=uuid.uuid4(), max_length=40)

    @classmethod
    def get_new_device_id(device):
        device = Device.objects.create()
        return device.code

class Basket(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    date_updated = models.DateTimeField(auto_now=True)
    products = models.ManyToManyField(Product, through='BasketProduct')
    collections = models.ManyToManyField(Collection, through='BasketCollection')
    promotion = models.ForeignKey(Promotion, on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    delivery = models.ForeignKey(Delivery, on_delete=models.SET_NULL, null=True)

    @property
    def item_cost(self):
        total = 0
        for bp in self.basketproduct_set.all():
            total += bp.total_cost
        for bc in self.basketcollection_set.all():
            total += bc.total_cost
        return total
    
    @property
    def total_cost(self):
        return self.item_cost # + delivery
    
    @property
    def promotion_amount(self):
        return self.promotion.get_discount(self.item_cost)
    
    @property
    def promotion_cost(self):
        return self.item_cost - self.promotion.get_discount(self.item_cost)
    
    def add_promotion(self, promotion):
        if promotion.is_eligible(self.item_cost):
            self.promotion = promotion
            self.save()
            promotion.set_used()
            return True
        return False
    
    def update_product_quantity(self, product, quantity):
        bp = BasketProduct.objects.get(basket=self, product=product)
        if quantity <= 0:
            bp.delete()
        else:
            bp.update_quantity(quantity)
    
    def update_collection_quantity(self, collection, quantity):
        bc = BasketCollection.objects.get(basket=self, collection=collection)
        if quantity <= 0:
            bc.delete()
        else:
            # bc.update_quantity(quantity)
            bc.quantity = quantity
            bc.save()

    def is_empty(self):
        return not (self.products.all() or self.collections.all())

    def get_and_remove_unavailable_items(self):
        unavailable = []
        for product in self.products.filter(available=False):
            unavailable.append(product)
            self.products.remove(product)
        for collection in self.collections.filter(available=False):
            unavailable.append(collection)
            self.collections.remove(collection)
        return unavailable

    @classmethod
    def get_basket(basket, device_code):
        device = Device.objects.get(code=device_code)
        basket, created = Basket.objects.get_or_create(device=device)
        return basket

    @classmethod
    def add_product_to_basket(basket, device_code, product, quantity):
        basket = Basket.get_basket(device_code)
        bp, created = BasketProduct.objects.get_or_create(basket=basket, product=product)
        bp.add_quantity(quantity)
    
    @classmethod
    def add_collection_to_basket(basket, device_code, collection, quantity):
        basket = Basket.get_basket(device_code)
        bc, created = BasketCollection.objects.get_or_create(basket=basket, collection=collection)
        bc.add_quantity(quantity)

class BasketProduct(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    @property
    def total_cost(self):
        return self.product.price * self.quantity
    
    def update_quantity(self, quantity):
        if quantity < self.product.min:
            self.quantity = self.product.min
        elif quantity > self.product.max:
            self.quantity = self.product.max
        else:
            self.quantity = quantity
        self.save()

    def add_quantity(self, quantity):
        self.quantity = self.quantity + quantity
        self.save()

class BasketCollection(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    @property
    def total_cost(self):
        return self.collection.price * self.quantity
    
    # def update_quantity(self, quantity):
    #     if quantity < self.product.min:
    #         self.quantity = self.product.min
    #     elif quantity > self.product.max:
    #         self.quantity = self.product.max
    #     else:
    #         self.quantity = quantity
    #     self.save()

    def add_quantity(self, quantity):
        self.quantity = self.quantity + quantity
        self.save()