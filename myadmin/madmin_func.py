          # -*- coding: utf-8 -*-
from cart.models import Client, CartProduct
from datetime import date, timedelta
import re, urllib, urllib2
from hashlib import md5
import decimal
from catalog.models import Product
from settings import *
from models import Cash, Balance

# Возвращает число понедельника и воскресенья текущей недели
def week_boundaries(year, week):
    start_of_year = date(year, 1, 1)
    now = start_of_year + timedelta(weeks=week)
    mon = now - timedelta(days=now.weekday())
    sun = mon + timedelta(days=6)
    return mon, sun

# Список клиентов за запрошенный период времени
def clients_list(when):
        today = date.today()
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
        return clients

# Список денежных поток за запрошенный период времени
def cash_list(when):
    today = date.today()
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
    return cash

# Отправка смс с tracking number клиенту
def client_sms(newform):
    login = 'palv1@yandex.ru'
    password = '97ajhJaj9zna'
    phone = re.sub("\D", "", newform.phone)
    from_phone = "79151225291"
    msg = u"Здравствуйте, посылка с вашим заказом выслана. Номер отправления: %s Отследить посылку можно на сайте emspost.ru С Уважением my-spy.ru" % newform.tracking_number
    msg = urllib.urlencode({'msg': msg.encode('cp1251')})
    urllib2.urlopen('http://sms48.ru/send_sms.php?login=%s&to=%s&%s&from=%s&check2=%s' % (login, phone, msg.encode('cp1251'), from_phone, md5(login + md5(password).hexdigest() + phone).hexdigest()) )

# Обновляет количество товара на складе
def update_store(data, products):
    # Предыдущий список товара
    products_name = []
    for product in products:
        products_name.append(product.product)
    # Текущий список товара
    newproducts_name = []
    for formitem in data:
        if formitem:
            print formitem
            product_name = formitem['product']
            quantity = formitem['quantity']
            # Обновление в случае удаления товара
            if formitem['DELETE']:
                store_product = Product.objects.get(name=product_name)
                store_product.quantity += quantity
                store_product.save()
            else:
                # Обновляю если у клиента еще нет товаров
                if not products:
                    store_product = Product.objects.get(name=product_name)
                    store_product.quantity -= quantity
                    store_product.save()
                else:
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
                                store_product.quantity -= store_quantity
                                store_product.save()
                # Если добавился товар
                if product_name not in products_name:
                    # Изменяю количество на складе
                    store_product = Product.objects.get(name=product_name)
                    store_product.quantity -= quantity
                    store_product.save()
                # Обновляю текущий список товара
                newproducts_name.append(product_name)
    # Сравниваю передыдущий список товара с текущим
    for product in products:
        # Если из предыдущего исчез товар
        if product.product not in newproducts_name:
            # Возвращаю его на склад
            store_product = Product.objects.get(name=product.product)
            store_product.quantity += product.quantity
            store_product.save()

# Высчитывает сумму и скидку
def subtotal(cartid):
    products = CartProduct.objects.filter(cartitem=cartid)
    cart_total = decimal.Decimal('0.00')
    cart_discount_total = 0
    discount = 0
    discount_quantity = 0
    for item in products:
        # Если на товар действует скидка
        if item.product.is_discount:
            # Высчитываю количество скидочных товаров
            discount_quantity += item.quantity
            # Общая стоимость скидочных товаров
            cart_discount_total += item.product.price * item.quantity
        # Общая стомость товаров без скидки
        cart_total += item.product.price * item.quantity
    # Если в настройках задана скидка то высчитываю
    if DISCOUNT:
        # Если товаров достаточно для скидки
        if discount_quantity >= COUNT_FOR_DISCOUNT:
            # Высчитываю скидку
            discount = (cart_discount_total * DISCOUNT_PERCENT)/100
        # Если скидочных товаров достсточно для скидки
        elif len(products) >= COUNT_FOR_DISCOUNT:
            # Высчитываю скидку
            discount = (cart_discount_total * DISCOUNT_PERCENT)/100
        cart_total -= discount
    ci = Client.objects.get(cart=cartid)
    ci.subtotal = cart_total
    ci.discount = discount
    ci.save()

def update_cash(data, client, client_status):
    # Если статус деньги внесены
    if data['status'] == 'CASH_IN':
        # Если предыдущий статус такой же, то ничего не делать
        if client_status == data['status']:
            pass
        # Если предыдущий статус был другой
        else:
            # Создаю денежный поток
            newcashflow = Cash()
            # Последний баланс
            last_balance = Cash.objects.all().latest('id')
            # Если доставка EMS
            if data['delivery'] == 'EMS':
                # Добавляю к стоимости 300 рублей
                newcashflow.cashflow = client.subtotal + EMS
                newcashflow.balance = last_balance.balance + client.subtotal + EMS
                newcashflow.comment = client.id
            # Если доставка курьером
            elif data['delivery'] == 'COURIER':
                # Вычитаю из стоимости 300 рублей
                newcashflow.cashflow = client.subtotal - COURIER
                newcashflow.balance = last_balance.balance + client.subtotal - COURIER
                newcashflow.comment = client.id
            else:
                # Бесплатная доставка
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
        # Если был изменен статус деньги внесены
        if client_status == 'CASH_IN':
            # Удаляю денежный поток и пересчитываю баланс
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
