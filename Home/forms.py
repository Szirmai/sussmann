from django import forms
from django.forms import modelformset_factory
from .models import Product, ProductImage, Contact, New, CategoryNew
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image', 'available', 'categories', 'cost', 'visibility']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'placeholder':'Enter product description'}),
            'price': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Enter price'}),
            'stock': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Enter stock quantity'}),
            'image': forms.ClearableFileInput(attrs={'class':'form-control-file'}),  # itt NEM kell multiple=True
            'available': forms.CheckboxInput(attrs={'class1':'form-check-input'}),
            'categories': forms.Select(attrs={'class':'form-category'}),
            'cost': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Enter cost'}),
            'visibility': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be a positive number.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock

# Formset a további képekhez
ProductImageFormSet = modelformset_factory(
    ProductImage,
    fields=('image',),
    extra=3,  # alapból 3 üres mező
)

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'})
        }

class ContactForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name', 'id': 'name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email', 'id': 'email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the subject', 'id': 'subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'cols': 40, 'placeholder': 'Enter your message', 'id': 'message'}),
            
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if "@" not in email:
            raise forms.ValidationError("Enter a valid email address.")
        return email

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long.")
        return message
        

class ContactStatusForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['status']


class NewForm(forms.ModelForm):
    class Meta:
        model = New
        fields = ['author', 'text', 'image', 'category', 'title']
        widgets = {
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter author name'
            }),
            
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter title'
            }),
            
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Write the article text here'
            }),
            
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            }),
            
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

class NewCategoryForm(forms.ModelForm):
    class Meta:
        model = CategoryNew
        fields = ['name']


class SubscribeForm(forms.Form):
    email = forms.EmailField()
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)