from staff.models import Category, Collection
from storefront.models import Device

def categories(request):
    return {'categories': Category.get_visible()}

def collections(request):
    return {'collections': Collection.get_visible()}

def device_id(request):
    context = {}
    if 'device' in request.COOKIES:
        context['needs_id'] = False
    else:
        context['needs_id'] = True
        context['device_id'] = Device.get_new_device_id()
    return context

    