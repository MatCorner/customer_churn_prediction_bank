from django.urls import path
from . import views
from .views import create_transaction

urlpatterns = [
    path('register/', views.register, name='register'),
    path('users/', views.list_users, name='list_users'),
    path('login/', views.login, name='login'),
    path('profile/<int:user_id>/', views.my_profile, name='my_profile'),
    path('profile/<int:user_id>/update/', views.update_profile, name='update_profile'),
    path('transaction/', create_transaction, name='create_transaction'),
    
]
