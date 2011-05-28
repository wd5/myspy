          # -*- coding: utf-8 -*-
from datetime import date, timedelta
from django.shortcuts import render_to_response
from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from cart.models import Client, CartItem, CartProduct
from forms import ClientForm, BaseProductFormset, CashForm, BalanceForm, TaskForm, TaskAnswerForm, OrderForm
from django.forms.models import inlineformset_factory
from cart.cart import _generate_cart_id
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from catalog.models import Product
from models import Cash, Balance, Waytmoney, Task, TaskAnswer, TaskFile, Order
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.contrib.auth.models import User
from madmin_func import clients_list, client_sms, update_store, subtotal, update_cash, cash_list
from settings import *

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

@login_required
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
    # Ожидаемое количество денег
    money = Waytmoney.objects.get(id=1).wayt_money
    # Применяю фильтр по статусам
    if request.method == 'POST':
        # Выбранные статусы
        statuses = []
        # Клиенты соответсвующие статусам
        clients = []
        for status in request.POST.getlist('status'):
            statuses.append(status)
            clients += Client.objects.filter(status=status)
        # Сортирую по id - так чтобы последний клиент был сверху
        clients.sort(key=lambda x: x.id, reverse=True)
    else:
        # Список клиентов за запрошеный период
        clients = clients_list(when)
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
                subtotal(cart.id)
            else:
                pass
            # После создания клиента тут же перекидываю на редактирование клиента
            return HttpResponseRedirect(reverse('myadmin.views.edit_client', args=(client.id,)))
    return render_to_response("myadmin/sale/client_form.html", locals(), context_instance=RequestContext(request))

@login_required
def delete_client(request, id):
    # УДаляю клиента
    client = Client.objects.get(id=id)
    cart_id = client.cart.id
    client.delete()
    # Уляляю корзину клиента
    cart = CartItem.objects.get(id=cart_id)
    cart.delete()
    return HttpResponseRedirect('/myadmin/sales/all')

@login_required
def edit_client(request, id):
    # Получаю нужные данные для работы с формами
    client = Client.objects.get(id=id)
    cartid = client.cart.id
    cart = CartItem.objects.get(id=cartid)
    CartProductFormset = inlineformset_factory(CartItem, CartProduct, formset=BaseProductFormset, extra=1)
    if request.method == 'POST':
        # Получаю предыдущие статусы клиента
        client_status = client.status
        sms_status = client.sms_status
        # Сохраняю форму используя объект клиента
        form = ClientForm(request.POST, instance=client, prefix='client')
        if form.is_valid():
            newform = form.save(commit=False)
            # Сохраняю в базе последнего пользователя редактирующего клиента
            newform.last_user = request.user.first_name
            # Отправляю смс клиенту
            if SEND_SMS:
                if newform.sms_status:
                    if not sms_status:
                        client_sms(newform)
            newform.save()
            # Сохраняю форму используя объект корзины клиента
            formset = CartProductFormset(request.POST, instance=cart)
            if formset.is_valid():
                # Получаю список покупок клиента
                products = CartProduct.objects.filter(cartitem=cart)
                # Обновляю количество товара на складе
                update_store(formset.cleaned_data, products)
                formset.save()
                # Высчитываю сумму и скидку
                subtotal(cartid)
            # Обновляю баланс
            update_cash(form.cleaned_data, client, client_status)
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
    balance = Balance.objects.get(id=1)
    cash = cash_list(when)
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
                last_balance = Cash.objects.all().latest('id')
                cash = Cash()
                cash.cashflow = -form.cleaned_data['amount']
                cash.balance = last_balance.balance - form.cleaned_data['amount']
                cash.cause = "OTHER"
                cash.type = "ENCASH"
                if form.cleaned_data['to_type'] == 'YANDEX':
                    cash.comment = "На яндекс деньги"
                elif form.cleaned_data['to_type'] == 'WEBMONEY':
                    cash.comment = "На webmoney"
            elif form.cleaned_data['from_type'] == 'YANDEX':
                balance.yandex -= form.cleaned_data['amount']
            elif form.cleaned_data['from_type'] == 'WEBMONEY':
                balance.webmoney -= form.cleaned_data['amount']
            if form.cleaned_data['to_type'] == 'ENCASH':
                balance.encash += form.cleaned_data['amount']
            elif form.cleaned_data['to_type'] == 'YANDEX':
                balance.yandex += form.cleaned_data['amount']
                cash.save()
            elif form.cleaned_data['to_type'] == 'WEBMONEY':
                balance.webmoney += form.cleaned_data['amount']
                cash.save()
            balance.total = balance.encash + balance.webmoney + balance.yandex
            balance.save()
    form = BalanceForm()
    return render_to_response("myadmin/cash/edit_balance.html", locals(), context_instance=RequestContext(request))

@login_required
def tasks(request):
    tasks = Task.objects.filter(is_done=False)
    return render_to_response("myadmin/tasks/tasks.html", locals(), context_instance=RequestContext(request))

