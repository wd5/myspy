from django.core.management.base import BaseCommand
from datetime import date, timedelta
from myadmin.models import Cash, Statistic

class Command(BaseCommand):
    def handle(self, *args, **options):
        today = date.today()
        cash = Cash.objects.filter(date=today)
        cash_in = 0
        cash_out = 0
        for i in cash:
            if i.cashflow > 0:
                cash_in += i.cashflow
            else:
                cash_out -= i.cashflow
        cash_all = cash_in + cash_out
        stat = Statistic()
        stat.date = today
        stat.type = 'cash_in'
        stat.cash = cash_in
        stat.save()
        stat = Statistic()
        stat.date = today
        stat.type = 'cash_out'
        stat.cash = cash_out
        stat.save()

