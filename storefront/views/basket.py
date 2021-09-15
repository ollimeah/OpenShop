from django.http import HttpResponse, JsonResponse
from storefront.forms import AddProductToBasketForm, AddCollectionToBasketForm
from staff.models import Product, Collection, Basket, BasketProduct, BasketCollection
from django.shortcuts import get_object_or_404, redirect, render
import json

def add_product_to_basket(request):
    if request.method == 'POST':
        form = AddProductToBasketForm(request.POST)
        if form.is_valid():
            product = get_object_or_404(Product, name=form.cleaned_data['product_name'])
            basket = Basket.get_basket(request.COOKIES['device'])
            basket.add_product(product, form.cleaned_data['quantity'])
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=406)
    else:
        return HttpResponse(status=405)

def add_collection_to_basket(request):
    if request.method == 'POST':
        form = AddCollectionToBasketForm(request.POST)
        if form.is_valid():
            collection = get_object_or_404(Collection, name = form.cleaned_data['collection_name'])
            basket = Basket.get_basket(request.COOKIES['device'])
            basket.add_collection(collection, form.cleaned_data['quantity'])
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=406)
    else:
        return HttpResponse(status=405)

def basket(request):
    try:
        basket = Basket.get_basket(request.COOKIES['device'])
        unavailable = basket.get_and_remove_unavailable_items()
        context = {'unavailable' : unavailable, 'basket' : basket}
    except:
        context = {'basket' : None}
    return render(request, 'storefront/order/basket.html', context)

def update_product_quantity(request):
    if request.method == 'POST':
        if request.POST:
            form = AddProductToBasketForm(request.POST)
        else:
            form = AddProductToBasketForm(json.loads(request.body))
        if form.is_valid():
            product = get_object_or_404(Product, name=form.cleaned_data['product_name'])
            basket = Basket.get_basket(request.COOKIES['device'])
            basket.update_product_quantity(product, form.cleaned_data['quantity'])
            if form.cleaned_data['quantity'] <= 0:
                return redirect('basket')
            else:
                bp = BasketProduct.objects.get(basket=basket, product=product)
                return JsonResponse({'productTotal':bp.total_cost, 'cost':basket.item_cost, 'numItems':basket.num_items})
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
            collection = get_object_or_404(Collection, name = form.cleaned_data['collection_name'])
            basket = Basket.get_basket(request.COOKIES['device'])
            basket.update_collection_quantity(collection, form.cleaned_data['quantity'])
            if form.cleaned_data['quantity'] <= 0:
                return redirect('basket')
            else:
                bc = BasketCollection.objects.get(basket=basket, collection=collection)
                return JsonResponse({'productTotal':bc.total_cost, 'cost':basket.item_cost, 'numItems':basket.num_items})
        else:
            return HttpResponse(status=406)
    else:
        return HttpResponse(status=405)