@login_required
def add_task(request):
    form = TaskForm()
    TaskFileFormset = inlineformset_factory(Task, TaskFile, extra=1)
    task = Task()
    formset = TaskFileFormset()
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            task.user = request.user.username
            task.save()
            formset = TaskFileFormset(request.POST, request.FILES, instance=task)
            if formset.is_valid():
                formset.save()
            url = urlresolvers.reverse('tasks-page')
            mails = []
            for user in task.performers.all().exclude(username=request.user):
                mails.append(user.email)
            if mails:
                send_mail(u'%s добавил задание для вас' % request.user.first_name, 'http://my-spy.ru/myadmin/tasks/%i/' % task.id, 'info@my-spy.ru', mails)
            return HttpResponseRedirect(url)
    return render_to_response("myadmin/tasks/add_task.html", locals(), context_instance=RequestContext(request))

@login_required
def task(request, id):
    task = Task.objects.get(pk=id)
    answers = TaskAnswer.objects.filter(task=task)
    if request.method == 'POST':
        form = TaskAnswerForm(request.POST, request.FILES)
        if form.is_valid():
            newform = form.save(commit=False)
            newform.task = task
            newform.user = request.user.username
            newform.save()
            mails = []
            for user in task.performers.all().exclude(username=request.user):
                mails.append(user.email)
            if mails:
                send_mail(u'%s добавил ответ в заданиe' % request.user.first_name, 'http://my-spy.ru/myadmin/tasks/%i/' % task.id, 'info@my-spy.ru', mails)
    form = TaskAnswerForm()
    return render_to_response("myadmin/tasks/task.html", locals(), context_instance=RequestContext(request))

@login_required
def edit_task(request, id):
    task = Task.objects.get(pk=id)
    form = TaskForm(instance=task)
    TaskFileFormset = inlineformset_factory(Task, TaskFile, extra=1)
    formset = TaskFileFormset(instance=task)
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
        formset = TaskFileFormset(request.POST, request.FILES, instance=task)
        if formset.is_valid():
            formset.save()
        url = urlresolvers.reverse('tasks-page')
        return HttpResponseRedirect(url)
    return render_to_response("myadmin/tasks/add_task.html", locals(), context_instance=RequestContext(request))

@login_required
def task_done(request, id):
    task = Task.objects.get(pk=id)
    task.is_done = True
    task.save()
    return HttpResponseRedirect(urlresolvers.reverse(tasks))

@login_required
def delete_task(request, id):
    task = Task.objects.get(pk=id)
    task.delete()
    return HttpResponseRedirect(urlresolvers.reverse(tasks))

@login_required
def show_taskdone(request):
    tasks = Task.objects.filter(is_done=True)
    return render_to_response("myadmin/tasks/tasks.html", locals(), context_instance=RequestContext(request))

@login_required
def my_tasks(request):
    tasks = Task.objects.filter(performers=request.user).exclude(is_done=True)
    return render_to_response("myadmin/tasks/tasks.html", locals(), context_instance=RequestContext(request))

@login_required
def myown_tasks(request):
    tasks = Task.objects.filter(user=request.user)
    return render_to_response("myadmin/tasks/tasks.html", locals(), context_instance=RequestContext(request))

@login_required
def orders(request):
    orders = Order.objects.all().exclude(is_done=True)
    return render_to_response("myadmin/orders/orders.html", locals(), context_instance=RequestContext(request))

@login_required
def add_order(request):
    form = OrderForm()
    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES)
        if form.is_valid():
            newform = form.save(commit=False)
            newform.user = request.user
            newform.save()
            users = User.objects.all().exclude(username=request.user)
            mails = []
            for user in users:
                mails.append(user.email)
            send_mail(u'%s добавил заказ' % request.user.first_name, 'http://my-spy.ru/myadmin/orders/%i/' % newform.id, 'info@my-spy.ru', mails)
            return HttpResponseRedirect(urlresolvers.reverse(orders))
    return render_to_response("myadmin/orders/order_form.html", locals(), context_instance=RequestContext(request))

@login_required
def order(request, id):
    order = Order.objects.get(id=id)
    return render_to_response("myadmin/orders/order.html", locals(), context_instance=RequestContext(request))

@login_required
def edit_order(request, id):
    order = Order.objects.get(pk=id)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES, instance=order)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(urlresolvers.reverse(orders))
    return render_to_response("myadmin/orders/order_form.html", locals(), context_instance=RequestContext(request))

@login_required
def show_orderdone(request):
    orders = Order.objects.filter(is_done=True)
    return render_to_response("myadmin/orders/orders.html", locals(), context_instance=RequestContext(request))

@login_required
def delete_order(request, id):
    order = Order.objects.get(pk=id)
    order.delete()
    return HttpResponseRedirect(urlresolvers.reverse(orders))

@login_required
def order_done(request, id):
    order = Order.objects.get(pk=id)
    order.is_done = True
    order.save()
    return HttpResponseRedirect(urlresolvers.reverse(orders))
