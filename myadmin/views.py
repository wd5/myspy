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
#        form = ClientForm(request.POST, instance=client, prefix='client')
        formset = CartProductFormset(request.POST, instance=cart)
        formset.save()
    CartProductFormset = inlineformset_factory(CartItem, CartProduct, formset=BaseProductFormset)
    formset = CartProductFormset(instance=cart)
#    form = ClientForm(instance=client, prefix='client')
    return render_to_response("myadmin/edit_client.html", locals(), context_instance=RequestContext(request))
