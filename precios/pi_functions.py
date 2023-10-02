from precios.models import (
    Settings,
    Site, 
    Marcas, 
    Campos,
    CamposEnSitio,
    SiteURLResults,
    Unifica,
    SelectorCampo,
    SiteMap,
    Countries,
    Regions,
    Cities,
    MomentosDespacho,
    Articulos,
    Vendedores,
    Estadistica_Consulta,
    EstadisticasBlackList,
)
from datetime import date


# from precios.pi_get import reemplaza_palabras    

from lxml import etree
from django.utils.dateparse import parse_date
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import F, Sum, Count, Min, Max


import psutil
from viusitemapparser.vsp import get_sitemap_contents
from viusitemapparser.get_file import get_file

from selenium.common.exceptions import NoSuchElementException 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

def getMessage():
    return Settings.objects.get(key='MSG-actualiza-articulos').value


def setMessage(valor):
    mensaje = Settings.objects.get(key='MSG-actualiza-articulos')
    mensaje.value = valor
    mensaje.save()

def registrar_consulta(request, clase_consultada, elemento_id, texto_busqueda=None):
    agente = request.META.get('HTTP_USER_AGENT')
    
    try:
        blacklist_entry = EstadisticasBlackList.objects.get(agente=agente)
        if blacklist_entry.no_contabilizar:
            return  # No contabilizar consultas para este agente
    except EstadisticasBlackList.DoesNotExist:
        # El agente no está en la lista negra, agregarlo con no_contabilizar = False
        blacklist_entry = EstadisticasBlackList.objects.create(agente=agente, no_contabilizar=False)

    fecha_actual = date.today()

    if texto_busqueda:
        # Obtén el último elemento_id para el texto de búsqueda
        ultimo_elemento = Estadistica_Consulta.objects.filter(
            clase_consultada=clase_consultada,
            texto_busqueda=texto_busqueda
        ).order_by('-elemento_id').first()

        if ultimo_elemento:
            nuevo_elemento_id = ultimo_elemento.elemento_id + 1
        else:
            nuevo_elemento_id = 1
    else:
        nuevo_elemento_id = elemento_id

    consulta, created = Estadistica_Consulta.objects.get_or_create(
        clase_consultada=clase_consultada,
        elemento_id=nuevo_elemento_id,
        fecha=fecha_actual,
        defaults={'texto_busqueda': texto_busqueda}
    )

    consulta.cantidad_vista += 1
    consulta.save()




###################
#### BeautifulSoup
###################
def loadProductBeautifulSoup(sopa, como, que_busca, que_obtiene, metaopcion):
    ## Para BeautifulSoup
    es_error  = False
    retorna = None
    if como == "valorfijo":
        retorna = que_busca
    if como == "css selector":
        try:
            objetos = sopa.select(que_busca)
            if not objetos:
                raise Exception("Objeto no existe")
                
            for objeto in objetos:
                if que_obtiene == 'text':
                    retorna = objeto.text
                else:
                    retorna = objeto[que_obtiene]

                
        except Exception as e:
            es_error  = True
            retorna = str(e)[0:640]
            
    elif como == "xpath":
        try:
            dom = etree.HTML(str(sopa))
            objetos = dom.xpath(que_busca)
            for objeto in objetos:
                retorna = objeto.text

        except Exception as e:
            es_error  = True
            retorna = str(e)[0:640]

    elif como == "meta":
        try:
            objetos = sopa.find("meta", property=que_busca)
            # objetos = sopa.find("meta", metaopcion=que_busca)
            for objeto in objetos:
                retorna = objeto[que_obtiene]

        except Exception as e:
            es_error  = True
            retorna = str(e)[0:640]
    
    # except Exception as e:
    #     print(f'*** como= {como} LoadProductBeautiful function Error: {str(e)}')
    #     retorna = str(e)[0:640]
    #     es_error  = True
    print(que_busca, retorna)

    return {"es_error": es_error, "valor":retorna}

