from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Root URL of Home app
    path('about/', views.About, name='about'),
    path('product/<int:product_id>/', views.ProductSingle, name='product_single'),
    path('bolt/', views.Shop, name='shop'),
    
    path('bolt/<str:name>/', views.CatPage, name='cat_page'),
    path('contact/', views.Contact, name='contact'),
    path('success/', views.Success, name='success'),
    path('scubsc/', views.subscribe_view, name='subsc'),
    path('news/', views.news, name='news'),
    path('new/<str:pk>', views.new, name='new'),
    path('adatvedelmi-tajekoztato/', views.policy, name='policy'),
]
