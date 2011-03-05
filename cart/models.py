          # -*- coding: utf-8 -*-
from django.db import models
from catalog.models import Products

class CartItem(models.Model):
    cart_id = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    product = models.ForeignKey(Products, unique=False)

    class Meta:
        db_table = 'cart_items'
        ordering = ['date_added']

    def total(self):
        return self.quantity * self.product.price

    def name(self):
        return self.product.name

    def price(self):
        return self.product.price

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def augment_quantity(self, quantity):
        self.quantity = self.quantity + int(quantity)
        self.save()

class Clients(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50, null=True, blank=True)
    patronymic = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    postcode = models.IntegerField(null=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    cart = models.CharField(max_length=50)
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name