def generate_filters(articulos):
    filtro = {}

    articulo_ids = articulos.values_list('id', flat=True)

    # Supermercados
    # Filtrar los Vendedores que tienen esos Articulos
    vendedores_filtrados = Vendedores.objects.filter(articulo__id__in=articulo_ids).exclude(vendidoen__precio=0)
    # Generar el filtro de supermercados
    supermercados = vendedores_filtrados.values('vendidoen__site__siteName', 'vendidoen__site__id').annotate(Count('articulo', distinct=True)).order_by()
    filtro['supermercados'] = supermercados

    # Marcas
    marcas = articulos.values('marca__nombre','marca_id').annotate(Count('id', distinct=True)).order_by()
    filtro['marcas'] = marcas

    # Grados
    grados = articulos.values('grados2').exclude(grados2=0).order_by('grados2').annotate(Count('id', distinct=True))
    filtro['grados'] = grados

    # Envase
    envase = articulos.values('envase').exclude(envase=None).annotate(Count('id', distinct=True)).order_by()
    filtro['envase'] = envase

    # Color
    color = articulos.values('color').exclude(color='').annotate(Count('id', distinct=True)).order_by()
    filtro['color'] = color

    # Medida cantidad
    medida_cant = articulos.values('medida_cant').annotate(Count('id', distinct=True)).order_by()
    filtro['medida_cant'] = medida_cant

    # Medida (cantidad y unidad de medida)
    medida = articulos.values('medida_cant', 'medida_um').annotate(Count('id', distinct=True)).order_by()
    filtro['medida'] = medida

    # Unidad de medida
    medida_um = articulos.values('medida_um').annotate(Count('id', distinct=True)).order_by()
    filtro['medida_um'] = medida_um

    # Talla
    medida_um = articulos.values('talla').exclude(talla='').annotate(Count('id', distinct=True)).order_by()
    filtro['talla'] = medida_um

    # Unidad de unidades
    unidades = articulos.values('unidades').annotate(Count('id', distinct=True)).order_by()
    filtro['unidades'] = unidades

    # # Rango de precios
    # rango_precios = articulos.aggregate(
    #     min_precio=Min('mejorprecio'),
    #     max_precio=Max('mejorprecio')
    # )

    # filtro['min_precio'] = rango_precios['min_precio']
    # filtro['max_precio'] = rango_precios['max_precio']

    return filtro

def generate_articulos_dict(articulos, momentos, MinSuperCompara, orden):
    articulos_dict = []
    articulos_count = 0
    ofertas_count = 0  # Asegúrate de inicializar esta variable si la usas posteriormente

    for particulo in articulos:
        if particulo.num_vendedores >= MinSuperCompara:
            detalle = Vendedores.objects \
                .filter(articulo=particulo.id) \
                .filter(vendidoen__site__in=momentos) \
                .exclude(vendidoen__precio__exact=0) \
                .order_by('vendidoen__precio')

            if detalle:
                articulos_count += 1
                ofertas_count += particulo.num_vendedores
                mejor_precio = detalle.first().vendidoen.precio if detalle.first() else None
                unidades = particulo.unidades if particulo.unidades else 1

                precio_por_unidad = mejor_precio / unidades if mejor_precio and unidades else None

                articulos_dict.append({
                    'articulo': particulo,
                    'detalle': detalle,
                    'ofertas': particulo.num_vendedores,
                    'mejor_precio': mejor_precio,
                    'precio_por_unidad': precio_por_unidad,
                    'marca': particulo.marca.nombre,
                    'nombre': particulo.nombre
                })

    # Ordenar la lista de diccionarios
    if orden.startswith('-'):
        articulos_dict = sorted(articulos_dict, key=lambda x: x.get(orden[1:]), reverse=True)
    else:
        articulos_dict = sorted(articulos_dict, key=lambda x: x.get(orden))

    return articulos_dict, articulos_count, ofertas_count
    
def getMomentos(request):
    momentos = MomentosDespacho.objects.all()
    momentos = momentos.values_list('areaDespacho__site',flat=True)
    momentos = momentos.distinct()

    if request.session.get('country_id'):
        regiones = Regions.objects.filter(country=request.session['country_id'])
        comunas = Cities.objects.filter(region__in=regiones)
        momentos = momentos.filter(areaDespacho__comuna__in=comunas)
    if request.session.get('region_id'):
        comunas = Cities.objects.filter(region__in=request.session['region_id'])
        momentos = momentos.filter(areaDespacho__comuna__in=comunas)
    if request.session.get('comuna_id'):
        momentos = momentos.filter(areaDespacho__comuna=request.session['comuna_id'])

    momentos = momentos.filter(areaDespacho__site__enable=True)

    momentos = momentos.values_list('areaDespacho__site',flat=True)
    momentos = momentos.distinct()
    supermercadoscount =  momentos.count()
        
    return momentos, supermercadoscount


