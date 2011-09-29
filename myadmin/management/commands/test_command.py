from django.core.management.base import BaseCommand
from myadmin.models import Cash

class Command(BaseCommand):
    def handle(self, *args, **options):
        cashs = Cash.objects.filter(cause="SALARY_VICTOR")
        b = 0
        for i in cashs:
            b -= i.cashflow
        print b
