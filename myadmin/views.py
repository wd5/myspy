          # -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from cart.models import Client, CartItem, CartProduct
from forms import ClientForm, StatusForm, BaseProductFormset, CashForm
from django.forms.models import inlineformset_factory
import calc
from cart.cart import _generate_cart_id
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from catalog.models import Product
from models import Cash

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
    clients_wayt_money = Client.objects.exclude(status='CASH_IN').exclude(status='REFUSED').exclude(status='BACK')
    money = 0
    for client in clients_wayt_money:
        products = CartProduct.objects.filter(cartitem=client.cart_id)
        for product in products:
            money += product.product.price * product.quantity
    form = StatusForm()
    # Применяю фильтр по статусам
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
    # Пейджинация
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # 100 клиентов на одну страницу
    paginator = Paginator(clients, 100)
    try:
        clients = paginator.page(page)
    except (EmptyPage, InvalidPage) :
        clients = paginator.page(paginator.num_pages)
    return render_to_response("myadmin/sales.html", locals(), context_instance=RequestContext(request))

@login_required
def store(request):
    products = Product.objects.all()
    money_in_retail = 0
    money_in_wholesale = 0
    for product in products:
        money_in_retail += product.quantity * product.price
        money_in_wholesale += product.quantity * product.wholesale_price
    return render_to_response("myadmin/store/store.html", locals(), context_instance=RequestContext(request))

@login_required
def cash(request):
    cash = Cash.objects.all()
    return render_to_response("myadmin/cash/cash.html", locals(), context_instance=RequestContext(request))

@login_required
def add_cashflow(request):
    form = CashForm()
    if request.method == 'POST':
        last_balance = Cash.objects.all().latest('id')
        form = CashForm(request.POST)
        newform = form.save(commit=False)
        newform.balance = last_balance.balance + newform.cashflow
        newform.save()
        if form.is_valid():
            form.save()
    return render_to_response("myadmin/cash/add_cashflow.html", locals(), context_instance=RequestContext(request))

@login_required
def edit_client(request, id):
    # Получаю нужные данные для работы с формами
    client = Client.objects.get(id=id)
    cartid = client.cart.id
    cart = CartItem.objects.get(id=cartid)
    CartProductFormset = inlineformset_factory(CartItem, CartProduct, formset=BaseProductFormset)
    if request.method == 'POST':
        # Получаю предыдущий статус клиента
        client_status = client.status
        # Сохраняю форму используя объект клиента
        form = ClientForm(request.POST, instance=client, prefix='client')
        form.save()

        # Сохраняю форму используя объект корзины клиента
        formset = CartProductFormset(request.POST, instance=cart)
        if formset.is_valid():
            # Высчитываю сумму и скидку
            calc.subtotal(cartid)
            # Получаю список покупок клиента
            products = CartProduct.objects.filter(cartitem=cart)
            # Обновляю количество товара на складе
            for formitem in formset.cleaned_data:
                if formitem:
                    product_name = formitem['product']
                    quantity = formitem['quantity']
                    # Обновление в случае удаления товара
                    if formitem['DELETE']:
                        store_product = Product.objects.get(name=product_name)
                        store_product.quantity = store_product.quantity + quantity
                        store_product.save()
                    else:
                        # Обновляю если у клиента еще нет товара
                        if not products:
                            store_product = Product.objects.get(name=product_name)
                            store_product.quantity = store_product.quantity - quantity
                            store_product.save()
                        for product in products:
                            # Если такой товар у клиента уже есть
                            if product.product == product_name:
                                # Если количество совпадает то ничего не делаю
                                if product.quantity == quantity:
                                    pass
                                # Если количество изменилось - пишу изменения количества в складе
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
        if form.cleaned_data['status'] == 'CASH_IN':
            if client_status == form.cleaned_data['status']:
                pass
            else:
                newcashflow = Cash()
                newcashflow.cashflow = client.subtotal
                last_balance = Cash.objects.all().latest('id')
                newcashflow.balance = last_balance.balance + client.subtotal
                newcashflow.cause = 'FROM_CLIENT'
                newcashflow.comment = client.id
                newcashflow.save()
        else:
            if client_status == 'CASH_IN':
                cash = Cash.objects.get(comment=client.id)
                cash.delete()
    # Создаю формы
    CartProductFormset = inlineformset_factory(CartItem, CartProduct, formset=BaseProductFormset)
    formset = CartProductFormset(instance=cart)
    client = Client.objects.get(id=id)
    form = ClientForm(instance=client, prefix='client')
    return render_to_response("myadmin/edit_client.html", locals(), context_instance=RequestContext(request))

@login_required
def add_client(request):
    # Создаю формы
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
        # Записываю корзину клиента
        newform.cart_id = cart.id
        newform.save()
        # Сохраняю форму используя объект корзины клиента
        formset = CartProductFormset(request.POST, instance=cart)
        if formset.is_valid():
            # Обновляю количество товара на складе
            for formitem in formset.cleaned_data:
                if formitem:
                    product_name = formitem['product']
                    quantity = formitem['quantity']
                    product = Product.objects.get(name=product_name)
                    true_quantity = product.quantity - quantity
                    product.quantity = true_quantity
                    product.save()
            formset.save()
            # Высчитываю сумму и скидку
            calc.subtotal(cart.id)
        else:
            pass
        # После создания клиента тут же перекидываю на редактирование клиента
        return HttpResponseRedirect(reverse('myadmin.views.edit_client', args=(client.id,)))
    return render_to_response("myadmin/add_client.html", locals(), context_instance=RequestContext(request))