def safe_session(request, country_id=None, region_id=None, comuna_id=None):
    request.session['country_id'] = country_id
    request.session['region_id'] = region_id
    request.session['comuna_id'] = comuna_id
    
    country_label = None
    if country_id:
        country_label = Countries.objects.values_list('name', flat=True).get(id=country_id)
    request.session['country_label'] = country_label

    region_label = None
    if region_id:
        region_label = Regions.objects.values_list('name', flat=True).get(id=region_id)
    request.session['region_label'] = region_label

    comuna_label = None
    if comuna_id:
        comuna_label = Cities.objects.values_list('name', flat=True).get(id=comuna_id)
    request.session['comuna_label'] = comuna_label

    return country_label, region_label, comuna_label

def get_sessions(request):
    country_id = None
    region_id = None
    comuna_id = None

    if 'country_id' in request.session:
        country_id = request.session['country_id']

    if 'region_id' in request.session:
        region_id = request.session['region_id']

    if 'comuna_id' in request.session:
        comuna_id = request.session['comuna_id']

    return country_id, region_id, comuna_id

def set_headers():
    ## Para BeautifulSoup
    user_agent          = Settings.objects.get(key='user-agent').value
    return {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': user_agent
            }

###################
#### Selenium
###################
def get_resultadoSelenium( browser, registro ):
    selector            = registro['como']
    que_busca           = registro['que_busca']
    que_obtiene         = registro['que_obtiene']
    printit             = registro['printit']
    removeChars         = registro['removeChars']
    split_return_by     = registro['split_return_by']
    split_get_element   = registro['split_get_element']
    quemeta             = registro['meta']
                            
    resultado = loadProductSelenium(browser, selector, que_busca,  que_obtiene, quemeta)

    valor    = resultado['valor']
    es_error = resultado['es_error']
    if printit:
        print(resultado)

    if not es_error and valor:
        valor = valor.lstrip()
        # valor = valor.title()
        
        ## Elimina strings o caracteres que no se desean
        if removeChars and not es_error: 
            for remover in list(removeChars.split(" ")):
                valor =  valor.replace(remover,'')

        if split_return_by:
            valor = valor.split(split_return_by)[split_get_element]

    
    return valor, es_error

def check_exists(driver, by_what, que_busca):
    try:
        driver.find_element(by_what, que_busca)

    except NoSuchElementException:
        return False
    except Exception as e:
        return False
    return True

def urlSave(site, url):
    if site.product_url != "" and site.product_url in url:
        try:
            obj_url, created = SiteURLResults.objects.update_or_create(site=site,  url=url)
            print(f'created = {created}')
        except:
            print(f'error con URL = {url}')
            obj_url = None
            created = False
    else:
        obj_url = None
        created = False
    return obj_url, created


def get_num_url_in_sites_per_brand(marcastr):
    subquery    = SiteURLResults.objects.filter(marca__exact=marcastr).exclude(error404=True).exclude(precio=0).exclude(site__id=7)
    subquery    = subquery.values('site__id')
    subquery    = subquery.annotate(total=Count('site__id'))
    subquery    = subquery.order_by('-total')
    subquery.all()

    return subquery

def get_articles_from_site(marcaobj, arr_id_url):
    vendedores = Vendedores.objects.select_related().filter(articulo__marca=marcaobj, vendidoen__site__in=arr_id_url).values_list('articulo__pk', flat=True).all()
    articles = Articulos.objects.filter(marca=marcaobj, id__in=vendedores).all()
    return articles, vendedores
    # 

def get_url_from_site(marca_str, siteid):
    urls2 = SiteURLResults.objects.filter(site__id=siteid, marca__iexact=marca_str ).exclude(error404=True).exclude(precio=0).all()
    return urls2

def get_url_from_site_mul(marca_str, site_list):
    urls = SiteURLResults.objects.filter(site__id__in=site_list, marca__iexact=marca_str ).exclude(error404=True).exclude(precio=0).all()
    return urls

def add_rule(rules, row_es, row_debe_ser, tipo, fuz_level):
    rules = {
        'si_marca':             row_es['articulo__marca'],
        'si_nombre':            row_es['articulo__nombre'],
        'si_grados':            row_es['articulo__grados2'],
        'si_medida_cant':       row_es['articulo__medida_cant'],
        'si_unidades':          row_es['articulo__unidades'],
        'si_envase'  :          row_es['articulo__envase'],
        'si_talla'  :           row_es['articulo__talla'],
        'entonces_marca' :      row_debe_ser['articulo__marca'],
        'entonces_nombre' :     row_debe_ser['articulo__nombre'],
        'entonces_grados' :     row_debe_ser['articulo__grados2'],
        'entonces_medida_cant': row_debe_ser['articulo__medida_cant'],
        'entonces_unidades' :   row_debe_ser['articulo__unidades'],
        'entonces_envase'   :   row_debe_ser['articulo__envase'],
        'entonces_talla'    :   row_debe_ser['articulo__talla'],
        'tipo': tipo,
        'fuz': fuz_level,
    }
    return rules




