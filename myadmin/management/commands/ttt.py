from django.core.management.base import BaseCommand
from cart.models import Client

class Command(BaseCommand):
    def handle(self, *args, **options):
        clients = Client.objects.all()
        for client in clients:
            client.change_log = u'Дата заведения: %s<br>\r' % client.ordered_at
            client.save()
