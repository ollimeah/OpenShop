from django import forms
from django.forms.widgets import HiddenInput
from .models import Delivery, Product, Address, ProductImage

ACTION_CHOICES = [
    ('delete', 'Delete'),
    ('hide', 'Hide'),
    ('available', 'Make Available'),
    ('unavailable', 'Make Unavailable')
]

class SettingsForm(forms.Form):
    shop_name = forms.CharField(label="Shop Name", max_length=50, required=True, strip=True)
    primary_colour = forms.CharField(label="Primary Colour", max_length=7, widget=forms.TextInput(attrs={'type': 'color'}))
    secondary_colour = forms.CharField(label="Secondary Colour", max_length=7, widget=forms.TextInput(attrs={'type': 'color'}))
    logo = forms.BooleanField(label="Use logo?", required=False)
    carousel = forms.BooleanField(label="Enable carousel?", required=False)

class CategoryProductForm(forms.Form):
    products = forms.ModelMultipleChoiceField(Product.objects, widget = forms.CheckboxSelectMultiple)

class ProductManagementForm(forms.Form):
    action = forms.ChoiceField(choices = ACTION_CHOICES, widget = forms.RadioSelect)
    products = forms.ModelMultipleChoiceField(Product.objects, widget = forms.CheckboxSelectMultiple)

class CollectionProductForm(forms.Form):
    products = forms.ModelMultipleChoiceField(Product.objects, widget = forms.CheckboxSelectMultiple)

class ShippingForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'

class DeliveryChoiceForm(forms.Form):
    delivery = forms.ModelChoiceField(Delivery.objects.filter(available=True), widget=forms.Select)

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = '__all__'
        widgets = {'product':HiddenInput()}