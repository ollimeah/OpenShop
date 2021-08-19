from django.shortcuts import get_object_or_404, redirect, render
from staff.models import Address, Category, Collection, Product
from storefront.models import Basket
from django.views import generic
from staff.forms import DeliveryChoiceForm, ShippingForm

def home(request):
    return render(request, 'storefront/home.html', {})

class ProductListView(generic.ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'storefront/shop.html'

    def get_queryset(self):
        if 'category' in self.kwargs:
            category = get_object_or_404(Category, name=self.kwargs['category'])
            return Product.objects.filter(hidden=False, category=category)
        else:
            return Product.objects.filter(hidden=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self.get_queryset()
        context['available'] = products.filter(available=True)
        context['unavailable'] = products.filter(available=False)
        if 'category' in self.kwargs:
            context['title'] = self.kwargs['category']
        else:
            context['title'] = "All Products"
        return context

class ProductDetailView(generic.DetailView):
    model = Product
    template_name = 'storefront/product.html'
    slug_field = 'name'
    slug_url_kwarg = 'name'
    queryset = Product.objects.filter(hidden=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['range'] = range(self.object.min, self.object.max + 1)
        return context

class CollectionDetailView(generic.DetailView):
    model = Collection
    template_name = 'storefront/collection.html'
    slug_field = 'name'
    slug_url_kwarg = 'name'
    queryset = Collection.objects.filter(hidden=False)

def shipping(request):
    basket = Basket.get_basket(request.COOKIES['device'])
    if basket.is_empty(): return redirect('basket')
    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            address = Address(**form.cleaned_data)
            address.save()
            basket.address = address
        delivery_form = DeliveryChoiceForm(request.POST)
        if delivery_form.is_valid():
            basket.delivery = delivery_form.cleaned_data['delivery']
        basket.save()
    elif basket.address:
        form = ShippingForm(instance=basket.address)
    else:
        form = ShippingForm()
    if basket.delivery:
        delivery_form = DeliveryChoiceForm({'delivery' : basket.delivery})
    else:
        delivery_form = DeliveryChoiceForm()
    context = {'form' : form, 'delivery_form' : delivery_form}
    return render(request, 'storefront/shipping.html', context)