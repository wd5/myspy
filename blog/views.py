          # -*- coding: utf-8 -*-
from datetime import datetime
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_object_or_404, render_to_response, get_list_or_404
from django.template import RequestContext
from blog.models import Entry, Category
from django.http import Http404

def blog(request):
    try:
        first_entry = Entry.objects.order_by()[0].date
    except IndexError:
        raise Http404
    entrys = get_list_or_404(Entry, date__range=(first_entry, datetime.now()))
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(entrys, 15)
    try:
        entrys = paginator.page(page)
    except (EmptyPage, InvalidPage) :
        entrys = paginator.page(paginator.num_pages)
    page_title = "Блог - Страница " + str(page)
    return render_to_response("blog/main.html", locals(), context_instance=RequestContext(request))

def archive(request, when):
    try:
        entrys = Entry.objects.filter(date__year=when[-4:], date__month=when[:-4])
    except ValueError:
        raise Http404
    if not entrys:
        raise Http404
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(entrys, 15)
    try:
        entrys = paginator.page(page)
    except (EmptyPage, InvalidPage) :
        entrys = paginator.page(paginator.num_pages)
    page_title = "Архив блога за " + str(when[:-4]) + "." + str(when[-4:]) + " - Страница " + str(page) + " - my-spy.ru"
    return render_to_response("blog/main.html", locals(), context_instance=RequestContext(request))

def entry(request, entry_slug):
    entry = get_object_or_404(Entry, slug=entry_slug)
    page_title = entry.title
    meta_keywords = entry.keywords
    meta_description = entry.description
    return render_to_response("blog/entry.html", locals(), context_instance=RequestContext(request))

def category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    entrys = get_list_or_404(Entry, category=category)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(entrys, 15)
    try:
        entrys = paginator.page(page)
    except (EmptyPage, InvalidPage) :
        entrys = paginator.page(paginator.num_pages)
    page_title = category.name.encode('utf-8') + " - Страница " + str(page)
    return render_to_response("blog/main.html", locals(), context_instance=RequestContext(request))
