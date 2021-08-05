from django import forms

class AddProductToBasketForm(forms.Form):
    product_name = forms.CharField(widget=forms.HiddenInput)
    quantity = forms.IntegerField(widget=forms.HiddenInput)
