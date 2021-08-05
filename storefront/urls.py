from django.urls import path
from storefront.views import *

urlpatterns = [
    path('', home, name='home'),
    path('shop/', ProductListView.as_view(), name='shop'),
    path('shop/<category>/', ProductListView.as_view(), name='shop-category'),
    path('shop/product/<str:name>/', ProductDetailView.as_view(), name='product'),
    path('collections/<str:name>/', CollectionDetailView.as_view(), name='collection'),
    path('basket/add-product/', add_product_to_basket, name='basket-add-product'),
    path('basket/add-collection/', add_collection_to_basket, name='basket-add-collection'),
]