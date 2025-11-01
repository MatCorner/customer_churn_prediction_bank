from django.db import models

from django.contrib.auth.models import User

class Customer(models.Model):
    # Link to built-in Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    marital_status = models.CharField(max_length=20)
    balance = models.FloatField(default=0)
    tenure = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username