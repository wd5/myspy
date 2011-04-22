from django.core.management.base import BaseCommand, CommandError
from cart.models import Client, CartProduct
from myadmin.models import Statistic

class Command(BaseCommand):
    def handle(self, *args, **options):
            clients_wayt_money = Client.objects.exclude(status='CASH_IN').exclude(status='REFUSED').exclude(status='BACK')
            money = 0
            for client in clients_wayt_money:
                products = CartProduct.objects.filter(cartitem=client.cart_id)
                for product in products:
                    money += product.product.price * product.quantity
            wayt_money = Statistic.objects.get(id=1)
            wayt_money.wayt_money = money
            wayt_money.save()