def saveUrlData(campoensitio, laurl, valor):

    if valor is not None:
        valor = valor.lstrip()

    if campoensitio.campo.campoQueGraba == 'proveedor':
        valor                   = valor.lower()
        laurl.proveedor         = valor

    if campoensitio.campo.campoQueGraba == 'stock':
        valor                   = valor.lower()
        laurl.stock             = valor[0:20]

    if campoensitio.campo.campoQueGraba == 'precioref':
        valor                   = valor.lower()
        laurl.precioref         = int(valor)

    if campoensitio.campo.campoQueGraba == 'unidades':
        valor                   = valor.lower()
        valor                   = float(valor)
        laurl.unidades          = valor

    if campoensitio.campo.campoQueGraba == 'medida_um':
        valor                   = valor.lower()
        laurl.medida_um          = valor

    if campoensitio.campo.campoQueGraba == 'medida_cant':
        valor                   = valor.lower()
        valor                   = float(valor)
        laurl.medida_cant       = valor

    if campoensitio.campo.campoQueGraba == 'tipo':
        valor                   = valor.lower()
        laurl.tipo              = valor.lstrip()
    
    if campoensitio.campo.campoQueGraba == 'categoria':
        valor                   = valor.lower()
        laurl.categoria         = valor.lstrip()

    if campoensitio.campo.campoQueGraba == 'nombre':
        valor                   = valor.lower()
        laurl.nombre            = valor.lstrip()

    if campoensitio.campo.campoQueGraba == 'descripcion':
        valor                   = valor.lower()
        laurl.descripcion       = valor.lstrip()

    if campoensitio.campo.campoQueGraba == 'marca':
        valor                   = valor.lower()
        laurl.marca             = valor.lstrip()

    if campoensitio.campo.campoQueGraba == 'idproducto':
        valor                   = valor.lower()
        laurl.idproducto        = valor.lstrip()

    if campoensitio.campo.campoQueGraba == 'image':
        laurl.image         = valor

    if campoensitio.campo.campoQueGraba == 'precio':
        valor               = valor.replace('.','')
        valor               = valor.replace('$','')

        if 'x' in valor or 'X' in valor:
            if 'x' in valor :
                datos = valor.split("x")
            if 'X' in valor:
                datos = valor.split("X")
            val1 = int(datos[0])
            laurl.precio_cantidad   = val1
            # print(f'  URL {laurl.url} tiene precio con X ... quedan unidades')
        if valor == "":
            valor = 0

        try:
            laurl.precio        = int(valor)
        except Exception as e:
            print(f"Error al generar precio de  las URLs de {valor}: {e} ")


    return laurl


def saveCampoEnSitio(the_url, campoensitio, the_site, es_error, valor):
    if  not es_error:
        valor = valor[0:600]
        urlobj = SiteURLResults.objects.filter(site=the_site, url=the_url).get()
        campoobj = Campos.objects.filter(nombre=campoensitio).get()
        campoennsitioobj = CamposEnSitio.objects.filter(site=the_site, campo=campoobj).get()
        # resultadoanterior, created = Results.objects.update_or_create(
        #     URLResult=urlobj, 
        #     campoEnSitio=campoennsitioobj,
        #     defaults={'es_error': es_error, 'valor' : valor},
        # )

        # if campoobj.guardar_historico:
        #     old_valor    = resultadoanterior.valor
        #     old_date     = resultadoanterior.updated
        
        #     if old_valor != valor:
        #         print(f'  old_valor={old_valor} valor={valor}')  
        #         ResultsHistory.objects.get_or_create(
        #             FromResult=resultadoanterior, 
        #             defaults={'Oldvalor': old_valor, 'OldDate' : old_date},
        #         )
            

