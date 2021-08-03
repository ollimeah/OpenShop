from staff.models import Collection, Product
from django.db import models
import uuid

class Device(models.Model):
    device_id = models.UUIDField(default=uuid.uuid4)

    @classmethod
    def get_new_device_id(device):
        device = Device.objects.create()
        return device.device_id

class Basket(models.Model):
    device_id = models.ForeignKey(Device, on_delete=models.CASCADE)
    date_updated = models.DateTimeField(auto_now=True)
    products = models.ManyToManyField(Product)
    collections = models.ManyToManyField(Collection)
