from django.urls import path
from storefront.views import *

urlpatterns = [
    path('', home, name='home'),
    path('shop/', ProductListView.as_view(), name='shop'),
    path('shop/<str:name>/', ProductDetailView.as_view(), name='product')
]