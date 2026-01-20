from django.db import models
from django.contrib.auth.models import User  # For author
import uuid
from Home.models import Product
from django.utils import timezone


class Coupon(models.Model):
    code = models.CharField(
        max_length=20,
        unique=True
    )

    DISCOUNT_TYPE_CHOICES = (
        ('percent', 'Százalékos'),
        ('fixed', 'Fix összeg'),
    )
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES
    )
    discount_value = models.PositiveIntegerField(
        help_text="Százalék vagy forint érték"
    )

    active = models.BooleanField(default=True)

    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Összesen hányszor használható (üres = végtelen)"
    )
    used_count = models.PositiveIntegerField(default=0)

    min_cart_value = models.PositiveIntegerField(
        default=0,
        help_text="Minimum kosárérték (Ft)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self, cart_total):
        now = timezone.now()

        if not self.active:
            return False
        if not (self.valid_from <= now <= self.valid_to):
            return False
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False
        if cart_total < self.min_cart_value:
            return False

        return True

    def __str__(self):
        return self.code


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
    created_at = models.DateTimeField(default=timezone.now)
    tax = models.CharField(max_length=200, null=True)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    discount_amount = models.IntegerField(default=0)


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