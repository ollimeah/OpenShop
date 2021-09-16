from typing import Set
from staff.models import Settings
from django.shortcuts import reverse, redirect

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.META.get('PATH_INFO', "")
        settings = Settings.load()
        if settings.maintenance and path!=reverse("maintenance") and not (path.startswith(reverse('admin:index')) or path.startswith(reverse('staff-login'))):
            response = redirect(reverse("maintenance"))
            return response
        response = self.get_response(request)
        return response