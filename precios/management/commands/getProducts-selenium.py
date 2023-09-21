from django.core.management.base import BaseCommand

from precios.models import (
    Settings,
    Site, 
    SiteURLResults,
    PAGECRAWLER,
)

import pytz
utc=pytz.UTC

import time
from datetime import datetime, timedelta

import urllib.parse

from precios.pi_functions import (
    set_headers,
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

        default_num_urls = int(Settings.objects.get(key='Get_Selenium_default_num_urls').value)

        parser.add_argument('SiteId', type=int, help='Id of VM to get info')

        parser.add_argument('numrecords', nargs='?', type=int, default=default_num_urls,
                    help='the bar to %(prog)s (default: %(default)s)')
        parser.add_argument('startrecord', nargs='?', type=int, default=0)

        parser.add_argument('all', nargs='?', type=bool, default=False,
                    help='the bar to %(prog)s (default: %(default)s)')


    def handle(self, *args, **options):
        SiteId      = options["SiteId"]
        numRecords  = options["numrecords"]
        startRecord = options["startrecord"]
        if startRecord > 0:
            numRecords = startRecord + numRecords
            
        self.headers = set_headers()
        dias_viejo = int(Settings.objects.get(key='diasActualizado').value)
        all = options["all"]

        sites = Site.objects.filter(id=SiteId)
        

        if not all:
            comparaday = utc.localize(datetime.today()) - timedelta(days=dias_viejo)
        else:
            comparaday = utc.localize(datetime.today())
        

        recienindexed = utc.localize(datetime.today()) - timedelta(hours=1)
        for site in sites:
            if site.crawler != PAGECRAWLER.SELENIUM:
                print("Sitio NO se indexa con Selenium")
                continue
            urlCount = 0

            if site.agregaSiteURL:
                url_suffix = site.siteURL
            else:
                url_suffix = ""

            print(f'Empresa = {site.siteName}')

            browser = set_browser()
            # browser.implicitly_wait(10)

            browser.get(site.siteURL)
            time.sleep(1.5)
            
            # siteclicks, arr_campo404, listaDeCampos, campoEnSitioObject = getSiteProperties(site)
            siteclicks, \
                arr_campo404, \
                listaDeCampos, \
                campoEnSitioObject, \
                arr_linksSelector, \
                ItemsEnListado,\
                arr_nextPage, \
                arr_maxPages = getSiteProperties(site)

            listaURLS = SiteURLResults.objects.filter(
                site=site, 
                # error404=False,
                # updated__lte=comparaday
                ).order_by('updated')[startRecord:numRecords]

            for laurl in listaURLS:
                if not all:
                    if laurl.updated > comparaday:
                        # print("Al dia")
                        continue

                    if laurl.updated > recienindexed:
                        print(comparaday)
                        continue

                urlCount = urlCount + 1
                url = urllib.parse.unquote(laurl.url)
                
                url_get(browser, 
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

        browser.quit()
        print(f"Fin de la ejecucion Site={site}")

   
    