### Grabar pagina
##### Grabar URLs
def saveData(site, data):
    # print(data)
    MyUrls   = data[0]["linksSelector"]
    cuenta1 = 0
    for myUrl in MyUrls:
        urlObj, created = urlSave(site, MyUrls[cuenta1])
        
        cuenta1 = cuenta1 + 1


    if cuenta1 > 0:
        cuenta = 0
        for linea in data:
            # cuenta = 0
            columnas = linea.keys()
            for columna in columnas:
                # print(columna)
                if columna != "linksSelector":
                    datos = data[cuenta][columna]
                    cuenta_rec = 0
                    for dato in datos:
                        # print(data[0]["linksSelector"][cuenta_rec], dato)
                        try:
                            saveCampoEnSitio(data[0]["linksSelector"][cuenta_rec],columna, site, False, dato)
                        except Exception as e:
                            print(str(e))
                        cuenta_rec = cuenta_rec + 1
                cuenta = cuenta + 1



def loadProductSelenium(driver, como, que_busca, que_obtiene, metaopcion ):
    

    try:
        es_error =  False
        if como == "valorfijo":
            retorna = que_busca
        if como == "css selector":
            # elemento = find_element((driver, como, que_busca))
            elemento = driver.find_element(By.CSS_SELECTOR, que_busca)
            retorna = elemento.get_attribute(que_obtiene)
            if que_obtiene == "text" :
                retorna = elemento.text
        elif como == "xpath":
            elemento = driver.find_element(By.XPATH,("//meta[@name='description']"))
            retorna = elemento.getAttribute(que_busca)
        elif como == "meta":
            searrch = "//meta[@"+metaopcion+ "='"+  que_busca +"']"
            
            elementos = driver.find_elements(By.XPATH,searrch)
            retorna = ""
            for elemento in elementos:
                retorna = elemento.get_attribute(que_obtiene)
                # print(retorna)
    except Exception as e:
        # print(f'como={como}, que_busca={que_busca} que_obtiene={que_obtiene} error={str(e)}')
        es_error  = True
        # retorna = "Errror"
        retorna = str(e)[0:640]

    return {"es_error": es_error, "valor":retorna}

def click_element(driver, by, selector):
    try:
        element = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((by, selector))
            )

        if element:
            element.click()

    except Exception as e:
        print(str(e))


def find_element(driver, by, selector):
    element = WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((by, selector))
    )
    return element

def find_elements(driver,  by, selector):
    try:
        # driver.find_element(by_what, que_busca)
        elements = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((by, selector))
        )

    except NoSuchElementException:
        return 0
    except Exception as e:
        return 0
    return elements

    
    # return elements

###################
# Generales
# ###################
# def saveScannError(errorUrl,ErrorField,errorStr):
#     obj, created = ScanErrors.objects.update_or_create(
#         URLResult=errorUrl, 
#         campoEnSitio=ErrorField,
#         defaults={'theerror' : errorStr},
#     )

def add_page(site, page, to_num_page):
    # sufijo = "/"  ## Cugat al parercer

    sufijo = ""
    page_suffix = ""
    if site.page_suffix:
        page_suffix = site.page_suffix
    else:
        page_suffix = ""
    if to_num_page > 1:
        sufijo = site.page_parameter +str(to_num_page) + page_suffix

    URL = site.siteURL + page.page + sufijo
    if site.url_suffix:
        URL = URL + "&" + site.url_suffix

    return URL

def checkIfProcessRunning(processName, kill=False):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                if kill:
                    proc.kill()
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def GetAllSiteMap():
    sites = Site.objects.filter(siteSearch='sitemap', enable=True).all()
    
    for site in sites:
        if site.sitemap_url != '':
            siteMapUrl = site.sitemap_url
            GetSiteMap(site, siteMapUrl)

def GetSiteMap(site, siteMapUrl):

    try:
        sitemap, sitemap_entries = get_sitemap_contents(siteMapUrl)
    except:
        print("error")
        return
        
    for entry in sitemap_entries:

        if sitemap.get("sitemap_type") == 'xml_sitemap_index':
            mifecha = entry.get('lastmod')
            if mifecha:
                mifecha = parse_date(mifecha)
            else:
                mifecha = parse_date('2022-10-24')
            try:
                obj_siteMap, created = SiteMap.objects.update_or_create(
                    site=site,  
                    loc=entry.get('loc'),
                    sitemap_type=sitemap.get("sitemap_type"),
                    lastmod=mifecha
                    )
            except:
                print(f'GetSiteMap: error {site.siteName}')
            GetSiteMap(site, entry.get('loc'))

    return 

