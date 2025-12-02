from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register),
    path("login/", views.login_view),
    path("profile/", views.my_profile),
    path("profile/update/", views.update_profile),
    path("account/create/", views.create_account),
    path("transaction/", views.create_transaction),
    path("users/", views.list_users),
    path("accounts/", views.list_accounts),
    path("transactions/admin/", views.transaction_history),
    path("transactions/me/", views.my_transactions),
]
