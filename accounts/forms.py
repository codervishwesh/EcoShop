from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    """
    User Registration Form
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
            'placeholder': 'Email Address'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
            'placeholder': 'Confirm Password'
        })


class UserLoginForm(AuthenticationForm):
    """
    User Login Form
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
            'placeholder': 'Password'
        })
    )


class UserProfileForm(forms.ModelForm):
    """
    User Profile Update Form
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'country', 'postal_code', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Email Address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Phone Number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Address',
                'rows': 3
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'City'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Country'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
                'placeholder': 'Postal Code'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none'
            }),
        }


class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom Password Reset Form
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-500 focus:outline-none',
            'placeholder': 'Email Address'
        })
    )
