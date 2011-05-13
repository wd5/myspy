          # -*- coding: utf-8 -*-
from datetime import date, timedelta
import urllib, urllib2
from hashlib import md5
from django.shortcuts import render_to_response
from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from cart.models import Client, CartItem, CartProduct
from forms import ClientForm, BaseProductFormset, CashForm, BalanceForm
from django.forms.models import inlineformset_factory
import calc
from cart.cart import _generate_cart_id
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from catalog.models import Product
from models import Cash, Balance, Waytmoney
from django.contrib.auth import logout
import re

def auth(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return HttpResponseRedirect("/myadmin/sales/all/")
        else:
            error = True
    return render_to_response("myadmin/auth.html", locals(), context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    url = urlresolvers.reverse('auth-page')
    return HttpResponseRedirect(url)

def week_boundaries(year, week):
    start_of_year = date(year, 1, 1)
    now = start_of_year + timedelta(weeks=week)
    mon = now - timedelta(days=now.weekday())
    sun = mon + timedelta(days=6)
    return mon, sun

@login_required
def sales(request, when):
    money = Waytmoney.objects.get(id=1).wayt_money
    today = date.today()
    # Применяю фильтр по статусам
    if request.method == 'POST':
        clients = []
        statuses = []
        for status in request.POST.getlist('status'):
            statuses.append(status)
            clients += Client.objects.filter(status=status)
        # Сортирую по id - так чтобы полследний клиент был сверху
        clients.sort(key=lambda x: x.id, reverse=True)
    else:
        if when == 'today':
            clients = Client.objects.filter(ordered_at__year=today.year, ordered_at__month=today.month, ordered_at__day=today.day)
        elif when == 'week':
            monday, sunday = week_boundaries(today.year, int(today.strftime("%W")))
            clients = Client.objects.filter(ordered_at__year=today.year, ordered_at__month=today.month, ordered_at__range=(monday,sunday))
        elif when == 'month':
            clients = Client.objects.filter(ordered_at__year=today.year, ordered_at__month=today.month)
        elif when == 'year':
            clients = Client.objects.filter(ordered_at__year=today.year)
        elif when == 'all':
            clients = Client.objects.all()
        else:
            clients = Client.objects.filter(ordered_at__year=when[-4:], ordered_at__month=when[:-4])
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
    return render_to_response("myadmin/sale/sales.html", locals(), context_instance=RequestContext(request))

@login_required
def add_client(request):
    # Создаю формы
    form = ClientForm()
    CartProductFormset = inlineformset_factory(CartItem, CartProduct, formset=BaseProductFormset, extra=1)
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
        if form.is_valid():
            newform = form.save(commit=False)
            # Записываю корзину клиента
            newform.cart_id = cart.id
            newform.last_user = request.user.first_name
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
    return render_to_response("myadmin/sale/client_form.html", locals(), context_instance=RequestContext(request))

@login_required
def delete_client(request, id):
    client = Client.objects.get(id=id)
    cart_id = client.cart.id
    client.delete()
    cart = CartItem.objects.get(id=cart_id)
    cart.delete()
    return HttpResponseRedirect(urlresolvers.reverse(sales))

@login_required
def edit_client(request, id):
    # Получаю нужные данные для работы с формами
    client = Client.objects.get(id=id)
    cartid = client.cart.id
    cart = CartItem.objects.get(id=cartid)
    CartProductFormset = inlineformset_factory(CartItem, CartProduct, formset=BaseProductFormset, extra=1)
    if request.method == 'POST':
        # Получаю предыдущий статус клиента
        client_status = client.status
        sms_status = client.sms_status
        # Сохраняю форму используя объект клиента
        form = ClientForm(request.POST, instance=client, prefix='client')
        if form.is_valid():
            newform = form.save(commit=False)
            newform.last_user = request.user.first_name
            if newform.sms_status:
                if not sms_status:
                    login = 'palv1@yandex.ru'
                    password = '97ajhJaj9zna'
                    phone = re.sub("\D", "", newform.phone)
                    from_phone = "79151225291"
                    msg = u"Здравствуйте, посылка с вашим заказом выслана. Номер отправления: %s Отследить посылку можно на сайте emspost.ru С Уважением my-spy.ru" % newform.tracking_number
                    msg = urllib.urlencode({'msg': msg.encode('cp1251')})
                    req = urllib2.urlopen('http://sms48.ru/send_sms.php?login=%s&to=%s&%s&from=%s&check2=%s' % (login, phone, msg.encode('cp1251'), from_phone, md5(login + md5(password).hexdigest() + phone).hexdigest()) )
            newform.save()
            # Сохраняю форму используя объект корзины клиента
            formset = CartProductFormset(request.POST, instance=cart)
            if formset.is_valid():
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
                # Высчитываю сумму и скидку
                calc.subtotal(cartid)
            if form.cleaned_data['status'] == 'CASH_IN':
                if client_status == form.cleaned_data['status']:
                        pass
                else:
                    newcashflow = Cash()
                    last_balance = Cash.objects.all().latest('id')
                    if form.cleaned_data['delivery'] == 'EMS':
                        newcashflow.cashflow = client.subtotal + 300
                        newcashflow.balance = last_balance.balance + client.subtotal + 300
                        newcashflow.comment = client.id
                    elif form.cleaned_data['delivery'] == 'COURIER':
                        newcashflow.cashflow = client.subtotal - 300
                        newcashflow.balance = last_balance.balance + client.subtotal - 300
                        newcashflow.comment = client.id
                    else:
                        newcashflow.cashflow = client.subtotal
                        newcashflow.balance = last_balance.balance + client.subtotal
                        newcashflow.comment = client.id
                    newcashflow.cause = 'FROM_CLIENT'
                    newcashflow.type = 'ENCASH'
                    newcashflow.save()
                    balance = Balance.objects.get(id=1)
                    balance.encash += newcashflow.cashflow
                    balance.total = balance.encash + balance.webmoney + balance.yandex
                    balance.save()
            else:
                if client_status == 'CASH_IN':
                    cashflow = Cash.objects.get(comment=client.id)
                    cashflows_recalc = Cash.objects.filter(pk__gt=cashflow.id).reverse()
                    true_balance = cashflow.balance - cashflow.cashflow
                    cashflow.delete()
                    for cashflow_recalc in cashflows_recalc:
                        cashflow_recalc.balance = true_balance + cashflow_recalc.cashflow
                        true_balance = cashflow_recalc.balance
                        cashflow_recalc.save()
                    balance = Balance.objects.get(id=1)
                    balance.encash -= cashflow.cashflow
                    balance.total = balance.encash + balance.webmoney + balance.yandex
                    balance.save()
        else:
            formset = CartProductFormset(instance=cart)
            return render_to_response("myadmin/sale/client_form.html", locals(), context_instance=RequestContext(request))
    # Создаю формы
    CartProductFormset = inlineformset_factory(CartItem, CartProduct, formset=BaseProductFormset, extra=1)
    formset = CartProductFormset(instance=cart)
    client = Client.objects.get(id=id)
    form = ClientForm(instance=client, prefix='client')
    return render_to_response("myadmin/sale/client_form.html", locals(), context_instance=RequestContext(request))

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
def cash(request, when):
    today = date.today()
    balance = Balance.objects.get(id=1)
    if when == 'today':
        cash = Cash.objects.filter(date__year=today.year, date__month=today.month, date__day=today.day)
    elif when == 'week':
        monday, sunday = week_boundaries(today.year, int(today.strftime("%W")))
        cash = Cash.objects.filter(date__year=today.year, date__month=today.month, date__range=(monday, sunday))
    elif when == 'month':
        cash = Cash.objects.filter(date__year=today.year, date__month=today.month)
    elif when == 'year':
        cash = Cash.objects.filter(date__year=today.year)
    else:
        cash = Cash.objects.filter(date__year=when[-4:], date__month=when[:-4])
    cash_in = 0
    cash_out = 0
    for i in cash:
        if i.cashflow > 0:
            cash_in += i.cashflow
        else:
            cash_out -= i.cashflow
    cash_all = cash_in + cash_out
    return render_to_response("myadmin/cash/cash.html", locals(), context_instance=RequestContext(request))

@login_required
def add_cashflow(request):
    if request.method == 'POST':
        last_balance = Cash.objects.all().latest('id')
        form = CashForm(request.POST)
        newform = form.save(commit=False)
        balance = Balance.objects.get(id=1)
        if newform.type == 'ENCASH':
            balance.encash += newform.cashflow
            newform.balance = last_balance.balance + newform.cashflow
            balance.total = balance.encash + balance.webmoney + balance.yandex
        elif newform.type == 'WEBMONEY':
            balance.webmoney += newform.cashflow
            newform.balance = last_balance.balance
            balance.total = balance.encash + balance.webmoney + balance.yandex
        elif newform.type == 'YANDEX':
            balance.yandex += newform.cashflow
            newform.balance = last_balance.balance
            balance.total = balance.encash + balance.webmoney + balance.yandex
        balance.save()
        newform.save()
    form = CashForm()
    return render_to_response("myadmin/cash/edit_cashflow.html", locals(), context_instance=RequestContext(request))

@login_required
def edit_cashflow(request, id):
    cash = Cash.objects.get(id=id)
    last_cashflow = cash.cashflow
    last_type = cash.type
    form = CashForm(instance=cash)
    if request.method == 'POST':
        form = CashForm(request.POST, instance=cash)
        newform = form.save(commit=False)
        if not last_cashflow == newform.cashflow:
            balance = Balance.objects.get(id=1)
            if last_type == 'ENCASH':
                balance.encash -= last_cashflow
                cashflow_diff = newform.cashflow - last_cashflow
                newform.balance = newform.balance + cashflow_diff
                cashflows_recalc = Cash.objects.filter(pk__gt=cash.id).reverse()
                true_balance = cash.balance
                for cashflow_recalc in cashflows_recalc:
                    if cashflow_recalc.type == 'ENCASH':
                        cashflow_recalc.balance = true_balance + cashflow_recalc.cashflow
                        true_balance = cashflow_recalc.balance
                        cashflow_recalc.save()
                    else:
                        cashflow_recalc.balance = true_balance
                        cashflow_recalc.save()
            elif last_type == 'YANDEX':
                balance.yandex -= last_cashflow
            elif last_type == 'WEBMONEY':
                balance.webmoney -= last_cashflow
            if newform.type == 'ENCASH':
                balance.encash += newform.cashflow
                if not last_type == newform.type:
                    newform.balance = newform.cashflow + newform.balance
                    true_balance = cash.balance
                    cashflows_recalc = Cash.objects.filter(pk__gt=cash.id).reverse()
                    for cashflow_recalc in cashflows_recalc:
                        if cashflow_recalc.type == 'ENCASH':
                            cashflow_recalc.balance = true_balance + cashflow_recalc.cashflow
                            true_balance = cashflow_recalc.balance
                            cashflow_recalc.save()
                        else:
                            cashflow_recalc.balance = true_balance
                            cashflow_recalc.save()
            elif newform.type == 'YANDEX':
                balance.yandex += newform.cashflow
            elif newform.type == 'WEBMONEY':
                balance.webmoney += newform.cashflow
            balance.total = balance.encash + balance.webmoney + balance.yandex
            balance.save()
        elif not last_type == newform.type:
            balance = Balance.objects.get(id=1)
            if last_type == 'ENCASH':
                balance.encash -= last_cashflow
                newform.balance = newform.balance - newform.cashflow
                true_balance = cash.balance
                cashflows_recalc = Cash.objects.filter(pk__gt=cash.id).reverse()
                for cashflow_recalc in cashflows_recalc:
                    if cashflow_recalc.type == 'ENCASH':
                        cashflow_recalc.balance = true_balance + cashflow_recalc.cashflow
                        true_balance = cashflow_recalc.balance
                        cashflow_recalc.save()
                    else:
                        cashflow_recalc.balance = true_balance
                        cashflow_recalc.save()
            elif last_type == 'YANDEX':
                balance.yandex -= last_cashflow
            elif last_type == 'WEBMONEY':
                balance.webmoney -= last_cashflow
            if newform.type == 'ENCASH':
                balance.encash += newform.cashflow
                newform.balance = newform.cashflow + newform.balance
                true_balance = cash.balance
                cashflows_recalc = Cash.objects.filter(pk__gt=cash.id).reverse()
                for cashflow_recalc in cashflows_recalc:
                    if cashflow_recalc.type == 'ENCASH':
                        cashflow_recalc.balance = true_balance + cashflow_recalc.cashflow
                        true_balance = cashflow_recalc.balance
                        cashflow_recalc.save()
                    else:
                        cashflow_recalc.balance = true_balance
                        cashflow_recalc.save()
            elif newform.type == 'YANDEX':
                balance.yandex += newform.cashflow
            elif newform.type == 'WEBMONEY':
                balance.webmoney += newform.cashflow
            balance.total = balance.encash + balance.webmoney + balance.yandex
            balance.save()
        newform.save()
    return render_to_response("myadmin/cash/edit_cashflow.html", locals(), context_instance=RequestContext(request))

@login_required
def edit_balance(request):
    if request.method == 'POST':
        form = BalanceForm(request.POST)
        if form.is_valid():
            balance = Balance.objects.get(id=1)
            if form.cleaned_data['from_type'] == 'ENCASH':
                balance.encash -= form.cleaned_data['amount']
            elif form.cleaned_data['from_type'] == 'YANDEX':
                balance.yandex -= form.cleaned_data['amount']
            elif form.cleaned_data['from_type'] == 'WEBMONEY':
                balance.webmoney -= form.cleaned_data['amount']
            if form.cleaned_data['to_type'] == 'ENCASH':
                balance.encash += form.cleaned_data['amount']
            elif form.cleaned_data['to_type'] == 'YANDEX':
                balance.yandex += form.cleaned_data['amount']
            elif form.cleaned_data['to_type'] == 'WEBMONEY':
                balance.webmoney += form.cleaned_data['amount']
            balance.total = balance.encash + balance.webmoney + balance.yandex
            balance.save()
    form = BalanceForm()
    return render_to_response("myadmin/cash/edit_balance.html", locals(), context_instance=RequestContext(request))
