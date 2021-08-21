from storefront.models import Device
from django.test import TestCase
import uuid

# Create your tests here.
class DeviceTest(TestCase):

    def test_new_device_id(self):
        num_devices = len(Device.objects.all())
        code = Device.get_new_device_id()
        self.assertTrue(isinstance(code, uuid.UUID))
        self.assertEqual(num_devices + 1, len(Device.objects.all()))
