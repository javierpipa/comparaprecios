from django.core.management.base import BaseCommand
from django.db.models import Count, Sum
from django.core.exceptions import ObjectDoesNotExist
from precios.models import (
    Settings,
    Site, 
    Pages, 
    Campos,
    CamposEnSitio,
    SiteURLResults,
    SELECTOR,
    DONDESEUSA,
    PAGECRAWLER,
    SelectorCampo,

)
import pytz
utc=pytz.UTC

import requests
from bs4 import BeautifulSoup
from lxml import etree
import re

from datetime import date
from datetime import datetime, timedelta

import urllib.parse

from precios.pi_functions import (
    loadProductBeautifulSoup, 
    set_headers,
    getCampoDef,
    click_element
)
from precios.pi_get import (
    url_get, 
    getSiteProperties, 
    set_browser
)    

class Command(BaseCommand):
    help = "Start the simulation"

    def __init__(self):
        super().__init__()
        self.links = []
    

    def add_arguments(self, parser):
        default_num_urls = int(Settings.objects.get(key='Get_Beautiful_default_num_urls').value)
        parser.add_argument('SiteId', type=int, help='Id of VM to get info')
        parser.add_argument('numrecords', nargs='?', type=int, default=default_num_urls,
                    help='the bar to %(prog)s (default: %(default)s)')
        parser.add_argument('startrecord', nargs='?', type=int, default=0)
        parser.add_argument('all', nargs='?', type=bool, default=False,
                    help='the bar to %(prog)s (default: %(default)s)')

    def handle(self, *args, **options):
        SiteId = options["SiteId"]
        numRecords = options["numrecords"]
        startRecord = options["startrecord"]
        if startRecord > 0:
            numRecords = startRecord + numRecords

        self.headers = set_headers()
        dias_viejo = int(Settings.objects.get(key='diasActualizado').value)
        all = options["all"]

        sites = Site.objects.filter(id=SiteId)

        if not all:
            today = utc.localize(datetime.today()) - timedelta(days=dias_viejo)
        else:
            today = utc.localize(datetime.today()) + timedelta(days=1)

        
        for site in sites:
            ### Get Site Info
            if site.agregaSiteURL:
                url_suffix = site.siteURL
            else:
                url_suffix = ""

            print(f'Empresa = {site.siteName}')
            
            # siteclicks = getCampoDef('mayordeedad',site)
            ## Error 404
            # arr_campo404 = getCampoDef('Pagina404',site)
            # listaDeCampos  =  Campos.objects.filter(donde=DONDESEUSA.EN_PRODUCTO)
            # campoEnSitioObject = CamposEnSitio.objects.filter(site=site, campo__in=listaDeCampos, enabled=True)
            
            listaURLS = SiteURLResults.objects.filter(
                site=site, 
                # error404=False,
                updated__lte=today
                 ).order_by('updated')[startRecord:numRecords]

            
            urlCount = 0
            
            # siteclicks, arr_campo404, listaDeCampos, campoEnSitioObject = getSiteProperties(site)
            siteclicks, \
                arr_campo404, \
                listaDeCampos, \
                campoEnSitioObject, \
                arr_linksSelector, \
                ItemsEnListado,\
                arr_nextPage, \
                arr_maxPages = getSiteProperties(site)

            for laurl in listaURLS:
                url = urllib.parse.unquote(laurl.url)

                urlCount = urlCount + 1
                startTime = datetime.now()
                
                try:
                    page2 = requests.get(url, self.headers, timeout=4.50)
                except requests.HTTPError:
                    laurl.error404 = True
                    laurl.save()
                    continue
                except:
                    laurl.error404 = True
                    laurl.save()
                    continue
                soup2 = BeautifulSoup(page2.content, "html.parser")

                     
                url_get(soup2, 
                    url, 
                    laurl, 
                    arr_campo404, 
                    siteclicks, 
                    campoEnSitioObject, 
                    site, 
                    urlCount, 
                    numRecords, 
                    startRecord
                )

            site.save()
        print("Fin de la ejecucion")