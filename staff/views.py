from django.shortcuts import render
from .forms import *
from .models import *

def dashboard(request):
    return render(request, 'dashboard.html')

def products(request):
    return render(request, 'products/index.html')

def settings(request):
    settings = Settings()
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            settings.update(form.cleaned_data)

    form = SettingsForm(settings.as_dict())
        
    context = {'form': form}
    return render(request, 'settings.html', context)