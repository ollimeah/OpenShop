from django.urls import path
from staff import views

urlpatterns = [
    path('', views.dashboard, name='staff-dashboard'),
    path('products/', views.ProductListView.as_view(), name='staff-products'),
    path('settings/', views.settings, name='staff-settings'),
]