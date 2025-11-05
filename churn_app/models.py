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

    def __str__(self):
        return f"{self.user.username} ({self.role})"
    