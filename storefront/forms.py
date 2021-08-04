from django import forms

class AddToBasketForm(forms.Form):
    product_name = forms.CharField(widget=forms.HiddenInput)
    quantity = forms.IntegerField(widget=forms.HiddenInput)
