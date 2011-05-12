          # -*- coding: utf-8 -*-
from models import CartItem, Client, CartProduct
from catalog.models import *
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
import threading, urllib2, urllib
from hashlib import md5
import decimal
import random
import settings, re

CART_ID_SESSION_KEY = 'cart_id'

def _cart_id(request):
    """ get the current user's cart id, sets new one if blank;
    Note: the syntax below matches the text, but an alternative,
    clearer way of checking for a cart ID would be the following:

    if not CART_ID_SESSION_KEY in request.session:

    """
    if request.session.get(CART_ID_SESSION_KEY,'') == '':
        request.session[CART_ID_SESSION_KEY] = _generate_cart_id()
    return request.session[CART_ID_SESSION_KEY]

def _generate_cart_id():
    """ function for generating random cart ID values """
    cart_id = ''
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()'
    cart_id_length = 50
    for y in range(cart_id_length):
        cart_id += characters[random.randint(0, len(characters)-1)]
    return cart_id

def get_cart_items(request):
    """ return all items from the current user's cart """
    #return CartItem.objects.filter(cart_id=_cart_id(request))
    try:
        cartid = CartItem.objects.get(cart_id = _cart_id(request))
        return CartProduct.objects.filter(cartitem__id__iexact=cartid.id)
    except :
        return False

def add_to_cart(request):
    postdata = request.POST.copy()
    # Получаю название заказанного продукта
    product_slug = postdata.get('product_slug','')
    quantity = 1
    product_in_cart = False
    # Получаю заказанный продукт
    p = get_object_or_404(Product, slug=product_slug)
    # Если клиент уже есть в базе
    if CartItem.objects.filter(cart_id = _cart_id(request)):
        # Получаю все продукты в корзине
        cart = CartItem.objects.get(cart_id = _cart_id(request))
        cart_products = CartProduct.objects.filter(cartitem=cart.id)
        # Проверяю есть ли такой продукт уже в корзине
        for cart_item in cart_products:
            if cart_item.product_id == p.id:
                # Если уже есть то обновляю количество
                ttt = CartProduct.objects.get(cartitem=cart,product=p.id)
                ttt.augment_quantity(quantity)
                product_in_cart = True
        # Если нету то добавляю
        if not product_in_cart:
            cart = CartItem.objects.get(cart_id = _cart_id(request))
            cp = CartProduct(cartitem = cart, product = p)
            cp.save()
    # Если клиента нету в базе то создаю его
    else:
        ci = CartItem()
        ci.cart_id = _cart_id(request)
        ci.save()

        # И добавляю его заказ в корзину
        cart = CartItem.objects.get(cart_id = _cart_id(request))
        cp = CartProduct(cartitem = cart, product = p)
        cp.save()

# returns the total number of items in the user's cart
def cart_distinct_item_count(request):
    if CartItem.objects.filter(cart_id = _cart_id(request)):
        return get_cart_items(request).count()
    else:
        return 0

def get_single_item(request, item_id):
    return get_object_or_404(CartProduct, id=item_id)

# update quantity for single item
def update_cart(request):
    postdata = request.POST.copy()
    item_id = postdata['item_id']
    quantity = postdata['quantity']
    cart_item = get_single_item(request, item_id)
    if cart_item:
        if int(quantity) > 0:
            cart_item.quantity = int(quantity)
            cart_item.save()
        else:
            remove_from_cart(request)

# remove a single item from cart
def remove_from_cart(request):
    postdata = request.POST.copy()
    item_id = postdata['item_id']
    cart_item = get_single_item(request, item_id)
    if cart_item:
        cart_item.delete()

class Subtotal:
    def __init__(self, request):
        self.request = request
        self.discount = 0

    def subtotal(self):
        cart_total = decimal.Decimal('0.00')
        cart_discount_total = 0
        cart_products = get_cart_items(self.request)
        discount_quantity = 0
        for cart_item in cart_products:
            if cart_item.product.is_discount:
                discount_quantity += cart_item.quantity
                cart_discount_total += cart_item.product.price * cart_item.quantity
            cart_total += cart_item.product.price * cart_item.quantity
        if len(cart_products) >= 2:
            self.discount = (cart_discount_total * 10)/100
        elif discount_quantity >=2:
            self.discount = (cart_discount_total * 10)/100
        cart_total -= self.discount
        return cart_total

