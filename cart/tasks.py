# -*- coding: utf-8 -*-
import urllib2, urllib
from hashlib import md5
import re
from celery.task import task

@task(name="add")
def add(cart_items, form):
    # Высылает смс сообщение о покупке и покупателе
    login = 'palv1@yandex.ru'
    password = '97ajhJaj9zna'
    phones = ["79151225291"]
    from_phone = re.sub("\D", "", form.cleaned_data['phone'])
    products = ""
    for item in cart_items:
        products += "%sx%s" % (item.product.slug, item.quantity)
    if form.cleaned_data['postcode']:
        msg = "%s %s %s %s %s %s" % (form.cleaned_data['city'], form.cleaned_data['name'], form.cleaned_data['surname'], form.cleaned_data['address'], u"индекс:" + str(form.cleaned_data['postcode']) ,products)
    else:
        msg = "%s %s %s %s %s" % (form.cleaned_data['city'], form.cleaned_data['name'], form.cleaned_data['surname'], form.cleaned_data['address'], products)
    msg = urllib.urlencode({'msg': msg.encode('cp1251')})
    for to_phone in phones:
        if len(str(form.cleaned_data['phone'])) != 16:
            if form.cleaned_data['postcode']:
                msg = "%s %s %s %s %s %s %s" % (form.cleaned_data['city'], form.cleaned_data['name'], form.cleaned_data['surname'], form.cleaned_data['address'], u"индекс:" + str(form.cleaned_data['postcode']), u"тел:" + str(form.cleaned_data['phone']) ,products)
            else:
                msg = "%s %s %s %s %s %s" % (form.cleaned_data['city'], form.cleaned_data['name'], form.cleaned_data['surname'], form.cleaned_data['address'], u"тел:" + str(form.cleaned_data['phone']), products)
            msg = urllib.urlencode({'msg': msg.encode('cp1251')})
            urllib2.urlopen('http://sms48.ru/send_sms.php?login=%s&to=%s&%s&from=%s&check2=%s' % (login, to_phone, msg.encode('cp1251'), 'my-spy', md5(login + md5(password).hexdigest() + to_phone).hexdigest()) )
        else:
            urllib2.urlopen('http://sms48.ru/send_sms.php?login=%s&to=%s&%s&from=%s&check2=%s' % (login, to_phone, msg.encode('cp1251'), from_phone, md5(login + md5(password).hexdigest() + to_phone).hexdigest()) )
