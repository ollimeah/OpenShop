from staff.forms import CategoryProductForm, CollectionProductForm, ProductImageForm, ProductManagementForm
from staff.models import Category, Collection, Product, ProductImage
from django.views import generic
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from .views import StaffTestMixin, staff_check
from django.contrib.auth.decorators import user_passes_test

class CategoryView(StaffTestMixin):
    model = Category
    slug_field = 'name'
    slug_url_kwarg = 'name'
    fields = '__all__'
    template_name = 'categories/view.html'

    def get_success_url(self):
        return reverse('staff-category', kwargs={'name' : self.object.name})

class CategoryListView(StaffTestMixin, generic.ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'categories/index.html'

class CategoryDetailView(CategoryView, generic.DetailView):
    template_name = 'categories/detail.html'

class CategoryCreateView(CategoryView, generic.edit.CreateView): pass

class CategoryUpdateView(CategoryView, generic.UpdateView): pass

class CategoryDeleteView(CategoryView, generic.DeleteView):
    def get(self, request, name):
        return redirect('staff-categories')

    def get_success_url(self):
        return reverse('staff-categories')

@user_passes_test(staff_check, login_url='staff-login')
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

class ProductListView(StaffTestMixin, generic.ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'products/index.html'

class ProductView(StaffTestMixin):
    model = Product
    slug_field = 'name'
    slug_url_kwarg = 'name'
    fields = '__all__'
    template_name = 'products/view.html'

    def get_success_url(self):
        return reverse('staff-product', kwargs={'name' : self.object.name})

class ProductDetailView(ProductView, generic.DetailView):
    template_name = 'products/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_form'] = ProductImageForm(initial={'product':self.object})
        return context
    
    def post(self, request, *args, **kwargs):
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            product = get_object_or_404(Product, id=form.cleaned_data['product'].id)
            ProductImage.objects.create(product=product, image=form.cleaned_data['image'])
        return redirect('staff-product', name=product.name)

@user_passes_test(staff_check, login_url='staff-login')
def delete_product_image(request, id):
    prod_img = get_object_or_404(ProductImage, id=id)
    product = prod_img.product
    prod_img.delete()
    return redirect('staff-product', name=product.name)

class ProductCreateView(ProductView, generic.edit.CreateView): pass

class ProductUpdateView(ProductView, generic.UpdateView): pass

class ProductDeleteView(ProductView, generic.DeleteView):
    def get(self, request, name):
        return redirect('staff-products')

    def get_success_url(self):
        return reverse('staff-products')

@user_passes_test(staff_check, login_url='staff-login')
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

class CollectionListView(StaffTestMixin, generic.ListView):
    model = Collection
    context_object_name = 'collections'
    template_name = 'collections/index.html'

class CollectionView(StaffTestMixin):
    model = Collection
    slug_field = 'name'
    slug_url_kwarg = 'name'
    fields = '__all__'
    template_name = 'collections/view.html'

    def get_success_url(self):
        return reverse('staff-collection', kwargs={'name' : self.object.name})

class CollectionDetailView(CollectionView, generic.DetailView):
    template_name = 'collections/detail.html'

class CollectionCreateView(CollectionView, generic.edit.CreateView): pass

class CollectionUpdateView(CollectionView, generic.UpdateView): pass

class CollectionDeleteView(CollectionView, generic.DeleteView):
    def get(self, request, name):
        return redirect('staff-collections')

    def get_success_url(self):
        return reverse('staff-collections')

@user_passes_test(staff_check, login_url='staff-login')
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