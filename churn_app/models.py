from django.db import models

from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    )
    # Link to built-in Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    age = models.IntegerField(null=True, blank=True)             # only for customers
    marital_status = models.CharField(max_length=20, blank=True) # only for customers
    balance = models.FloatField(default=0)                       # only for customers
    tenure = models.IntegerField(default=0)                      # only for customers

    # 顾客注册时间
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Account(models.Model):
    ACCOUNT_TYPES = (
        ('debit', 'Debit Account'),
        ('credit', 'Credit Account'),
    )

    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="accounts")
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class Transaction(models.Model):
    sender_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name="sent")
    recipient_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name="received")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    action = models.CharField(max_length=20, choices=[
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('transfer', 'Transfer'),
        ('payment', 'Payment'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    
class Loan(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.FloatField()
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('default', 'Default'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)


class BehaviorLog(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    metadata = models.JSONField(default=dict)  # 记录额外行为细节
    created_at = models.DateTimeField(auto_now_add=True)
