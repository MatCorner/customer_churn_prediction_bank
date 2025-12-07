from django.urls import path
from . import views

urlpatterns = [
    # --- Teammate's Original APIs ---
    path("register/", views.register, name='register'),
    path("login/", views.login_view, name='login'),
    path("users/", views.list_users, name='list_users'),
    path("transaction/", views.create_transaction, name='create_transaction_generic'),

    # --- Your Frontend Pages (HTML) ---
    path('page/login/', views.page_login, name='page_login'),
    path('dashboard/', views.page_dashboard, name='page_dashboard'),

    # --- Your Frontend APIs (Simplified for easier JS calls) ---
    # Profile & Prediction
    path('profile/me/', views.profile_me, name='profile_me'),

    # Wallet & Account Info
    path('accounts/my/', views.my_accounts, name='my_accounts'),

    # Quick Actions
    path('transactions/deposit/', views.deposit, name='deposit'),
    path('transactions/withdraw/', views.withdraw, name='withdraw'),
    path('transactions/transfer/', views.transfer, name='transfer'),
]