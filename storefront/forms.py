from django import forms
from django.forms.widgets import HiddenInput

class AddProductToBasketForm(forms.Form):
    product_name = forms.CharField(widget=forms.HiddenInput)
    quantity = forms.IntegerField(widget=forms.HiddenInput)

class AddCollectionToBasketForm(forms.Form):
    collection_name = forms.CharField(widget=HiddenInput)
    quantity = forms.IntegerField(widget=HiddenInput)

class PromotionCodeForm(forms.Form):
    code = forms.CharField(required=True, strip=True)