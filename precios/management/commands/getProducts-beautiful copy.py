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
    saveUrlData, 
    click_element
)

class Command(BaseCommand):
    help = "Start the simulation"

    def __init__(self):
        super().__init__()
        self.links = []
    
    def get_resultado(self, soup2, registro):
        selector            = registro['como']
        que_busca           = registro['que_busca']
        que_obtiene         = registro['que_obtiene']
        printit             = registro['printit']
        removeChars         = registro['removeChars']
        split_return_by     = registro['split_return_by']
        split_get_element   = registro['split_get_element'],
        quemeta             = registro['meta']

        resultado = loadProductBeautifulSoup(soup2,selector,que_busca, que_obtiene, quemeta)
                
        valor    =  resultado['valor']
        es_error =  resultado['es_error']
        if not es_error:
            if valor:
                valor    = valor.lstrip()
                valor    = valor.rstrip()
                valor    = valor.title()
            else:
                valor   = ""
        
        ## Elimina strings o caracteres que no se desean
        if removeChars and not es_error: 
            for remover in list(removeChars.split(" ")):
                valor =  valor.replace(remover,'')

        if split_return_by:
            my_list = valor.split(split_return_by)
            if len(my_list) > 1:
                valor = my_list[split_get_element]
            else:
                valor = ""

        return valor, es_error

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
            today = utc.localize(datetime.today())

        
        for site in sites:
            ### Get Site Info
            if site.agregaSiteURL:
                url_suffix = site.siteURL
            else:
                url_suffix = ""

            print(f'Empresa = {site.siteName}')
            
            siteclicks = getCampoDef('mayordeedad',site)
           

            ## Error 404
            arr_campo404 = getCampoDef('Pagina404',site)
            

            listaDeCampos  =  Campos.objects.filter(donde=DONDESEUSA.EN_PRODUCTO)
            campoEnSitioObject = CamposEnSitio.objects.filter(site=site, campo__in=listaDeCampos, enabled=True)
            
            listaURLS = SiteURLResults.objects.filter(
                site=site, 
                error404=False,
                updated__lte=today
                 ).order_by('updated')[startRecord:numRecords]

            
            urlCount = 0
            for laurl in listaURLS:
                url = urllib.parse.unquote(laurl.url)

                urlCount = urlCount + 1
                startTime = datetime.now()
                
                try:
                    page2 = requests.get(url, self.headers)
                except requests.HTTPError:
                    laurl.error404 = True
                    laurl.save()
                    continue
                except:
                    laurl.error404 = True
                    laurl.save()
                    continue
                soup2 = BeautifulSoup(page2.content, "html.parser")

                # if arr_campo404:
                #     salir = False
                #     for registro in arr_campo404:
                #         if check_exists(browser, registro['como'], registro['que_busca']):
                #             print(f'Error 404 url={url}')
                #             laurl.error404 = True
                #             laurl.save()
                #             salir = True
                #             break
                        
                #     if salir:
                #         continue
                #     else:
                #         laurl.error404 = False
                #         laurl.save()
     
                for campoensitio in campoEnSitioObject:
                    arr_campo = getCampoDef(campoensitio.campo.nombre,site)
                    for registro in arr_campo:

                        valor, es_error = self.get_resultado(soup2, registro)
                        selectorcampo = SelectorCampo.objects.get(pk=registro['SelectorCampoID'])
                        if not es_error:
                            selectorcampo.error_count = 0
                            selectorcampo.save()
                            break
                        else:
                            selectorcampo.error_count = selectorcampo.error_count + 1
                            selectorcampo.save()


                    if not es_error:
                        laurl = saveUrlData(campoensitio, laurl, valor)
                        campoensitio.save()

                endTime = datetime.now()
                difference = endTime - startTime


                laurl.secondsToGet = int(difference.total_seconds())
                laurl.error404 = False        
                laurl.save()
                print(f'Site={site}... {urlCount} de {numRecords }, Tiempo = {int(difference.total_seconds())}')      

            site.save()
        print("Fin de la ejecucion")