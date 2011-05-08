          # -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import urllib2, re

class Command(BaseCommand):
    def handle(self, *args, **options):
        response = urllib2.urlopen('http://www.emspost.ru/tracking/EA186667499RU')
        result = re.finditer(ur"<tr class=\"odd\"><td>(.+?)</tr>", response.read())
        for match in result:
            print match.group()

