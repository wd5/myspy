          # -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render_to_response
from django.http import Http404
from django.core import urlresolvers
from django.template import RequestContext
from catalog.models import Category, Product, Section
from django.http import HttpResponseRedirect, HttpResponse
from cart import cart, settings
from django.core.mail import send_mail
import threading

def index(request):
    page_title = "Магазин домашней безопасности, шпионская техника"
    meta_keywords = """шпионские штучки магазин, шпионские штучки купить, купить подслушивающее устройство,
     шпионская техника, шпионские камеры, шпионское оборудование продажа, магазин шпионских товаров,
      шпионские устройства, шпионские штучки, жучки для прослушки купить, прослушивающее устройство,
       продажа жучков, жучок для прослушки"""
    meta_description = """Интернет магазин, где можно купить шпионские штучки, камеры,
     подслушивающие устройства. Так же у нас в продаже шпионская техника, оборудование,
      глушилка мобильных телефонов, мини камера."""
    sections = Section.objects.filter(is_active=True)
    return render_to_response("main/index.html", locals(), context_instance=RequestContext(request))

def show_category(request, category_slug):
    if request.method == 'POST':
        cart.add_to_cart(request)
        url = urlresolvers.reverse('show_cart')
        return HttpResponseRedirect(url)
    else:
        try:
            category = Category.objects.get(slug=category_slug)
            products = category.product_set.filter(is_active=True).order_by('categoryproduct__position')
            if category.section.name == category.name:
                page_title = "%s" % category.section
            else:
                page_title = "%s %s" % (category.section, category)
            meta_keywords = category.meta_keywords
            meta_description = category.meta_descriotion
        except :
            section = get_object_or_404(Section, slug=category_slug)
            category = section.category_set.filter(is_active=True)
            page_title = "%s" % section
            products = []
            for cat in category:
                products += cat.product_set.filter(is_active=True).order_by('categoryproduct__position')
        if category_slug == 'antibugs':
            page_title += ': блокираторы сотовой связи(сотовых телефонов), обнаружители камер'
            meta_description = "блокиратор сотовой связи сотовых телефонов, обнаружитель камер"
            meta_keywords = "Блокиратор сотовой связи, блокиратор сотовых телефонов, обнаружитель камер от интернет-магазина my-spy.ru"
        elif category_slug == 'audio':
            page_title = 'Миниатюрные диктофоны, цифровые мини диктофоны – my-spy.ru'
            meta_description = "Мини диктофоны с радиусом слышимости от 9 до 20 метров и со временем работы в режиме записи  от 4 до 300 часов"
            meta_keywords = "миниатюрный диктофон мини диктофоны цифровые edic mini"
        elif category_slug == 'jammers':
            page_title = 'Глушилки, подавители сотовых телефонов и сотовой связи'
            meta_description = "Нужен подавить сигнал сотовой связи? Глушилки и подавители сотовых телефонов с радиусом действия от 1 до 40 метров"
            meta_keywords = "глушилка сотовых телефонов подавитель"
    return render_to_response("main/catalog.html", locals(), context_instance=RequestContext(request))

def show_product(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    if not product.is_active:
        raise Http404
    photos = product.productphoto_set.all()
    features = product.feature_set.all()
    if request.method == 'POST':
        postdata = request.POST.copy()
        if 'product_slug' in postdata:
            cart.add_to_cart(request)
            url = urlresolvers.reverse('show_cart')
            return HttpResponseRedirect(url)
    page_title = "%s - my-spy.ru" % product.name
    meta_keywords = page_title
    meta_description = "%s - %s" % (page_title, product.mini_html_description)
    if product_slug == "808a":
        page_title = "Глушилка GSM сигнала 808А - my-spy.ru"
        meta_keywords = "глушилка gsm сигнала"
        meta_description = "Глушилка GSM сигнала 808А отлично справляется с задачей подавления сотовых телефонов, а также GSM жучков"
    elif product_slug == '808kb':
        page_title = "GPS глушилка  808KB - my-spy.ru"
        meta_keywords = "глушилка gps глушилки"
        meta_description = "Глушилка GPS сигнала 808KB поможет в том случае, если хотите защитить от слежения Вашей машины через спутник"
    elif product_slug == 'gm980':
        page_title = "Прослушка на расстоянии с радио жучком GM980 - my-spy.ru"
        meta_keywords = "прослушка на расстоянии прослушивающие устройства"
        meta_description = "Прослушка на расстоянии с помощью радио жучка GM980. Жучок передает звук на расстояние до 500 метров в условиях города и до 7 км на открытом пространстве"
    return render_to_response("main/tovar.html", locals(), context_instance=RequestContext(request))

def all_goods(request):
    if request.method == 'POST':
        cart.add_to_cart(request)
        url = urlresolvers.reverse('show_cart')
        return HttpResponseRedirect(url)
    products = Product.objects.filter(is_active=True)
    page_title = "my-SPY - Все товары"
    meta_keywords = page_title
    return render_to_response("main/catalog.html", locals(), context_instance=RequestContext(request))

def about(request):
    page_title = "О нас"
    return render_to_response('main/about.html', locals(), context_instance=RequestContext(request))

def delivery(request):
    page_title = "Доставка и оплата"
    return render_to_response('main/delivery.html', locals(), context_instance=RequestContext(request))

def take_vk_comment(request):
    if request.method == 'POST':
        param = request.POST['comment']
        if settings.SEND_ADMIN_EMAIL:
            t = threading.Thread(target= send_mail, args=[
              u'Новый комментарий',
              u'%s' % param, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], 'fail_silently=False'])
            t.setDaemon(True)
            t.start()
    return HttpResponse()
