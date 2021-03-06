from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from staff.models import FAQ, Address, CarouselImage, Category, Collection, Delivery, Message, Order, Product, Basket, Promotion
from django.views import generic
from staff.forms import DeliveryChoiceForm, ShippingForm
from storefront.forms import PromotionCodeForm
from django.conf import settings

def home(request):
    return render(request, 'storefront/home.html', {"carousel" : CarouselImage.objects.all()})

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

class Contact(generic.CreateView):
    model = Message
    template_name = 'storefront/contact/contact.html'
    fields = ['name', 'email', 'subject', 'message']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faqs'] = FAQ.objects.all()
        return context

    def get_success_url(self):
        return reverse('message-sent')

def shipping(request):
    basket = Basket.get_basket(request.COOKIES['device'])
    if basket.is_empty(): return redirect('basket')
    if request.method == 'POST':
        address_form = ShippingForm(request.POST)
        if address_form.is_valid():
            address = Address(**address_form.cleaned_data)
            address.save()
            basket.address = address
        delivery_form = DeliveryChoiceForm(request.POST)
        if delivery_form.is_valid():
            basket.delivery = delivery_form.cleaned_data['delivery']
        basket.save()
        if address_form.is_valid() and delivery_form.is_valid(): return redirect('checkout')
    elif basket.address:
        address_form = ShippingForm(instance=basket.address)
    else:
        address_form = ShippingForm()
    if basket.delivery:
        delivery_form = DeliveryChoiceForm({'delivery' : basket.delivery})
    else:
        delivery_form = DeliveryChoiceForm()
    deliveries = {}
    for delivery in Delivery.objects.filter(available=True):
        deliveries.update({delivery.name:delivery.price})
    context = {'form' : address_form, 'delivery_form' : delivery_form, 'deliveries' : deliveries}
    return render(request, 'storefront/order/shipping.html', context)

def checkout(request):
    basket = Basket.get_basket(request.COOKIES['device'])
    if basket.is_empty() or not basket.contains_available(): return redirect('basket')
    if not basket.address or not basket.delivery: return redirect('shipping')
    context = {}
    if request.method == 'POST':
        promo_form = PromotionCodeForm(request.POST)
        if promo_form.is_valid():
            code = promo_form.cleaned_data['code']
            try:
                promotion = Promotion.objects.get(code=code)
                if promotion:
                    context['error'] = not basket.add_promotion(promotion)
            except Exception as e:
                # print(e)
                context['error'] = True
    if basket.promotion:
        promo_form = PromotionCodeForm({'code' : basket.promotion.code})
    else:
        promo_form = PromotionCodeForm()
    unavailable = basket.get_and_remove_unavailable_items()
    context.update({'unavailable' : unavailable, 'basket' : basket, 'promo_form' : promo_form, 'debug' : settings.DEBUG})
    return render(request, 'storefront/order/checkout.html', context)

def place_order(request):
    if not settings.DEBUG: return redirect('basket')
    if request.method == 'POST':
        basket = Basket.get_basket(request.COOKIES['device'])
        if basket.is_empty() or not basket.contains_available(): return redirect('basket')
        if not basket.address or not basket.delivery: return redirect('shipping')
        Order.create_order_and_empty_basket(basket)
        return redirect('order-success')
    else:
        return HttpResponse(status=405)