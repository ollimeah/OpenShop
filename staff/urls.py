from django.urls import path
from staff import views

urlpatterns = [
    path('', views.dashboard, name='staff-dashboard'),

    path('products/', views.ProductListView.as_view(), name='staff-products'),
    path('products/new/', views.ProductCreateView.as_view(), name='staff-products-new'),
    path('product/<str:name>/', views.ProductDetailView.as_view(), name='staff-product'),
    path('product/<str:name>/update/', views.ProductUpdateView.as_view(), name='staff-product-update'),
    path('product/<str:name>/delete/', views.ProductDeleteView.as_view(), name='staff-product-delete'),
    path('products/manage/', views.manage_products, name='staff-products-manage'),

    path('categories/', views.CategoryListView.as_view(), name='staff-categories'),
    path('categories/new/', views.CategoryCreateView.as_view(), name='staff-categories-new'),
    path('category/<str:name>/', views.CategoryDetailView.as_view(), name='staff-category'),
    path('category/<str:name>/update/', views.CategoryUpdateView.as_view(), name='staff-category-update'),
    path('category/<str:name>/delete/', views.CategoryDeleteView.as_view(), name='staff-category-delete'),
    path('category/<str:name>/products/', views.category_add_products, name='staff-category-products'),

    path('collections/', views.CollectionListView.as_view(), name='staff-collections'),
    path('collections/new/', views.CollectionCreateView.as_view(), name='staff-collections-new'),
    path('collection/<str:name>/', views.CollectionDetailView.as_view(), name='staff-collection'),
    path('collection/<str:name>/update/', views.CollectionUpdateView.as_view(), name='staff-collection-update'),
    path('collection/<str:name>/delete/', views.CollectionDeleteView.as_view(), name='staff-collection-delete'),
    path('collection/<str:name>/products/', views.collection_add_products, name='staff-collection-products'),

    path('settings/', views.settings, name='staff-settings'),
]