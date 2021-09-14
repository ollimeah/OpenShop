from django.urls import path
from storefront.views import *
from django.views.generic import TemplateView

urlpatterns = [
    path('', home, name='home'),
    path('shop/', ProductListView.as_view(), name='shop'),
    path('shop/<category>/', ProductListView.as_view(), name='shop-category'),
    path('shop/product/<str:name>/', ProductDetailView.as_view(), name='product'),
    path('collections/<str:name>/', CollectionDetailView.as_view(), name='collection'),
    path('contact/', Contact.as_view(), name='contact'),
    path('contact/sent/', TemplateView.as_view(template_name='storefront/contact/sent.html'), name='message-sent'),
    path('basket/add-product/', add_product_to_basket, name='basket-add-product'),
    path('basket/add-collection/', add_collection_to_basket, name='basket-add-collection'),
    path('basket/update-product/', update_product_quantity, name='basket-update-product'),
    path('basket/update-collection/', update_collection_quantity, name='basket-update-collection'),
    path('basket/', basket, name='basket'),
    path('shipping/', shipping, name='shipping'),
    path('checkout/', checkout, name='checkout'),
    path('success/', TemplateView.as_view(template_name='storefront/order/success.html'), name='order-success'),
]