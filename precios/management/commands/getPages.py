from django.core.management.base import BaseCommand
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
# from precios.models import (
#     Settings,
#     Site, 
#     Pages, 
#     Campos,
#     CamposEnSitio,
#     DONDESEUSA,
#     SelectorCampo
# )


# import re
# import urllib.parse
# from time import sleep
# import time


# from precios.pi_functions import (
#     check_exists, 
#     click_element,
#     add_page,
#     getCampoDef,
#     get_resultadoSelenium,
#     urlSave,
#     find_element,
#     find_elements,
#     saveUrlData
# )
# from precios.pi_get import (
#     url_get, 
#     getSiteProperties, 
#     set_browser
# ) 

# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, StaleElementReferenceException

from datetime import datetime, timedelta
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
import chromedriver_autoinstaller

try:
    chromedriver_autoinstaller.install() 
except:
    print('Sin conexión')

from precios.models import Site, Campos, CamposEnSitio, SiteURLResults, Pages, Settings

from precios.pi_get import (
    url_get, 
    getSiteProperties, 
    set_browser
) 
from django.core.exceptions import ObjectDoesNotExist
from precios.pi_functions import (
    check_exists, 
    add_page,
    urlSave,
)

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



    # def NextPage(self, browser, arr_nextPage, page, site, MaxPagesInThisPage, page_counter):
    #     salir = False
    #     for registro in arr_nextPage:
    #         if check_exists(browser, registro['como'], registro['que_busca']):
    #             # print(f"Existe boton Next Page registro={registro}")
    #             elements = browser.find_elements(registro['como'], registro['que_busca'])
    #             for element in elements:
    #                 try:
    #                     print("inicio Try  page_counter=", page_counter)
    #                     clases = element.get_attribute("class")
    #                     if registro['evita'] in clases:
    #                         # Botonn next des-habilitado
    #                         salir = True
    #                         print("Saliendo con ", page_counter)
    #                         break
    #                     # element.click()
    #                     # click_element(browser,registro['como'], registro['que_busca'])
    #                     browser.execute_script("arguments[0].click();", element)

    #                     page_counter = page_counter + 1
    #                     URL = add_page(site, page, page_counter)
                        
    #                     page.lastPageIndexed = page_counter
    #                     page.save()
    #                     time.sleep(0.5)                                    
            
    #                 except ElementNotInteractableException: #if something goes wrong, and the next page button is able to be clicked, this ensures the whole program doesn't crash
    #                     print("en ElementNotInteractableException  No se puede hacer Click en Next Page")
    #                     page_counter = page_counter + 1
    #                     if page_counter <= MaxPagesInThisPage  :
    #                         URL = add_page(site, page, page_counter)
    #                         print( URL)
    #                         browser.get(URL)
    #                         page.lastPageIndexed = page_counter
    #                         page.save()
    #                         time.sleep(1.5)
    #                     else:
    #                         salir = True
    #                         page_counter = 1
    #                         sufijo = ""
    #                     break
    #                 except StaleElementReferenceException:
    #                     print("en StaleElementReferenceException")
    #                     # page_counter = page_counter + 1
    #                     if page_counter <= MaxPagesInThisPage  :
    #                         URL = add_page(site, page, page_counter)
    #                         print( URL)
    #                         browser.get(URL)
    #                         page.lastPageIndexed = page_counter
    #                         page.save()
    #                     else:
    #                         salir = True
    #                         page_counter = 1
    #                         sufijo = ""
    #                     break
    #                 except Exception as e:
    #                     # URL = add_page(site, page, page_counter)
    #                     # print( URL)

    #                     print(str(e))
    #                     salir = True
    #                     break
                    
    #         else: #no additional pages
    #             print("NO HAY  boton Next Page")
    #             salir = True
    #             break

    #     return salir, page_counter
            
    def obtener_estructura_enlaces(self, site, palabras_clave_evitar, max_urls_visitadas, max_levels, site_category, debug):
        url_base                = site.siteURL
        siteAgregaSiteUrl       = site.agregaSiteURL
        siteAllLinksInOnePage   = site.allLinksInOnePage

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

        estructura_enlaces = {}  # Estructura para mapear URL padre a enlaces hijos
        urls_visitadas = set()  # Almacenar todas las URLs visitadas


        # Configuración de Selenium
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Ejecución sin ventana del navegador
        options.add_argument("--enable-javascript")
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)

        def updatePage(site, url):
            siteURL         = site.siteURL
            page_parameter  = site.page_parameter

            pageBase1       = url.replace(siteURL,'')
            pageBase2_arr   = pageBase1.split(page_parameter)
            pageBase        = pageBase2_arr[0]

            if len(pageBase2_arr) > 1:
                pageNumber  = pageBase2_arr[1]
                pageNumber  = pageNumber.replace('/','')
                # print(len(pageBase2_arr))
            else:
                pageNumber  = 0

            # print(f'pageBase={pageBase} pageNumber={pageNumber}')
            ## Page exists ?
            if Pages.objects.filter(site=site, page=pageBase).exists():
                # print(f'Existe pageBase={pageBase} ')
                ## Get Page
                page = Pages.objects.filter(site=site, page=pageBase).get()
                maxPagesFound = page.maxPagesFound
                if int(pageNumber) > maxPagesFound:
                    page.maxPagesFound = pageNumber

                page.save()
            else:
                obj_url, created = Pages.objects.update_or_create(site=site,  page=pageBase,enabled=True,maxPagesFound=pageNumber)
                if created:
                    print(f'Se crea pageBase={pageBase} ')
                else:
                    print(f'Se MODIFICA pageBase={pageBase} ')
            
            

        def NextPage(browser, arr_nextPage, site, MaxPagesInThisPage, page_counter):
            salir = False
            browser.implicitly_wait(10)
            for registro in arr_nextPage:
                if check_exists(browser, registro['como'], registro['que_busca']):
                    # print(f"Existe boton Next Page registro={registro}")
                    elements = browser.find_elements(registro['como'], registro['que_busca'])
                    for element in elements:
                        try:
                            # print("inicio Try  page_counter=", page_counter)
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
                            # URL = add_page(site, '', page_counter)
                            
                            
                
                        except ElementNotInteractableException: #if something goes wrong, and the next page button is able to be clicked, this ensures the whole program doesn't crash
                            print("en ElementNotInteractableException  No se puede hacer Click en Next Page")
                            page_counter = page_counter + 1

                            break
                        except StaleElementReferenceException:
                            print("en StaleElementReferenceException")
                            page_counter = page_counter + 1
                            if page_counter <= MaxPagesInThisPage  :
                                URL = add_page(site, '', page_counter)
                                print( URL)
                                browser.get(URL)
                           
                            break
                        except Exception as e:

                            print(str(e))
                            salir = True
                            break
                        
                else: #no additional pages
                    # print("NO HAY  boton Next Page")
                    salir = True
                    break

            return salir, page_counter
        
        def buscar_enlaces(url, nivel=1, dominio_actual=None):
            if nivel > max_levels:  # Limitar la recursión
                return

            if dominio_actual is None:
                dominio_actual = url

            if max_urls_visitadas:
                if len(estructura_enlaces) > max_urls_visitadas:
                    return

            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                htmlelement= driver.find_element(By.TAG_NAME, 'html')
            
            except Exception as e:
                print(f"Error al obtener las URLs de {url}: {e} nivel={nivel}")

            if site.listNeedsPgDn:
                cuenta_down = 0
                while cuenta_down < 2:
                    htmlelement.send_keys(Keys.PAGE_DOWN)
                    cuenta_down = cuenta_down + 1
                    
            urls = set()
            
            MaxPagesInThisPage = 1
            page_counter = 1
            salir, page_counter = NextPage(driver, arr_nextPage, site, MaxPagesInThisPage, page_counter)
                    
            for enlace in driver.find_elements(By.TAG_NAME, 'a'):
                url_enlace = enlace.get_attribute('href')
                
                if url_enlace and \
                    url_enlace.startswith('http') and \
                    url_enlace.startswith(site.product_url) and \
                    not contiene_palabras_clave(url_enlace, palabras_clave_evitar) and \
                    url_enlace not in urls_visitadas:
                    
                    urls.add(url_enlace)

                    if site_category in url_enlace:
                        if not debug:
                            updatePage(site, url_enlace)
                        
                    else:
                        print(f'Otro tipo de URL = {url_enlace} nivel={nivel}')
                    

            
            if url not in estructura_enlaces:
                estructura_enlaces[(nivel, url)] = urls
            
            urls_visitadas.update(urls)  # Agregar las URLs visitadas al conjunto global
            print(f' {len(urls_visitadas)} Nivel={nivel}')
            
            try:
                # Procesar las URLs encontradas
                for nueva_url in urls:
                    buscar_enlaces(nueva_url, nivel + 1, dominio_actual)

            except Exception as e:
                print(f"Error al buscar_enlaces {url}: {e} nivel={nivel}")

        def contiene_palabras_clave(url, palabras_clave):
            return any(palabra in url for palabra in palabras_clave)

        buscar_enlaces(site.siteURL)

        driver.quit()  # Cerrar el navegador después de terminar

        return estructura_enlaces
       
    def handle(self, *args, **options):
        SiteId = options["SiteId"]
        numRecords = options["numrecords"]

        print("Current Time =", datetime.now().time())

        sites = Site.objects.filter(id=SiteId)
        for site in sites:
            print(" 1   Current Time =", datetime.now().time())
            max_urls_visitadas  = None
            # max_levels          = 3
            max_urls_visitadas  = 20
            max_levels          = 2
            debug               = False

            ### Get Site Info
            url_base                = site.siteURL
            siteAgregaSiteUrl       = site.agregaSiteURL
            siteAllLinksInOnePage   = site.allLinksInOnePage

            site_category           = site.product_category
            site_producto           = site.product_product
            product_palabras_evitar = site.product_palabras_evitar

            if not product_palabras_evitar:
                palabras_clave_evitar = ['/busca', '#']
            else:
                palabras_clave_evitar       = list(site.product_palabras_evitar.split(','))    
            
            if not site_category  :
                print(f'Falta definir variables site_category  sitio={site}')
                site_category       = 'quiendabese'
                debug               = True
                
            
                
            # if not site_producto :
            #     print(f'Falta definir variables site_producto en sitio={site}')
            #     site_producto       = 'nosecuales'
                

            if siteAgregaSiteUrl:
                url_suffix = url_base
            else:
                url_suffix = ""

            estructura_enlaces = self.obtener_estructura_enlaces(site,  palabras_clave_evitar, max_urls_visitadas, max_levels, site_category, debug)

            # Imprimir la estructura de enlaces
            # for url_padre, enlaces_hijos in estructura_enlaces.items():
            #     print(f"Level: {url_padre}")

            #     print(f"Hijos: ")
            #     for enlaces_hijo in enlaces_hijos:
            #         print(f"- {enlaces_hijo}")
                    
                    
            #     print()
            


        


        print("Fin de la ejecucion")