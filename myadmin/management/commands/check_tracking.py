          # -*- coding: utf-8 -*-
import urllib
from django.core.management.base import BaseCommand
import urllib2, re, time
from BeautifulSoup import BeautifulSoup
from cart.models import Client

class Command(BaseCommand):
    def handle(self, *args, **options):
        clients = Client.objects.filter(status='POSTSENDED')
        for client in clients:
            if client.tracking_number:
                try:
                    url = 'http://www.russianpost.ru/resp_engine.aspx?Path=rp/servise/ru/home/postuslug/trackingpo'
                    values = {'BarCode' : client.tracking_number,
                              'CDAY' : '12', 'CMONTH' : '12', 'CYEAR' : '2011', 'PATHCUR' : 'rp/servise/ru/home/postuslug/trackingpo',
                              'PATHPAGE' : 'RP/INDEX/RU/Home/Search', 'PATHWEB' : 'RP/INDEX/RU/Home', 'searchsign' : '1'}
                    data = urllib.urlencode(values)
                    req = urllib2.Request(url, data)
                    response = urllib2.urlopen(req)
                except urllib2.HTTPError:
                    print "sleeep - except"
                    time.sleep(1200)
                    continue
                doc = response.read()
                soup = BeautifulSoup(''.join(doc))
                content = soup.findAll("table")[10]
                for i in str(content.find("tbody")).split("</tr>"):
                    try:
                        last_status = i.split("</td>")[1][4:] + " " + i.split("</td>")[3][4:] + " " + i.split("</td>")[4][4:]
                        client.tracking_status = last_status
                    except :
                        pass
                time.sleep(5)
