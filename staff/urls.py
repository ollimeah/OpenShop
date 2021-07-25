from django.urls import path
from staff import views

urlpatterns = [
    path('', views.dashboard, name='staff-dashboard'),

    path('products/', views.ProductListView.as_view(), name='staff-products'),
    path('products/new/', views.ProductCreateView.as_view(), name='staff-products-new'),
    path('product/<str:name>/', views.ProductDetailView.as_view(), name='staff-product'),
    path('product/<str:name>/update/', views.ProductUpdateView.as_view(), name='staff-product-update'),
    path('product/<str:name>/delete/', views.ProductDeleteView.as_view(), name='staff-product-delete'),
    path('products/manage/', views.manage_products, name='staff-manage-products'),

    path('categories/', views.CategoryListView.as_view(), name='staff-categories'),
    path('categories/new/', views.CategoryCreateView.as_view(), name='staff-categories-new'),
    path('category/<str:name>/', views.CategoryDetailView.as_view(), name='staff-category'),
    path('category/<str:name>/update/', views.CategoryUpdateView.as_view(), name='staff-category-update'),
    path('category/<str:name>/delete/', views.CategoryDeleteView.as_view(), name='staff-category-delete'),
    path('category/<str:name>/products/', views.category_add_products, name='staff-category-products'),

    path('settings/', views.settings, name='staff-settings'),
]