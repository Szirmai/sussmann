from django.urls import path
from . import views

urlpatterns = [
    path('', views.dash, name='dash-home'),
    path('order/<str:order_id>', views.order_page, name='order-page'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('product-list/', views.product_list, name='product_list'),
    path('order-list/', views.order_list, name='order_list'),
    path('contacts/', views.contacts, name='contacts'),
    path('contact/<int:contact_id>/', views.contact, name='contact_dash'),
    path('edit/shipping-cost/<int:shipping_id>', views.edit_shipping, name='edit_shipping'),
    path('dash/news', views.new_dash, name='new_dash'),
    path('logout/', views.logout, name='logout'),
    path('add/new', views.add_new, name="add_new"),
    path('edit/new/<str:pk>', views.edit_new, name='edit_new'),
]