def getCampoDef(nombre_campo, site):
    campoField = Campos.objects.filter(nombre=nombre_campo).get()
    arr_campo = []
    try:
        campo_sitio = CamposEnSitio.objects.filter(site=site,campo=campoField,enabled=True).get()
    except ObjectDoesNotExist:
        return arr_campo
    
    try:
        selCampos = SelectorCampo.objects.filter(campo=campo_sitio).all()
        
        for selCampo in selCampos:
            campo = {
                'SelectorCampoID': selCampo.id,
                'nombre': campoField.nombre,
                'campoQueGraba': campoField.campoQueGraba,
                'multiple': campoField.es_multiple,
                'es_click': campoField.es_click,
                'como':  selCampo.selector,
                'que_busca': selCampo.que_busca,
                'meta': selCampo.meta_opcion,
                'que_obtiene': selCampo.que_obtiene,
                'evita': campo_sitio.evita,
                'printit': campo_sitio.printit,
                'removeChars': selCampo.removeChars,
                'split_return_by':  selCampo.split_return_by,
                'split_get_element': selCampo.split_get_element
            }
            
            arr_campo.append(campo)
            
    except ObjectDoesNotExist:
        print('sale2')
        return arr_campo

    return arr_campo

    # nombres = pd.unique(c[['articulo__nombre']].values.ravel('K'))
    # c2 = np.unique(c[['articulo__nombre', 'articulo__envase']].values)
    # c2 = pd.concat([c['articulo__nombre'],c['articulo__envase'],c['articulo__grados2']]).unique()
    # c2 = c.drop_duplicates()
    
    # nombres = c.articulo__nombre.value_counts()
    # medidas = c.articulo__medida_cant.value_counts()
    # grados  = c.articulo__grados2.value_counts()
    # envases = c.articulo__envase.value_counts()

    # print(nombres)
    # # print(c.articulo__nombre.value_counts())
    # for nombre in nombres:
    #     print(nombre)

    # if este_grados == 0 and este_medida_cant == 0 and este_envase == "":
            #     df_matches = c.loc[
            #         (c['lo__unidades']       == este_unidades) & 
            #         (c['articulo__pk']      != este_pk)
            #     ]
            # if este_grados == 0 and este_medida_cant == 0 and este_envase != "":
            #     df_matches = c.loc[
            #         (c['lo__unidades']       == este_unidades) & 
            #         (c['lo__envase']         == este_envase) & 
            #         (c['articulo__pk']      != este_pk)
            #     ]
            # if este_grados == 0 and este_medida_cant != 0 and este_envase == "":
            #     df_matches = c.loc[
            #         (c['lo__unidades']       == este_unidades) & 
            #         (c['lo__medida_cant']    == este_medida_cant) & 
            #         (c['articulo__pk']      != este_pk)
            #     ]
            # if este_grados == 0 and este_medida_cant != 0 and este_envase != "":
            #     df_matches = c.loc[
            #         (c['lo__unidades']       == este_unidades) & 
            #         (c['lo__medida_cant']    == este_medida_cant) & 
            #         (c['lo__envase']         == este_envase) & 
            #         (c['articulo__pk']      != este_pk)
            #     ]

            # if este_grados != 0 and este_medida_cant == 0 and este_envase == "":
            #     df_matches = c.loc[
            #         (c['lo__unidades']       == este_unidades) & 
            #         (c['lo__grados2']        == este_grados) & 
            #         (c['articulo__pk']      != este_pk)
            #     ]
            # if este_grados != 0 and este_medida_cant == 0 and este_envase != "":
            #     df_matches = c.loc[
            #         (c['lo__unidades']       == este_unidades) & 
            #         (c['lo__grados2']        == este_grados) & 
            #         (c['lo__envase']         == este_envase) & 
            #         (c['articulo__pk']      != este_pk)
            #     ]
            # if este_grados != 0 and este_medida_cant != 0 and este_envase == "":
            #     df_matches = c.loc[
            #         (c['lo__unidades']       == este_unidades) & 
            #         (c['lo__grados2']        == este_grados) & 
            #         (c['lo__medida_cant']    == este_medida_cant) & 
            #         (c['articulo__pk']      != este_pk)
            #     ]
            # if este_grados != 0 and este_medida_cant != 0 and este_envase != "":
            #     df_matches = c.loc[
            #         (c['lo__unidades']       == este_unidades) & 
            #         (c['lo__grados2']        == este_grados) & 
            #         (c['lo__medida_cant']    == este_medida_cant) & 
            #         (c['lo__envase']         == este_envase) & 
            #         (c['articulo__pk']      != este_pk)