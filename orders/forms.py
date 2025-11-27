from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    """
    Checkout Form for placing orders
    """
    class Meta:
        model = Order
        fields = [
            'shipping_name', 'shipping_email', 'shipping_phone',
            'shipping_address', 'shipping_city', 'shipping_country',
            'shipping_postal_code', 'notes'
        ]
        widgets = {
            'shipping_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Full Name'
            }),
            'shipping_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Email Address'
            }),
            'shipping_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Phone Number'
            }),
            'shipping_address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Street Address',
                'rows': 3
            }),
            'shipping_city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'City'
            }),
            'shipping_country': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Country'
            }),
            'shipping_postal_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Postal Code'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Order Notes (Optional)',
                'rows': 3
            }),
        }
