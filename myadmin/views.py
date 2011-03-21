          # -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from cart.models import Client, CartItem, CartProduct
from forms import ClientForm, StatusForm, BaseProductFormset
from django.forms.models import inlineformset_factory
import calc
from cart.cart import _generate_cart_id
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
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
    form = StatusForm()
    if request.method == 'POST':
        form = StatusForm(request.POST)
        if form.is_valid():
            clients = []
            for i in form.cleaned_data['status']:
               clients += Client.objects.filter(status=i)
            # Сортирую по id - так чтобы полследний клиент был сверху
            clients.sort(key=lambda x: x.id, reverse=True)
    else:
        clients = Client.objects.all()
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(clients, 100)
    try:
        clients = paginator.page(page)
    except (EmptyPage, InvalidPage) :
        clients = paginator.page(paginator.num_pages)
    return render_to_response("myadmin/sales.html", locals(), context_instance=RequestContext(request))

@login_required
def store(request):
    products = Product.objects.all()
    return render_to_response("myadmin/store/store.html", locals(), context_instance=RequestContext(request))

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
            calc.subtotal(cartid)
            products = CartProduct.objects.filter(cartitem=cart)
            for formitem in formset.cleaned_data:
                if formitem:
                    product_name = formitem['product']
                    quantity = formitem['quantity']
                    if formitem['DELETE']:
                        store_product = Product.objects.get(name=product_name)
                        store_product.quantity = store_product.quantity + quantity
                        store_product.save()
                    else:
                        if not products:
                            store_product = Product.objects.get(name=product_name)
                            store_product.quantity = store_product.quantity - quantity
                            store_product.save()
                        for product in products:
                            if product.product == product_name:
                                if product.quantity == quantity:
                                    pass
                                else:
                                    store_quantity = quantity - product.quantity
                                    store_product = Product.objects.get(name=product_name)
                                    store_product.quantity = store_product.quantity - store_quantity
                                    store_product.save()
                            else:
                                pass
            formset.save()
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
            for formitem in formset.cleaned_data:
                if formitem:
                    product_name = formitem['product']
                    quantity = formitem['quantity']
                    product = Product.objects.get(name=product_name)
                    true_quantity = product.quantity - quantity
                    product.quantity = true_quantity
                    product.save()
            calc.subtotal(cart.id)
            formset.save()
        else:
            pass
        # После создания клиента тут же перекидываю на редактирование клиента
        return HttpResponseRedirect(reverse('myadmin.views.edit_client', args=(client.id,)))
    return render_to_response("myadmin/add_client.html", locals(), context_instance=RequestContext(request))

