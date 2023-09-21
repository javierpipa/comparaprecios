from django.core.management.base import BaseCommand
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from precios.models import (
    Settings,
    Site, 
    Pages, 
    Campos,
    CamposEnSitio,
    DONDESEUSA,
    SelectorCampo
)

# import requests
# from bs4 import BeautifulSoup
# from lxml import etree
import re

import urllib.parse
from time import sleep
import time
from datetime import datetime, timedelta

from precios.pi_functions import (
    check_exists, 
    click_element,
    add_page,
    getCampoDef,
    get_resultadoSelenium,
    urlSave,
    find_element,
    find_elements,
    saveUrlData
)
from precios.pi_get import (
    url_get, 
    getSiteProperties, 
    set_browser
) 

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, StaleElementReferenceException


######## IMPORTANTE ############
# browser.implicitly_wait(10)
################################

class Command(BaseCommand):
    help = "Start the simulation"

    def __init__(self):
        super().__init__()

    def add_arguments(self, parser):
        default_num_pages = int(Settings.objects.get(key='Get_Num_Pages').value)
        parser.add_argument('SiteId', type=int, help='Id of VM to get info')
        parser.add_argument('numrecords', nargs='?', type=int, default=default_num_pages,
                    help='the bar to %(prog)s (default: %(default)s)')



    def NextPage(self, browser, arr_nextPage, page, site, MaxPagesInThisPage, page_counter):
        salir = False
        for registro in arr_nextPage:
            if check_exists(browser, registro['como'], registro['que_busca']):
                # print(f"Existe boton Next Page registro={registro}")
                elements = browser.find_elements(registro['como'], registro['que_busca'])
                for element in elements:
                    try:
                        print("inicio Try  page_counter=", page_counter)
                        clases = element.get_attribute("class")
                        if registro['evita'] in clases:
                            # Botonn next des-habilitado
                            salir = True
                            print("Saliendo con ", page_counter)
                            break
                        # element.click()
                        # click_element(browser,registro['como'], registro['que_busca'])
                        browser.execute_script("arguments[0].click();", element)

                        page_counter = page_counter + 1
                        URL = add_page(site, page, page_counter)
                        
                        page.lastPageIndexed = page_counter
                        page.save()
                        time.sleep(0.5)                                    
            
                    except ElementNotInteractableException: #if something goes wrong, and the next page button is able to be clicked, this ensures the whole program doesn't crash
                        print("en ElementNotInteractableException  No se puede hacer Click en Next Page")
                        page_counter = page_counter + 1
                        if page_counter <= MaxPagesInThisPage  :
                            URL = add_page(site, page, page_counter)
                            print( URL)
                            browser.get(URL)
                            page.lastPageIndexed = page_counter
                            page.save()
                            time.sleep(1.5)
                        else:
                            salir = True
                            page_counter = 1
                            sufijo = ""
                        break
                    except StaleElementReferenceException:
                        print("en StaleElementReferenceException")
                        # page_counter = page_counter + 1
                        if page_counter <= MaxPagesInThisPage  :
                            URL = add_page(site, page, page_counter)
                            print( URL)
                            browser.get(URL)
                            page.lastPageIndexed = page_counter
                            page.save()
                        else:
                            salir = True
                            page_counter = 1
                            sufijo = ""
                        break
                    except Exception as e:
                        # URL = add_page(site, page, page_counter)
                        # print( URL)

                        print(str(e))
                        salir = True
                        break
                    
            else: #no additional pages
                print("NO HAY  boton Next Page")
                salir = True
                break

        return salir, page_counter
            

       
    def handle(self, *args, **options):
        SiteId = options["SiteId"]
        numRecords = options["numrecords"]

        print("Current Time =", datetime.now().time())

        sites = Site.objects.filter(id=SiteId)
        for site in sites:
            print(" 1   Current Time =", datetime.now().time())
            ### Get Site Info
            url_base                = site.siteURL
            siteAgregaSiteUrl       = site.agregaSiteURL
            siteAllLinksInOnePage   = site.allLinksInOnePage

            if siteAgregaSiteUrl:
                url_suffix = url_base
            else:
                url_suffix = ""


            pages = Pages.objects.filter(site=site, enabled=True).order_by('last_scan')
            # [:numRecords]


            siteclicks, \
                arr_campo404, \
                listaDeCampos, \
                campoEnSitioObject, \
                arr_linksSelector, \
                ItemsEnListado,\
                arr_nextPage, \
                arr_maxPages = getSiteProperties(site)


            ## Campos en items del listado
            campoField = Campos.objects.filter(nombre='ItemsEnListado').get()
            try:
                campo_sitio = CamposEnSitio.objects.filter(site=site,campo=campoField,enabled=True).get()
                arr_hijos_del_listado = CamposEnSitio.objects.filter(
                    site=site,
                    hijoDe=campo_sitio
                )

            except ObjectDoesNotExist:
                arr_hijos_del_listado = None

            
            if arr_hijos_del_listado:
                arr_inicio      = ItemsEnListado
                arr_procesar    = arr_hijos_del_listado
            else:
                arr_inicio      = arr_linksSelector
                arr_procesar    = arr_linksSelector

            browser = set_browser(True)
            

            for page in pages:
                page_counter = 1

                URL = add_page(site, page, page_counter)
                print( URL)

                browser.get(URL)
                browser.maximize_window()

                site.save()
                page.save()


                htmlelement= browser.find_element(By.TAG_NAME, 'html')

                #Scrolls down to the bottom of the page
                htmlelement.send_keys(Keys.END)

                #Scrolls up to the top of the page
                htmlelement.send_keys(Keys.HOME)
                
                if arr_campo404:
                    salir = False
                    for registro in arr_campo404:
                        if check_exists(browser, registro['como'], registro['que_busca']):
                            print(f'Error 404 ')
                            page.got_404 = True
                            page.save()
                            salir = True
                            break
                    if salir:
                        continue
                    else:
                        page.got_404 = False
                        page.save()

                
                ## Busco MaxPages
                MaxPagesInThisPage = 1
                if arr_maxPages:
                    for registro in arr_maxPages:
                        listadePaginas = find_elements(browser, registro['como'], registro['que_busca'])
                        if listadePaginas:
                            MaxPagesInThisPage = len(listadePaginas)
                            break
                        else:
                            MaxPagesInThisPage = 10

                print(f'MaxPagesInThisPage={MaxPagesInThisPage}')
                page.maxPagesFound = MaxPagesInThisPage
                page.save()

                # ## Check Mayor de edad
                if siteclicks:
                    salir = False
                    for registro in siteclicks:
                        if check_exists(browser, registro['como'], registro['que_busca']):
                            click_element(browser,registro['como'], registro['que_busca'])
                            # print("HIZO Click MAYOR")
                            htmlelement.send_keys(Keys.END)


                htmlelement= browser.find_element(By.TAG_NAME, 'html')
                while True:
                    if site.listNeedsPgDn:
                        cuenta_down = 0
                        while cuenta_down < 2:
                            # htmlelement.send_keys(Keys.PAGE_DOWN)
                            cuenta_down = cuenta_down + 1
                        ## Por Easy ###

                    time.sleep(2)

                    # return
                    ## Get ItemsEnListado
                    # for item in ItemsEnListado:
                    cuenta_ele = 0
                    for item in arr_inicio:
                        
                        elementos = find_elements(browser, item['como'], item['que_busca'])
                        
                        if elementos:
                            print(len(elementos))
                            # #### Intentamos buscar y grabar contenido
                            for elemento in elementos:
                                cuenta_ele +=1
                                
                                
                                action = ActionChains(browser)
                                action = ActionChains(browser).send_keys(Keys.PAGE_DOWN)
                                # for num in range(1, cuenta_ele):
                                #     if num % 8 ==0:
                                #         action = ActionChains(browser).send_keys(Keys.PAGE_DOWN)
                                action.perform()
                                # time.sleep(0.3)

                                startTime = datetime.now()
                                
                                laurl = None
                                for campoensitio in arr_procesar:
                                    arr_campo = getCampoDef(campoensitio.campo.nombre,site)

                                    for registro in arr_campo:
                                        # valor, es_error = get_resultadoSelenium(elemento,registro,len(elementos))
                                        valor, es_error = get_resultadoSelenium(elemento,registro)
                                        
                                        selectorcampo = SelectorCampo.objects.get(pk=registro['SelectorCampoID'])
                                        if not es_error:
                                            selectorcampo.error_count = 0
                                            selectorcampo.save()
                                            # print("Grabaria ", selectorcampo)
                                            break
                                        else:
                                            selectorcampo.error_count = selectorcampo.error_count + 1
                                            selectorcampo.save()
                                            print("Errrorr ", selectorcampo)
                                        
                                        
                                    if not es_error:
                                        if arr_campo[0]["campoQueGraba"] == 'url':
                                            # print(f'Arrrcampo = {arr_campo[0]["campoQueGraba"]}')
                                            laurl, created = urlSave(site,  url_suffix + valor)
                                        else:
                                            # print(f'valor={valor}')
                                            if laurl:
                                                laurl = saveUrlData(campoensitio, laurl, valor)

                                    # print("pageDnnn 2")
                                    # htmlelement.send_keys(Keys.PAGE_DOWN)
                                endTime = datetime.now()
                                difference = endTime - startTime

                                if laurl:
                                    laurl.secondsToGet = int(difference.total_seconds())
                                    laurl.error404 = False        
                                    laurl.save()
                        else:
                            
                            print('Sin elementos', item['como'], item['que_busca'])

                       
                    
                    salir, page_counter = self.NextPage(browser, arr_nextPage, page, site, MaxPagesInThisPage, page_counter)
                    print('salir=', salir)
                    # salir = True
                  
                    if salir:
                        break
                
                
                # if siteAllLinksInOnePage:
                #     for registro in arr_linksSelector:
                #         self.get_links_selenium(registro['evita'], site,  browser, registro['como'], registro['que_busca'], text_suffix=url_suffix)

                # return
                page.last_scan = datetime.now()
                page.save()
                # if page_counter > numRecords:
                #     print("Saliendo")
                #     break

            site.save()


        browser.quit()


        print("Fin de la ejecucion")