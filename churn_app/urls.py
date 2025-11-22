from django.urls import path
from . import views
from .views import create_transaction

urlpatterns = [
    # 注册、登录、用户相关
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('users/', views.list_users, name='list_users'),
    path('profile/<int:user_id>/', views.my_profile, name='my_profile'),
    path('profile/<int:user_id>/update/', views.update_profile, name='update_profile'),

    # 交易相关
    path('transaction/', views.create_transaction, name='create_transaction'),
    path('transactions/', views.all_transactions, name='all_transactions'),  # 管理员查看所有交易
    path('transactions/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),  # 按ID查看单条交易
    
]
