from django import forms
from .models import Product, Review, Category

class ProductForm(forms.ModelForm):
    """
    Product Creation/Edit Form
    """
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'price', 'compare_price', 
            'stock', 'eco_score', 'eco_certifications', 'carbon_footprint',
            'recyclable', 'biodegradable', 'image', 'image2', 'image3'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Product Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Product Description',
                'rows': 5
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Price',
                'step': '0.01'
            }),
            'compare_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Compare Price (Optional)',
                'step': '0.01'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Stock Quantity'
            }),
            'eco_score': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Eco Score (1-100)',
                'min': '1',
                'max': '100'
            }),
            'eco_certifications': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'e.g., Organic, Fair Trade'
            }),
            'carbon_footprint': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Carbon Footprint (kg CO2)',
                'step': '0.01'
            }),
            'recyclable': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500'
            }),
            'biodegradable': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none'
            }),
            'image2': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none'
            }),
            'image3': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none'
            }),
        }


class ProductSearchForm(forms.Form):
    """
    Product Search Form
    """
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
            'placeholder': 'Search eco-friendly products...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none'
        })
    )
    min_eco_score = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
            'placeholder': 'Min Eco Score',
            'min': '1',
            'max': '100'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
            'placeholder': 'Max Price',
            'step': '0.01'
        })
    )


class ReviewForm(forms.ModelForm):
    """
    Product Review Form
    """
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none'
                }
            ),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Review Title'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Share your experience with this product',
                'rows': 5
            }),
        }
