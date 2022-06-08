from django.db import models


class User(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=254, blank=False)
    username = models.CharField(max_length=150, blank=False)
    first_name = models.CharField(max_length=10, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    password = models.CharField(max_length=150, blank=False)

    class Meta:
        ordering = ('created',)
