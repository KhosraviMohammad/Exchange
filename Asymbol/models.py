from django.db import models

# Create your models here.


class Symbol(models.Model):
    name = models.CharField(max_length=150, null=True, blank=True)
    final_price = models.CharField(max_length=150, null=True, blank=True)
    volume = models.CharField(max_length=150, null=True, blank=True)
    price = models.CharField(max_length=150, null=True, blank=True)