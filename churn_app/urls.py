from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('users/', views.list_users, name='list_users'),
]
