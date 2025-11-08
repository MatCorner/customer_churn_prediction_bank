from django.db import models

from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('manager', 'Manager'),
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

class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    action = models.CharField(max_length=50, choices=[
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('transfer', 'Transfer'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.amount} ({self.action})"