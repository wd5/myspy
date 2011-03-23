          # -*- coding: utf-8 -*-
from django.db import models

CAUSE_CHOICES = (
    ('FROM_CLIENT', 'С продажи'),
    ('SALARY_VLADIMIR', 'Зарплата Владимиру'),
    ('SALARY_VICTOR', 'Зарплата Виктору'),
    ('SALARY_COURIER', 'Зарплата курьеру'),
    ('PURCHASE', 'Закупка товара'),
    ('BRIBE', 'Взятка'),
)

class Cash(models.Model):
    date = models.DateField(auto_now_add=True)
    cashflow = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    cause = models.CharField(max_length=200 ,choices=CAUSE_CHOICES)
    comment = models.CharField(max_length=200, null=True, blank=True)

