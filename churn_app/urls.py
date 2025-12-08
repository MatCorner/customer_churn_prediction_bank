from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("register/", views.register, name='register'),
    path("login/", views.login_view, name='login'),

    # Manager Pages & APIs
    path("manager/dashboard/", views.page_manager_dashboard, name='page_manager_dashboard'),
    path("manager/alerts/", views.manager_alerts, name='manager_alerts'),
    path("users/", views.list_users, name='list_users'), # Auto-analyzes on load
    path("users/<int:user_id>/analyze/", views.analyze_user_churn, name='analyze_user_churn'),

    # Client Pages & APIs
    path('page/login/', views.page_login, name='page_login'),
    path('dashboard/', views.page_dashboard, name='page_dashboard'),
    path('profile/me/', views.profile_me, name='profile_me'),
    path('accounts/my/', views.my_accounts, name='my_accounts'),
    path('alerts/my/', views.client_alerts, name='client_alerts'),

    # Transactions
    path('transactions/deposit/', views.deposit, name='deposit'),
    path('transactions/withdraw/', views.withdraw, name='withdraw'),
    path('transactions/transfer/', views.transfer, name='transfer'),
    path("transaction/", views.create_transaction, name='create_transaction_generic'),
]