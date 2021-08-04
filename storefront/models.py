from staff.models import Collection, Product
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
    collections = models.ManyToManyField(Collection)

    @classmethod
    def add_product_to_basket(basket, device_code, product, quantity):
        device = Device.objects.get(code=device_code)
        basket, created = Basket.objects.get_or_create(device=device)
        bp, created = BasketProduct.objects.get_or_create(basket=basket, product=product)
        bp.add_quantity(quantity)
        print(basket.products.all())
        print(bp.quantity)

class BasketProduct(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def add_quantity(self, quantity):
        self.quantity = self.quantity + quantity
        self.save()