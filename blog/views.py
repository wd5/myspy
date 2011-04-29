from django.shortcuts import render_to_response
from django.template import RequestContext
from myspy.blog.models import Entry

def blog(request):
    entrys = Entry.objects.all()
    return render_to_response("blog/main.html", locals(), context_instance=RequestContext(request))
