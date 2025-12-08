
from django.db import models
from django.contrib.auth.models import User  # For author


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)  # The name of the product
    description = models.TextField()  # A detailed description of the product
    price = models.DecimalField(max_digits=10, decimal_places=0)  # Price with 2 decimal places
    stock = models.PositiveIntegerField()  # The number of items in stock
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when the product is created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set when the product is updated
    image = models.ImageField(upload_to='products/', null=True)  # Image field (optional)
    available = models.BooleanField(default=True)
    categories = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return self.name  # String representation of the product (display name in admin)
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"Image for {self.product.name}"


class DealOfMonth(models.Model):
    percent = models.IntegerField(default=20)
    per = models.CharField(max_length=50, default="...", null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when the product is created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set when the product is updated
    image = models.ImageField(upload_to='products/', null=True)  # Image field (optional)
    available = models.BooleanField(default=True)
    exp_date = models.DateField()

    def __str__(self):
        return self.title
    
class YouTube(models.Model):
    motto = models.CharField(max_length=200)
    link = models.URLField()
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    index = models.ImageField(upload_to='products/', null=True)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __srt__(self):
        return self.title

class Quotes(models.Model):
    name = models.CharField(max_length=150, null=True)
    quote = models.TextField(max_length=500, null=True)
    attribute = models.CharField(max_length=150, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Team(models.Model):
    on = models.BooleanField(null=True, default=True)
    name = models.CharField(null=True, max_length=150)
    instagram = models.URLField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to='team/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    work = models.CharField(max_length=70, null=True)

    def __str__(self):
        return self.name
    

STATUS_CHOICES = [
    ("Új", "Új"),
    ("Megtekintve", "Megtenkintve"),
    ("Válaszolva", "Válaszolva"),
]


class Contact(models.Model):
    name = models.CharField(max_length=100)  # Name of the person contacting
    email = models.EmailField()  # Email address
    subject = models.CharField(max_length=200)  # Subject of the message
    message = models.TextField()  # The message content
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the message was sent
    status = models.CharField(max_length=50, null=True, choices=STATUS_CHOICES, default="Új")

    def __str__(self):
        return f"{self.name} - {self.subject}"
    

class Subsc(models.Model):
    email = models.EmailField(max_length=200, null=True)

    def __str__(self):
        return self.email
    

class CategoryNew(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
    

class New(models.Model):
    author = models.CharField(max_length=200, null=True)
    date = models.DateField(auto_now_add=True)
    category = models.ForeignKey(CategoryNew, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200, null=True)
    text = models.TextField(max_length=10000, null=True)
    image = models.ImageField(upload_to='mews/', null=True)

    def __str__(self):
        return self.title
