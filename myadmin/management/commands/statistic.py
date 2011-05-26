from django.core.management.base import BaseCommand
from cart.models import Client, CartProduct, CartItem
from myadmin.models import Waytmoney

class Command(BaseCommand):
    def handle(self, *args, **options):
        clients = Client.objects.filter(cart__product__category=4)
        p = CartProduct.objects.filter(product__category=4)
        sum = 0
        for client in clients:
            i = CartProduct.objects.filter(cartitem=client.cart)
            for z in i:
                sum += z.product.price - z.product.wholesale_price
        print sum
