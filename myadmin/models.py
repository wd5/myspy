          # -*- coding: utf-8 -*-
from django.db import models

CAUSE_CHOICES = (
    ('FROM_CLIENT', 'С продажи'),
    ('SALARY_VLADIMIR', 'Зарплата Владимиру'),
    ('SALARY_VICTOR', 'Зарплата Виктору'),
    ('SALARY_COURIER', 'Зарплата курьеру'),
    ('PURCHASE', 'Закупка товара'),
    ('BRIBE', 'Взятка'),
    ('SENDGOODS', 'Отправка товара'),
    ('PHONE', 'На телефон'),
    ('Yandex', 'Яндекс Директ'),
    ('OTHER', 'Прочее'),
)

TYPE_CHOICES = (
    ('ENCASH', 'Наличные'),
    ('WEBMONEY', 'Webmoney'),
    ('YANDEX', 'Яндекс'),
)

class Cash(models.Model):
    date = models.DateField(auto_now_add=True)
    cashflow = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Поток")
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    cause = models.CharField(max_length=200 ,choices=CAUSE_CHOICES, verbose_name="Причина")
    type = models.CharField(default='Encash',max_length=200 ,choices=TYPE_CHOICES, verbose_name="Тип")
    comment = models.CharField(max_length=200, null=True, blank=True, verbose_name="Комментарий")

    class Meta:
        ordering = ['-id']

class Balance(models.Model):
    yandex = models.DecimalField(max_digits=10, decimal_places=2)
    webmoney = models.DecimalField(max_digits=10, decimal_places=2)
    encash = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

class Waytmoney(models.Model):
    wayt_money = models.DecimalField(max_digits=20, decimal_places=2)

class Statistic(models.Model):
    date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=200)
    cash = models.DecimalField(max_digits=10, decimal_places=2)
