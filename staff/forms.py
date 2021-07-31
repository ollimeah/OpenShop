from django import forms
from .models import Category, Collection, FAQ, Product, Promotion

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

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

class CategoryProductForm(forms.Form):
    products = forms.ModelMultipleChoiceField(Product.objects, widget = forms.CheckboxSelectMultiple)

class ProductManagementForm(forms.Form):
    action = forms.ChoiceField(choices = ACTION_CHOICES, widget = forms.RadioSelect)
    # all = forms.BooleanField(label = "All Products", required = False)
    products = forms.ModelMultipleChoiceField(Product.objects, widget = forms.CheckboxSelectMultiple)

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = '__all__'

class CollectionProductForm(forms.Form):
    products = forms.ModelMultipleChoiceField(Product.objects, widget = forms.CheckboxSelectMultiple)