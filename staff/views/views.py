from django.shortcuts import render
from staff.forms import SettingsForm
from staff.models import Order, Product, Settings

def dashboard(request):
    context = {'orders_today' : Order.num_orders_today(), 'sales_today' : Order.sales_today(), 
                'available_products' : Product.num_available(), 'best_sellers' : Product.best_sellers(5), 
                'recent_orders' : Order.recent_orders(10)}
    return render(request, 'staff/dashboard.html', context)

def settings(request):
    settings = Settings()
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            settings.update(form.cleaned_data)

    form = SettingsForm(settings.as_dict())
        
    context = {'form': form}
    return render(request, 'settings.html', context)