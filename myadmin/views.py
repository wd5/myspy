          # -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from cart.models import Client, CartItem, CartProduct
from forms import ClientForm, BaseProductFormset
from django.forms.models import modelformset_factory, inlineformset_factory
from catalog.models import Product
import calc
from cart.cart import _generate_cart_id
from django.core.urlresolvers import reverse


def auth(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return HttpResponseRedirect("/myadmin/sales")
        else:
            error = True
    return render_to_response("myadmin/auth.html", locals(), context_instance=RequestContext(request))

@login_required
def sales(request):
    all_clients = Client.objects.all()
    return render_to_response("myadmin/sales.html", locals(), context_instance=RequestContext(request))

def store(request):
    pass

def cash(request):
    pass

@login_required
def edit_client(request, id):
    client = Client.objects.get(id=id)
    cartid = client.cart.id
    cart = CartItem.objects.get(id=cartid)
    CartProductFormset = inlineformset_factory(CartItem, CartProduct, formset=BaseProductFormset)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client, prefix='client')
        form.save()
        formset = CartProductFormset(request.POST, instance=cart)
        if formset.is_valid():
            formset.save()
            calc.subtotal(cartid)
        else:
            pass
    CartProductFormset = inlineformset_factory(CartItem, CartProduct, formset=BaseProductFormset)
    formset = CartProductFormset(instance=cart)
    client = Client.objects.get(id=id)
    form = ClientForm(instance=client, prefix='client')
    return render_to_response("myadmin/edit_client.html", locals(), context_instance=RequestContext(request))

@login_required
def add_client(request):
    form = ClientForm()
    CartProductFormset = inlineformset_factory(CartItem, CartProduct)
    formset = CartProductFormset()
    if request.method == 'POST':
        # Создаю объект корзины для клиента
        cart = CartItem()
        cart.cart_id = _generate_cart_id()
        cart.save()
        # Создаю объект клиента
        client = Client()
        # Сохраняю форму используя объект созданного клиента
        form = ClientForm(request.POST, instance=client)
        newform = form.save(commit=False)
        newform.cart_id = cart.id
        newform.save()
        formset = CartProductFormset(request.POST, instance=cart)
        if formset.is_valid():
            formset.save()
            calc.subtotal(cart.id)
        else:
            pass
        # После создания клиента тут же перекидываю на редактирование клиента
        return HttpResponseRedirect(reverse('myadmin.views.edit_client', args=(client.id,)))
    return render_to_response("myadmin/add_client.html", locals(), context_instance=RequestContext(request))

