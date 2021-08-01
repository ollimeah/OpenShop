from django.urls import path
from storefront import views

urlpatterns = [
    path('', views.home, name='home'),
]