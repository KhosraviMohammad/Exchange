from django.db import models

# Create your models here.


class Symbol(models.Model):
    symbol_name = models.CharField(max_length=30, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    sector = models.CharField(max_length=50, null=True, blank=True)
    market = models.CharField(max_length=50, null=True, blank=True)
    final_price = models.CharField(max_length=30, null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    volume = models.CharField(max_length=30, null=True, blank=True)
    price = models.CharField(max_length=30, null=True, blank=True)
    stored_date = models.DateTimeField(auto_now=True)
    final_price_change = models.CharField(max_length=30, null=True, blank=True)