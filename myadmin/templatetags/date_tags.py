from django import template
from datetime import date
from cart.models import Client
from myadmin.models import Cash

register = template.Library()

def spanning_months(start, end):
    assert start <= end
    current = start.year * 12 + start.month - 1
    end = end.year * 12 + end.month - 1
    while current <= end:
        yield date(current // 12, current % 12 + 1, 1)
        current += 1

@register.inclusion_tag("myadmin/tags/date_tags.html")
def date_tags(request_path):
    print request_path
    if 'sales' in request_path:
        latest_client = Client.objects.all().latest('id').ordered_at
        first_client = Client.objects.order_by()[0].ordered_at
        dates = spanning_months(first_client, latest_client)

    elif 'cash' in request_path:
        latest_client = Cash.objects.all().latest('id').date
        first_client = Cash.objects.order_by()[0].date
        dates = spanning_months(first_client, latest_client)

    return {
        'dates': dates,
        'request_path' : request_path
        }
