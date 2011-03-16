          # -*- coding: utf-8 -*-
from django.db import models
from catalog.models import Product

class CartItem(models.Model):
    cart_id = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    product = models.ForeignKey(Product, unique=False)

    class Meta:
        db_table = 'cart_item'
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

STATUS_CHOICES = (
    ('BACK', 'Вернуть'),
    ('POSTSEND', 'Отправить почтой'),
    ('POSTSENDED', 'Отправлено почтой'),
)

class Client(models.Model):
    surname = models.CharField(max_length=50, null=True, blank=True, verbose_name="Фамилия")
    name = models.CharField(max_length=50, verbose_name="Имя")
    patronymic = models.CharField(max_length=50, null=True, blank=True, verbose_name="Отчество")
    city = models.CharField(max_length=50, null=True, blank=True, verbose_name="Город")
    postcode = models.IntegerField(null=True, blank=True, verbose_name="Индекс")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.CharField(max_length=50, null=True, blank=True, verbose_name="Адрес")
    email = models.EmailField(null=True, blank=True)
    cart = models.CharField(max_length=50)
    ordered_at = models.DateTimeField(auto_now_add=True )
    subtotal = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name="Сумма")
    discount = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name="Скидка")
    tracking_number = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус")
    referrer = models.URLField(verify_exists=False)

    def get_order(self):
        cart_items = CartItem.objects.filter(cart_id = self.cart)
        products = ""
        for item in cart_items:
            products += u"%s - %sшт; " % (item.product.slug, item.quantity )
        return products

    class Meta:
        ordering = ['-ordered_at']

    def __unicode__(self):
        return self.name
