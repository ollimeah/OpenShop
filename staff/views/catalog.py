from staff.forms import CategoryProductForm, CollectionProductForm, ProductManagementForm
from staff.models import Category, Collection, Product
from django.views import generic
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render

class CategoryListView(generic.ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'categories/index.html'

class CategoryDetailView(generic.DetailView):
    model = Category
    template_name = 'categories/detail.html'
    slug_field = 'name'
    slug_url_kwarg = 'name'

class CategoryCreateView(generic.edit.CreateView):
    model = Category
    fields = '__all__'
    template_name = 'categories/new.html'

    def get_success_url(self):
        return reverse('staff-category', kwargs={'name' : self.object.name})

class CategoryUpdateView(generic.UpdateView):
    model = Category
    slug_field = 'name'
    slug_url_kwarg = 'name'
    fields = '__all__'
    template_name = 'categories/update.html'

    def get_success_url(self):
        return reverse('staff-category', kwargs={'name' : self.object.name})

class CategoryDeleteView(generic.DeleteView):
    model = Category
    slug_field = 'name'
    slug_url_kwarg = 'name'
    template_name = 'categories/delete.html'

    def get_success_url(self):
        return reverse('staff-categories')

def category_add_products(request, name):
    category = get_object_or_404(Category, name=name)
    products = {'products' : category.items().values_list(flat=True)}

    if request.method == 'POST':
        form = CategoryProductForm(request.POST, initial = products)
        if form.is_valid():
            category.add_products(form.cleaned_data['products'])
            for product in category.items():
                if not product in form.cleaned_data['products']:
                    product.hidden = True
                    product.available = False
                    product.save()
            return redirect('staff-category', name = category.name)
    
    context={'category' : category, 'form' : CategoryProductForm(initial = products)}
    return render(request, 'categories/products.html', context)

class ProductListView(generic.ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'products/index.html'

class ProductDetailView(generic.DetailView):
    model = Product
    template_name = 'products/detail.html'
    slug_field = 'name'
    slug_url_kwarg = 'name'

class ProductCreateView(generic.edit.CreateView):
    model = Product
    fields = '__all__'
    template_name = 'products/new.html'

    def get_success_url(self):
        return reverse('staff-product', kwargs={'name' : self.object.name})

class ProductUpdateView(generic.UpdateView):
    model = Product
    slug_field = 'name'
    slug_url_kwarg = 'name'
    fields = '__all__'
    template_name = 'products/update.html'

    def get_success_url(self):
        return reverse('staff-product', kwargs={'name' : self.object.name})

class ProductDeleteView(generic.DeleteView):
    model = Product
    slug_field = 'name'
    slug_url_kwarg = 'name'
    template_name = 'products/delete.html'

    def get_success_url(self):
        return reverse('staff-products')

def manage_products(request):
    if request.POST:
        form = ProductManagementForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            products = form.cleaned_data['products']
            if action == 'hide':
                Product.hide_products(products)
            elif action == 'delete':
                Product.delete_products(products)
            elif action == 'available':
                Product.make_products_available(products)
            elif action == 'unavailable':
                Product.make_products_unavailable(products)
        return redirect('staff-products')
    return render(request, 'products/manage.html', {'form' : ProductManagementForm()})

class CollectionListView(generic.ListView):
    model = Collection
    context_object_name = 'collections'
    template_name = 'collections/index.html'

class CollectionDetailView(generic.DetailView):
    model = Collection
    template_name = 'collections/detail.html'
    slug_field = 'name'
    slug_url_kwarg = 'name'

class CollectionCreateView(generic.edit.CreateView):
    model = Collection
    fields = '__all__'
    template_name = 'collections/new.html'

    def get_success_url(self):
        return reverse('staff-collection', kwargs={'name' : self.object.name})

class CollectionUpdateView(generic.UpdateView):
    model = Collection
    slug_field = 'name'
    slug_url_kwarg = 'name'
    fields = '__all__'
    template_name = 'collections/update.html'

    def get_success_url(self):
        return reverse('staff-collection', kwargs={'name' : self.object.name})

class CollectionDeleteView(generic.DeleteView):
    model = Collection
    slug_field = 'name'
    slug_url_kwarg = 'name'
    template_name = 'collections/delete.html'

    def get_success_url(self):
        return reverse('staff-collections')

def collection_add_products(request, name):
    collection = get_object_or_404(Collection, name=name)
    products = {'products' : collection.products.all()}

    if request.method == 'POST':
        form = CollectionProductForm(request.POST, initial = products)
        if form.is_valid():
            collection.add_products(form.cleaned_data['products'])
            for product in collection.products.all():
                if not product in form.cleaned_data['products']:
                    collection.products.remove(product)
            return redirect('staff-collection', name = collection.name)
    
    context={'collection' : collection, 'form' : CollectionProductForm(initial = products)}
    return render(request, 'collections/products.html', context)