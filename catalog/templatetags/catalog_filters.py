from django import template
from catalog.models import Section
from cart import cart
from decimal import *

register = template.Library()

@register.inclusion_tag("tags/sidebar.html")
def category_list(request_path):
    active_sections = Section.objects.all()
    return {
        'request_path': request_path,
        'sections': active_sections
}

@register.inclusion_tag("cart/cart_box.html")
def cart_box(request):
    box_count = cart.cart_distinct_item_count(request)
    return {
        'box_count': box_count,
}

@register.filter
def div(value, arg):
    return value % arg
