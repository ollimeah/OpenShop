from django.shortcuts import render
from .forms import *
from .models import *
from django.views import generic
from django.urls import reverse

def dashboard(request):
    return render(request, 'dashboard.html')

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

def settings(request):
    settings = Settings()
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            settings.update(form.cleaned_data)

    form = SettingsForm(settings.as_dict())
        
    context = {'form': form}
    return render(request, 'settings.html', context)