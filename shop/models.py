from django.db import models
from django.contrib.auth.models import User  # For author
import uuid
from Home.models import Product

class ShippingCost(models.Model):
    cost = models.IntegerField(default=2500, null=True)

    def __int__(self):
        return self.cost
    
    


STATUS_CHOICES = [
    ("Új", "Új"),
    ("Megtekintve", "Megtekintve"),
    ("Összekészítve", "Összekészítve"),
    ("Becsomagolva", "Becsomagolva"),
    ("Feladva", "Feladva"),
    ("Kiszállítva", "Kiszállítva"),
]


class Order(models.Model):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=True)
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    payment_method = models.CharField(max_length=20, null=True)
    all_cost = models.IntegerField(null=True)
    net_price = models.IntegerField(null=True)
    brutto_price = models.IntegerField(null=True)
    shipping_cost = models.ForeignKey(ShippingCost, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=50, null=True, choices=STATUS_CHOICES, default="Új")
    created_at = models.DateTimeField(auto_now_add=True)
    tax = models.CharField(max_length=200, null=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    

class BillingAddress(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    company = models.CharField(max_length=200, null=True)
    tax = models.CharField(max_length=13, null=True, blank=True)
    address = models.CharField(max_length=300, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.DateTimeField(auto_now_add=True)
    payment_deadline = models.DateTimeField(auto_now_add=True)

class ShippingAddress(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True)
    state_num = models.IntegerField(null=True, blank=True)
    door_num = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=200, null=True)
    personal = models.BooleanField(null=True, default=True)