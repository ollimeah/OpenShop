from django.shortcuts import get_object_or_404, redirect, render
from staff.forms import SettingsForm
from staff.models import Basket, Order, Product, Settings
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views import generic

def staff_check(user):
    return user.groups.filter(name='Staff').exists()

class StaffTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Staff').exists()
    
    def get_login_url(self):
        return reverse('staff-login')

@user_passes_test(staff_check, login_url='staff-login')
def dashboard(request):
    context = {'orders_today' : Order.num_orders_today(), 'sales_today' : Order.sales_today(), 
                'available_products' : Product.num_available(), 'best_sellers' : Product.best_sellers(5), 
                'recent_orders' : Order.recent_orders(10)}
    return render(request, 'staff/dashboard.html', context)

@user_passes_test(staff_check, login_url='staff-login')
def home(request):
    return render(request, 'staff/home/home.html', {})

@user_passes_test(staff_check, login_url='staff-login')
def settings(request):
    settings = Settings()
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            settings.update(form.cleaned_data)
    form = SettingsForm(settings.as_dict())
    context = {'form': form}
    return render(request, 'staff/settings.html', context)

class OrderListView(StaffTestMixin, generic.ListView):
    model = Order
    template_name = 'staff/orders/index.html'
    context_object_name = 'orders'
    ordering = ['-date_ordered']

class OrderDetailView(StaffTestMixin, generic.DetailView):
    model = Order
    template_name = 'staff/orders/detail.html'

@user_passes_test(staff_check, login_url='staff-login')
def toggle_shipped(request, pk):
    get_object_or_404(Order, id=pk).toggle_shipped()
    return redirect('staff-order', pk=pk)

class BasketListView(StaffTestMixin, generic.ListView):
    model = Basket
    template_name = 'staff/baskets/index.html'
    context_object_name = 'baskets'
    ordering = ['-date_updated']

class BasketDetailView(StaffTestMixin, generic.DetailView):
    model = Basket
    template_name = 'staff/baskets/detail.html'