from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='bussiness_home'),
    path('add-cost/', views.add_cost, name='add_cost'),
    path('edit/<int:cost_id>/', views.edit_cost, name='edit_cost'),
    path('delete/<int:cost_id>/', views.delete_cost, name='delete_cost'),
    path('add-category/', views.add_cost_cat, name='add_cost_cat'),
    path('delete-category/<int:cost_id>', views.delete_cost_cat, name='delete_cost_cat'),
]
