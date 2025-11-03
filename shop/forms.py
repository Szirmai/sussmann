from django import forms
from .models import Order, ShippingCost

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }

class EditShipping(forms.ModelForm):
    class Meta:
        model = ShippingCost
        fields = ['cost']
