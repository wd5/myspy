          # -*- coding: utf-8 -*-
from django.db import models
from catalog.models import Product
from datetime import datetime


class CartProduct(models.Model):
    cartitem = models.ForeignKey('CartItem')
    product = models.ForeignKey(Product, verbose_name='Товар')
    quantity = models.IntegerField(default=1, verbose_name='Количество')

    def augment_quantity(self, quantity):
        self.quantity = self.quantity + int(quantity)
        self.save()

class CartItem(models.Model):
    cart_id = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)
#    quantity = models.IntegerField(default=1)
    product = models.ManyToManyField(Product, through=CartProduct)

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
    ('PROCESS', 'Обработать'),
    ('POSTSEND', 'Отправить почтой'),
    ('POSTSENDED', 'Отправлено почтой'),
    ('COURIER_SEND', 'Отправить курьером'),
    ('COURIER_TAKE', 'Передано курьеру'),
    ('BUYER_TAKE', 'Передано покупателю'),
    ('WAYT_PRODUCT', 'Ожидание поступления товара'),
    ('BACK', 'Обмен/Возврат'),
    ('CONTACT_AT', 'Связаться в назначенное время'),
    ('REFUSED', 'Снятие заявки клиентом'),
    ('CASH_IN', 'Деньги внесены'),
)

DELIVERY_CHOICES = (
    ('EMS', 'EMS'),
    ('COURIER', 'Курьер'),
)

class Client(models.Model):
    surname = models.CharField(max_length=50, null=True, blank=True, verbose_name="Фамилия")
    name = models.CharField(max_length=50, verbose_name="Имя")
    patronymic = models.CharField(max_length=50, null=True, blank=True, verbose_name="Отчество")
    city = models.CharField(max_length=50, null=True, blank=True, verbose_name="Город")
    postcode = models.IntegerField(null=True, blank=True, verbose_name="Индекс")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.CharField(max_length=500, null=True, blank=True, verbose_name="Адрес")
    email = models.EmailField(null=True, blank=True)
    cart = models.ForeignKey(CartItem)
    ordered_at = models.DateTimeField(auto_now_add=True )
    subtotal = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name="Сумма")
    discount = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name="Скидка")
    tracking_number = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус", default='PROCESS')
    referrer = models.URLField(verify_exists=False, max_length=500)
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')
    execute_at = models.DateTimeField(editable=True,null=True, blank=True, verbose_name='Время исполнения')
    delivery = models.CharField(max_length=20, choices=DELIVERY_CHOICES, null=True, blank=True, verbose_name='Способ доставки')

    def get_order(self):
        cart_items = CartProduct.objects.filter(cartitem = self.cart.id)
        products = ""
        for item in cart_items:
            products += u"%s - %sшт; " % (item.product.slug, item.quantity )
        return products

    class Meta:
        ordering = ['-ordered_at']

    def __unicode__(self):
        return self.name
