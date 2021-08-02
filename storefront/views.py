from django.shortcuts import render
from staff.models import Product
from django.views import generic

def home(request):
    return render(request, 'storefront/home.html', {})

# def shop(request):
#     available = Product.get_available()
#     unavailable = Product.get_unavailable()
#     context = {'available' : available, 'unavailable' : unavailable}
#     return render(request, 'storefront/shop.html', context)

class ProductListView(generic.ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'storefront/shop.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available'] = Product.get_available()
        context['unavailable'] = Product.get_unavailable()
        return context

class ProductDetailView(generic.DetailView):
    model = Product
    template_name = 'storefront/product.html'
    slug_field = 'name'
    slug_url_kwarg = 'name'
    queryset = Product.objects.filter(hidden=False)