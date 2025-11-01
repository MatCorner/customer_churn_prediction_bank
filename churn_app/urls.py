from django.urls import path
from . import views

urlpatterns = [
    path('customers/', views.customer_list_create, name='customer_api'),
]
