from django.urls import path
from staff import views

urlpatterns = [
    path('', views.dashboard, name='staff-dashboard'),
    path('products/', views.products, name='staff-products'),
    path('settings/', views.settings, name='staff-settings'),
]