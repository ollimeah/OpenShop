from django.urls import path
from staff import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='staff/login.html'), name='staff-login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='staff/login.html', extra_context={'logout':True}), name='staff-logout'),
    path('dashboard/', views.dashboard, name='staff-dashboard'),

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

    path('faqs/', views.FAQListView.as_view(), name='staff-faqs'),
    path('faqs/new/', views.FAQCreateView.as_view(), name='staff-faqs-new'),
    path('faq/<int:pk>/update/', views.FAQUpdateView.as_view(), name='staff-faq-update'),
    path('faq/<int:pk>/delete/', views.FAQDeleteView.as_view(), name='staff-faq-delete'),

    path('promotions/', views.PromotionListView.as_view(), name='staff-promotions'),
    path('promotions/percentage/new/', views.PercentagePromotionCreateView.as_view(), name='staff-promotions-percentage-new'),
    path('promotions/fixed/new/', views.FixedPromotionCreateView.as_view(), name='staff-promotions-fixed-new'),
    path('promotion/<str:code>/', views.PromotionDetailView.as_view(), name='staff-promotion'),
    path('promotion/<str:code>/update/', views.PromotionUpdateView.as_view(), name='staff-promotion-update'),
    path('promotion/<str:code>/delete/', views.PromotionDeleteView.as_view(), name='staff-promotion-delete'),
    path('promotions/disable-all/', views.disable_promotions, name='staff-disable-promotions'),

    path('deliveries/', views.DeliveryListView.as_view(), name='staff-deliveries'),
    path('deliveries/new/', views.DeliveryCreateView.as_view(), name='staff-deliveries-new'),
    path('delivery/<int:pk>/update/', views.DeliveryUpdateView.as_view(), name='staff-delivery-update'),
    path('delivery/<int:pk>/delete/', views.DeliveryDeleteView.as_view(), name='staff-delivery-delete'),

    path('home/', views.home, name='staff-home'),

    path('carousel-images/', views.CarouselImageListView.as_view(), name='staff-carousel-index'),
    path('carousel/new/', views.CarouselImageCreateView.as_view(), name='staff-carousel-new'),
    path('carousel/<int:pk>/', views.CarouselImageDetailView.as_view(), name='staff-carousel'),
    path('carousel/<int:pk>/update/', views.CarouselImageUpdateView.as_view(), name='staff-carousel-update'),
    path('carousel/<int:pk>/delete/', views.CarouselImageDeleteView.as_view(), name='staff-carousel-delete'),

    path('order/', views.OrderListView.as_view(), name='staff-orders'),

    path('settings/', views.settings, name='staff-settings'),
]