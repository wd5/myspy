          # -*- coding: utf-8 -*-
from django.db import models

class Cash(models.Model):
    date = models.DateField(auto_now_add=True)
    cashflow = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    cause = models.CharField(max_length=20)