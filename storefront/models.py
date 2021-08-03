from staff.models import Collection, Product
from django.db import models
import uuid

class Device(models.Model):
    device = models.UUIDField(default=uuid.uuid4)

class Basket(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    date_updated = models.DateTimeField(auto_now=True)
    products = models.ManyToManyField(Product)
    collections = models.ManyToManyField(Collection)
