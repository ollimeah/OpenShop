from staff.models import Category, Product
from django.views import generic
from django.urls import reverse

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