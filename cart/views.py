          # -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from forms import OrderForm
from settings import SEND_SMS
import cart

def show_cart(request, template_name="cart/cart.html"):
    if request.method == 'POST':
        subtotal_class = cart.Subtotal(request)
        cart_items = cart.get_cart_items(request)
        cart_subtotal = subtotal_class.subtotal()
        discount = subtotal_class.discount
        postdata = request.POST.copy()

        if 'Remove' in postdata:
            cart.remove_from_cart(request)
        elif 'Update' in postdata:
            cart.update_cart(request)
        else:
            form = OrderForm(request.POST)
            if form.is_valid():
                # Пишу клиента в базу
                cart.save_client(request, form)
                # Удаляю сессию у клиента
                del request.session['cart_id']
                is_order = 1
                # Отправляем админу смс
                if SEND_SMS:
                    cart.send_sms(cart_items, form)
                # Отправляем админу email
                cart.send_admin_email(request, cart_items, form, cart_subtotal, discount)
                if form.cleaned_data['email']:
                    # Отправляем email клиенту
                    cart.send_client_email(cart_items, form, cart_subtotal)
    form = OrderForm()
    cart_items = cart.get_cart_items(request)
    if cart_items:
        subtotal_class = cart.Subtotal(request)
        cart_subtotal = subtotal_class.subtotal()
        discount = subtotal_class.discount
    page_title = 'Корзина'
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
