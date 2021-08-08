from django.http import HttpResponse, JsonResponse
from storefront.forms import AddProductToBasketForm, AddCollectionToBasketForm
from storefront.models import Basket, BasketProduct, BasketCollection
from staff.models import Product, Collection
from django.shortcuts import redirect, render
import json

def add_product_to_basket(request):
    if request.method == 'POST':
        form = AddProductToBasketForm(request.POST)
        if form.is_valid():
            product = Product.objects.get(name = form.cleaned_data['product_name'])
            Basket.add_product_to_basket(request.COOKIES['device'], product, form.cleaned_data['quantity'])
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=406)
    else:
        return HttpResponse(status=405)

def add_collection_to_basket(request):
    if request.method == 'POST':
        form = AddCollectionToBasketForm(request.POST)
        if form.is_valid():
            collection = Collection.objects.get(name = form.cleaned_data['collection_name'])
            Basket.add_collection_to_basket(request.COOKIES['device'], collection, form.cleaned_data['quantity'])
            print(collection)
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=406)
    else:
        return HttpResponse(status=405)

def basket(request):
    basket = Basket.get_basket(request.COOKIES['device'])
    unavailable = basket.get_and_remove_unavailable_items()
    context = {'unavailable' : unavailable, 'basket' : basket}
    return render(request, 'storefront/basket.html', context)

def update_product_quantity(request):
    if request.method == 'POST':
        if request.POST:
            form = AddProductToBasketForm(request.POST)
        else:
            form = AddProductToBasketForm(json.loads(request.body))
        if form.is_valid():
            product = Product.objects.get(name = form.cleaned_data['product_name'])
            basket = Basket.get_basket(request.COOKIES['device'])
            basket.update_product_quantity(product, form.cleaned_data['quantity'])
            if form.cleaned_data['quantity'] <= 0:
                return redirect('basket')
            else:
                bp = BasketProduct.objects.get(basket=basket, product=product)
                return JsonResponse({'productTotal':bp.total_cost, 'cost':basket.item_cost, 'total':basket.total_cost})
        else:
            return HttpResponse(status=406)
    else:
        return HttpResponse(status=405)

def update_collection_quantity(request):
    if request.method == 'POST':
        if request.POST:
            form = AddCollectionToBasketForm(request.POST)
        else:
            form = AddCollectionToBasketForm(json.loads(request.body))
        if form.is_valid():
            collection = Collection.objects.get(name = form.cleaned_data['collection_name'])
            basket = Basket.get_basket(request.COOKIES['device'])
            basket.update_collection_quantity(collection, form.cleaned_data['quantity'])
            if form.cleaned_data['quantity'] <= 0:
                return redirect('basket')
            else:
                bc = BasketCollection.objects.get(basket=basket, collection=collection)
                return JsonResponse({'productTotal':bc.total_cost, 'cost':basket.item_cost, 'total':basket.total_cost})
        else:
            return HttpResponse(status=406)
    else:
        return HttpResponse(status=405)