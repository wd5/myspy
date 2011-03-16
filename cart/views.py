          # -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from catalog.forms import OrderForm
import cart

def show_cart(request, template_name="cart/cart.html"):
    if request.method == 'POST':
        subtotal_class = cart.Subtotal(request)
        cart_items = cart.get_cart_items(request)
        cart_subtotal = subtotal_class.subtotal()
        discount = subtotal_class.discount
        postdata = request.POST.copy()
        form = OrderForm(postdata)

        if 'Remove' in postdata:
            cart.remove_from_cart(request)
        if 'Update' in postdata:
            cart.update_cart(request)
        if form.is_valid():
            # Пишу клиента в базу
            cart.save_client(request, form)
            # Удаляю сессию у клиента
            del request.session['cart_id']
            is_order = 1
            # Отправляем админу смс
            cart.send_sms(cart_items, form)
            # Отправляем админу email
            cart.send_admin_email(request, cart_items, form, cart_subtotal, discount)
            if form.cleaned_data['email']:
                # Отправляем email клиенту
                cart.send_client_email(cart_items, form, cart_subtotal)
    else:
        form = OrderForm()

    subtotal_class = cart.Subtotal(request)
    cart_items = cart.get_cart_items(request)
    page_title = 'Корзина'
    cart_subtotal = subtotal_class.subtotal()
    discount = subtotal_class.discount
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
