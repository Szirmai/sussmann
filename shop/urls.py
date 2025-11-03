from django.urls import path
from shop.views import cart_add, cart_remove, cart_view, checkout, create_order

urlpatterns = [
    path('add/<int:product_id>/', cart_add, name='cart_add'),
    path('remove/<int:product_id>/', cart_remove, name='cart_remove'),
    path('', cart_view, name='cart_view'),
    path('checkout/', checkout, name='checkout'),
    path('checkout/create_order/', create_order, name='create_order'),
]
