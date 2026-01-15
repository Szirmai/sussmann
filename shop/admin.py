from django.contrib import admin
from .models import ShippingCost, Order, OrderItem, ShippingAddress, BillingAddress, Coupon

admin.site.register(ShippingCost)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(ShippingAddress)
admin.site.register(BillingAddress)
admin.site.register(Coupon)
# Register your models here.
