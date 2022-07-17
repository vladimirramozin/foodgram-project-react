from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.CharField(max_length=254, unique=True)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=150)
    password = models.CharField(max_length=150)
    #subscriptions = models.ManyToManyField('self', related_name='subscriptions',blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        ordering = ['-id']