def save_client(request, form):
    cart = CartItem.objects.get(cart_id=_cart_id(request))
    subtotal_class = Subtotal(request)

    ci = Client()
    ci.cart = cart

    ci.name = form.cleaned_data['name']
    ci.surname = form.cleaned_data['surname']
    ci.patronymic = form.cleaned_data['patronymic']
    ci.city = form.cleaned_data['city']
    ci.postcode = form.cleaned_data['postcode']
    ci.phone = form.cleaned_data['phone']
    ci.address = form.cleaned_data['address']
    ci.email = form.cleaned_data['email']
    ci.subtotal = subtotal_class.subtotal()
    ci.discount = subtotal_class.discount
    ci.referrer = request.COOKIES.get('REFERRER', None)
    ci.save()
    # Обновляю количество на складе
    products = CartProduct.objects.filter(cartitem=cart)
    for product in products:
        store_product = Product.objects.get(name=product.product)
        store_product.quantity -= product.quantity
        store_product.save()

def send_admin_email(request, cart_items, form, cart_subtotal, discount):
    products_for_email = ""
    for item in cart_items:
        products_for_email += u"%s:%s шт  http://my-spy.ru%s\n" % (item.product.name,
                                          item.quantity, item.product.get_absolute_url())
    t = threading.Thread(target= send_mail, args=[
        u'Заказ от %s %s' % (form.cleaned_data['name'], form.cleaned_data['surname'] ),
        u'Имя: %s %s %s \nГород: %s\nИндекс: %s\nТелефон: %s\nАдрес: %s\nEmail: %s\n\n%s\nВсего на сумму: %s руб\nСкидка: %s руб\n\nПришел с: %s'
        % (form.cleaned_data['surname'], form.cleaned_data['name'], form.cleaned_data['patronymic'],
        form.cleaned_data['city'], form.cleaned_data['postcode'], form.cleaned_data['phone'],
        form.cleaned_data['address'], form.cleaned_data['email'], products_for_email, cart_subtotal, discount, request.COOKIES.get('REFERRER', None) ),
        settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], 'fail_silently=False'])
    t.setDaemon(True)
    t.start()

def send_client_email(cart_items, form, cart_subtotal):
    products_for_email = ""
    for item in cart_items:
        products_for_email += u"%s:%s шт  http://my-spy.ru%s\n" % (item.product.name,
                                          item.quantity, item.product.get_absolute_url())
    t = threading.Thread(target= send_mail, args=[
        u'Ваш заказ от my-spy',
        u'Здравствуйте %s,\n\nВы оформили у нас заказ на:\n%s\nВсего на сумму: %s руб\n\nВ ближайшее время наш менеджер с вами свяжется.\nС Уважением, my-spy.ru' %
        (form.cleaned_data['name'], products_for_email, cart_subtotal ),
        settings.EMAIL_HOST_USER, [form.cleaned_data['email']], 'fail_silently=False'])
    t.setDaemon(True)
    t.start()

def send_sms(cart_items, form):
    login = 'palv1@yandex.ru'
    password = '97ajhJaj9zna'
    phones = ["79151225291", "79267972292"]
    from_phone = re.sub("\D", "", form.cleaned_data['phone'])
    products = ""
    for item in cart_items:
        products += "%sx%s" % (item.product.slug, item.quantity)
    msg = "%s,%s %s %s %s %s" % (form.cleaned_data['city'], form.cleaned_data['name'], form.cleaned_data['surname'], form.cleaned_data['address'], form.cleaned_data['postcode'] ,products)
    msg = urllib.urlencode({'msg': msg.encode('cp1251')})
    for to_phone in phones:
        req = urllib2.urlopen('http://sms48.ru/send_sms.php?login=%s&to=%s&%s&from=%s&check2=%s' % (login, to_phone, msg.encode('cp1251'), from_phone, md5(login + md5(password).hexdigest() + to_phone).hexdigest()) )
        if not req:
            urllib2.urlopen('http://sms48.ru/send_sms.php?login=%s&to=%s&%s&from=%s&check2=%s' % (login, to_phone, msg.encode('cp1251'), '79151225291', md5(login + md5(password).hexdigest() + to_phone).hexdigest()) )

