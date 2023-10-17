from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from itertools import combinations


import chromedriver_autoinstaller
##

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path


##




try:
    chromedriver_autoinstaller.install() 
except:
    print('Sin conexcion')


from django.db.models import Count, Q
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError
import re
import html
import unidecode

import requests
from bs4 import BeautifulSoup
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer


from precios.pi_functions import (
    set_headers,
    getCampoDef,
    check_exists, 
    get_resultadoSelenium,
    loadProductBeautifulSoup,
    saveUrlData,
    click_element,
    add_page,
)
from precios.pi_supermercado import (
    product_details_fromsoup,
    product_details_fromsoup_breadcrumb,
)

from datetime import datetime, timedelta

from precios.models import (
    SelectorCampo,
    Campos,
    CamposEnSitio,
    DONDESEUSA,
    PAGECRAWLER,
    Unifica,
    Marcas,
    Site,
    Articulos,
    Vendedores,
    SiteURLResults,
    MarcasSistema,
    Settings,
    ReemplazaPalabras,
    AllPalabras,
    TIPOPALABRA,
    Unifica,
)

#### Get URL's
def set_beautifulBrowser(url,laurl):
    headers = set_headers()
    try:
        page2 = requests.get(url, headers)
    except requests.HTTPError:
        laurl.error404 = True
        laurl.save()
        return
    except:
        laurl.error404 = True
        laurl.save()
        return
    browser = BeautifulSoup(page2.content, "html.parser")

    return browser

def set_browser(headless=True):
    options = Options()
    if headless:
        options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    options.add_argument("--enable-javascript")
    
    # browser = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),options=options)

    #  Instalacion de chrome version espercifica
    # wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.90-1_amd64.deb
    # dpkg -i google-chrome-stable_114.0.5735.90-1_amd64.deb
    # apt-mark hold google-chrome-stable
    # google-chrome-stable --version

    ## update precios_siteurlresults set unidades = 1 ;
    
    browser = webdriver.Chrome(options=options)

    browser.implicitly_wait(2)

    return browser

def getSiteProperties(site):
    siteclicks = getCampoDef('mayordeedad',site)
    arr_campo404 = getCampoDef('Pagina404',site)
    arr_linksSelector = getCampoDef('linksSelector',site)
    ItemsEnListado = getCampoDef('ItemsEnListado',site)
    
    ## Next Page
    arr_nextPage = getCampoDef('nextPage',site)

    # maxPages
    arr_maxPages = getCampoDef('MaxPages',site)

    listaDeCampos  =  Campos.objects.filter(donde=DONDESEUSA.EN_PRODUCTO)
    campoEnSitioObject = CamposEnSitio.objects.filter(site=site, campo__in=listaDeCampos, enabled=True)

    return siteclicks, \
        arr_campo404, \
        listaDeCampos, \
        campoEnSitioObject, \
        arr_linksSelector, \
        ItemsEnListado,\
        arr_nextPage, \
        arr_maxPages


def get_resultadoBeautiful( soup2, registro):
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

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def url_get(browser, 
            url, 
            laurl, 
            arr_campo404, 
            siteclicks, 
            campoEnSitioObject, 
            site, 
            urlCount,
            numRecords,
            startRecord, 
    ):

    startTime = datetime.now()
    browser.get(url)
    
    
    if arr_campo404:
        salir = False
        for registro in arr_campo404:
            if check_exists(browser, registro['como'], registro['que_busca']):
                print(f'Error 404 url={url}')
                laurl.error404 = True
                laurl.save()
                salir = True
                break
            
        if salir:
            return
        else:
            laurl.error404 = False
            laurl.save()

    # ## Check Mayor de edad
    if siteclicks:
        salir = False
        for registro in siteclicks:
            if check_exists(browser, registro['como'], registro['que_busca']):
                click_element(browser,registro['como'], registro['que_busca'])

    laurl.error404 = False   

    if site.crawler == PAGECRAWLER.SELENIUM:     
        # print(f'try w selenium url={url}')
        ld_json_tags = browser.find_elements(By.XPATH,('//script[@type="application/ld+json"]'))
        ld_response = product_details_fromsoup(ld_json_tags, is_selenium=True)
        ld_response_bread = product_details_fromsoup_breadcrumb(ld_json_tags, is_selenium=True)
    else:
        ld_json_tags = browser.find_all('script', type='application/ld+json')
        ld_response = product_details_fromsoup(ld_json_tags, is_selenium=False)
        ld_response_bread = product_details_fromsoup_breadcrumb(ld_json_tags, is_selenium=False)

    bread_list_arr = []
    if ld_response_bread:
        for item in ld_response_bread:
            bread_list_arr.append(item['name'])

    if ld_response:
        nombre              = ld_response.get("name").lstrip().lower()
        nombre              = nombre.replace('&quot;','')
        if '|' in nombre:
            arr_nombre = nombre.split('|')
            nombre = arr_nombre[0]

        marca         = ld_response.get("brand_name").lstrip().lower()
        # OJO... puede generar cualquier marca
        # if marca !="" and not Marcas.objects.filter(nombre__exact=marca).exists():
        #     Marcas.objects.create(
        #         nombre = marca,
        #     )
        laurl.marca = marca

        laurl.nombre        = nombre
        image               = ld_response.get("image")
        if isinstance(image, dict) or isinstance(image, list):
            laurl.image         = image[0]
        else:
            laurl.image         = image

        stock               = ld_response.get("availability")
        if stock:
            stock           = stock.replace('https://schema.org/','').replace('http://schema.org/','')[0:20]
        laurl.stock         = stock

        laurl.categoria     = ld_response.get("category").lstrip()[0:50]

        gtin13              = ld_response.get("gtin13")
        if gtin13:
            print('gtin13=', gtin13)
            laurl.idproducto    = gtin13.lstrip()
        else:
            idproducto          = ld_response.get("sku")
            if idproducto:
                if isinstance(idproducto, str):
                    laurl.idproducto    = idproducto.lstrip()
        
        descripcion         = ld_response.get("description")
        if descripcion:
            descripcion         = remove_html_tags(descripcion)

        laurl.descripcion   = descripcion
        laurl.priceCurrency = ld_response.get("priceCurrency")

        precio              = ld_response.get("price")
        if precio:
            if not isinstance(precio, int) and not isinstance(precio, float):
                precio              = precio.replace('$','')
                precio_float        = float(precio)
                precio              = int(precio_float)

        if precio == "":
            precio = 0

                
        ### Tags
        laurl.tags.remove()
        if ld_response_bread:
            for item in ld_response_bread:
                laurl.tags.add(str(item['name']))

        laurl.precio        = int(precio)
        laurl.error404 = False
    
        

    for campoensitio in campoEnSitioObject:
        arr_campo = getCampoDef(campoensitio.campo.nombre,site)
        
        
        for registro in arr_campo:
            if site.crawler == PAGECRAWLER.SELENIUM:
                valor, es_error = get_resultadoSelenium(browser,registro)
            else:
                valor, es_error = get_resultadoBeautiful(browser, registro)
                
            selectorcampo = SelectorCampo.objects.get(pk=registro['SelectorCampoID'])
            if not es_error:
                selectorcampo.error_count = 0
                selectorcampo.error_description = ''
                selectorcampo.save()
                break
            else:
                selectorcampo.error_count = selectorcampo.error_count + 1
                selectorcampo.error_description = valor
                selectorcampo.save()

        if not es_error:
            laurl = saveUrlData(campoensitio, laurl, valor)
            campoensitio.save()
        else:
            if campoensitio.campo.campoQueGraba == 'stock':
                laurl = saveUrlData(campoensitio, laurl, '')
            if campoensitio.campo.campoQueGraba == 'nombre':
                laurl.error404 = True
        


    endTime = datetime.now()
    difference = endTime - startTime

    laurl.secondsToGet = int(difference.total_seconds())
    
    laurl.save()
    porcent = round((urlCount / (numRecords - startRecord) * 100),2)
    print(f'Site={site}... {porcent}% ({urlCount} de {numRecords - startRecord}), Tiempo = {int(difference.total_seconds())}')

def savePalabras(palabra):
    try:
        palabraz2  = AllPalabras.objects.filter(palabra=palabra)
        for palabraz in palabraz2:
            palabraz.contador = palabraz.contador + 1
            palabraz.save()
    except ObjectDoesNotExist:
        AllPalabras.objects.update_or_create(palabra=palabra, contador=1)



def reemplaza_palabras(texto):
    
    if texto:
        
        temp = texto.split()
        for palabra_busco in temp:
            savePalabras(palabra_busco)

            if ReemplazaPalabras.objects.filter(palabra__iexact=palabra_busco).exists():
                reemplazo = ReemplazaPalabras.objects.filter(palabra__iexact=palabra_busco).get()
                if reemplazo.reemplazo:
                    texto = texto.replace(palabra_busco, reemplazo.reemplazo)
                else:
                    texto = texto.replace(palabra_busco, '')
                reemplazo.contador = reemplazo.contador + 1
                reemplazo.save()

        ######## Por cada palabra o frase en ReemplazaPalabras
        pal_o_frases = ReemplazaPalabras.objects.all()
        
        for pal_o_frase in pal_o_frases:
            if pal_o_frase.palabra in texto:
                if pal_o_frase.reemplazo:
                    texto = texto.replace(pal_o_frase.palabra, pal_o_frase.reemplazo)
                else:
                    texto = texto.replace(pal_o_frase.palabra, '')
                
                pal_o_frase.contador = pal_o_frase.contador + 1
                pal_o_frase.save()


    return texto


def remove_dollar_sign_and_following(text):
    return re.sub(r'\$.*$', '', text)

# Words with both alphabets and numbers
# Using isdigit() + isalpha() + any()
# res = []
# temp = nombre.split()
def get_palabras_con_numychar(texto):
    ## La función get_palabras_con_numychar toma un string texto como entrada 
    # y devuelve una lista de palabras que contienen al menos un carácter alfabético y al menos un dígito numérico.
    res = []
    temp = texto.split()
    for idx in temp:
        if any(chr.isalpha() for chr in idx) and any(chr.isdigit() for chr in idx):
            res.append(idx.strip())

    return res

def normaliza_talla(talla):
    talla = talla.replace('/', '-').strip()
    match talla:
        case 'talla xs':
            return 'talla xp'
        case 'talla s':
            return 'talla p'
        case 'talla ch':
            return 'talla p'
        case 'talla ch-m':
            return 'talla p-m'
        case 'talla s-m':
            return 'talla p-m'
        case 'talla l':
            return 'talla g'
        case 'talla l-xl':
            return 'talla g-xg'
        case 'talla xl':
            return 'talla xg'
        case 'talla xxl':
            return 'talla xxg'
    
    return talla

def extract_and_remove_weight_range_updated(text):
    match = re.search(r'(\d+([.,]\d+)?\s*[-–a]\s*\d+([.,]\d+)?)\s*kg', text, re.IGNORECASE)
    if match:
        weight_range = match.group(0)
        new_text = re.sub(re.escape(weight_range), '', text)
        return weight_range, new_text.strip()
    return '', text

def replace_comma_in_degrees(text):
    # return re.sub(r'(\d+),(\d+)°', r'\1.\2°', text)
    # Reemplazar comas en grados por puntos
    text = re.sub(r'(\d+),(\d+)°', r'\1.\2°', text)
    # Eliminar 'gl' si está presente al lado derecho de '°'
    text = re.sub(r'°\s*gl', '°', text)
    return text

def get_unidades2(nombre, unidades):
    # Lista de patrones de búsqueda

    busquedas = [
        r'(\d+)\s*(?:packs?|unidades?|pack)\s*x',
        r'(\d+\s*unidades)',
        r'(\d+\s*unidad)',
        r'(\d+\s*unid)',
        r'(\d+\s*uds)',
        r'(\d+)\s*x\s*',
        r'\s*[^\S\n\t]+x\s*(\d+)',
        r'^\d{1,2}'
    ]
    # Bucle para buscar y actualizar unidades y nombre
    for busca in busquedas:
        if unidades == 1:  # Si ya hemos encontrado unidades, no necesitamos seguir buscando
            retorna, nombre = pack_search(nombre, busca)
            if retorna:
                # Elimina cualquier palabra no numérica (como "unidades", "pack", etc.)
                try:
                    retorna = re.sub(r'\D', '', retorna)
                except:
                    pass
                
                unidades = int(retorna)
                return nombre, unidades
            
                # break  # Salir del bucle una vez que se encuentre una coincidencia
    return nombre, 1

## 4.05 Anotacion de tallas
def obtener_talla(nombre, TALLAS):
    talla, nombre           = remueveYGuardaSinSplit(TALLAS, nombre, remover=True, todos=True)
    if talla == '':
        busquedas = [
            ' xxg',
            ' xg',
            ' rn',
            ' xg',
            ' prematuro'
        ]
        for busca in busquedas:
            if talla == '':  # Si ya hemos encontrado talla, no necesitamos seguir buscando
                if busca in nombre:
                    talla = 'talla' + busca
                    nombre = nombre.replace(busca,'')
                    break
    if talla:
        talla = normaliza_talla(talla)

    return talla, nombre

def obtener_marca(nombre, marca):
    ## Revisamos si la marca en la URL existe
    
    # Si la marca no existe, busco en todas las marcas habilitadas si estuviera en el nombre
    if not Marcas.objects.filter(es_marca=True, nombre=marca).exists():
        # Busca marca con espacios a ambos lados
        for posible_marca in Marcas.objects.filter(es_marca=True).values_list('nombre', flat=True).all():
            if ( ' ' + posible_marca +' ' in nombre ) :
                marca  = posible_marca
                nombre = nombre.replace(posible_marca, '')
                return nombre, marca
            
        # Busca marca SIN espacios a ambos lados
        for posible_marca in Marcas.objects.filter(es_marca=True).values_list('nombre', flat=True).all():
            if (  posible_marca  in nombre ) :
                marca  = posible_marca
                nombre = nombre.replace(posible_marca, '')
                return nombre, marca
    
    else:  # Si la marca SI existe, 
        posible_marca = Marcas.objects.filter(es_marca=True, nombre=marca).values_list('nombre', flat=True).get()
        nombre = nombre.replace(posible_marca, '')
        return nombre, marca

    ## Quizas la marca esta des-habilitada
    if not Marcas.objects.filter(es_marca=True, nombre=marca).exists():
        if Marcas.objects.filter(es_marca=False, nombre=marca).exists():
            marca_obj = Marcas.objects.filter(es_marca=False, nombre=marca).get()
            
            if Unifica.objects.filter(si_marca=marca_obj, si_nombre=None, si_grados2=float(0), si_medida_cant=float(0), si_unidades=1,  automatico=False ).exists():
                unifica_obj = Unifica.objects.filter(si_marca=marca_obj, si_nombre=None, si_grados2=float(0), si_medida_cant=float(0), si_unidades=1, automatico=False).first()
                if unifica_obj:
                    marca = unifica_obj.entonces_marca.nombre
            else:
                # print(f'Marca deshabilitada Y no tiene redireccion =|{marca}| Habilito la Marca')
                # marca_obj.es_marca = True
                # marca_obj.save()
                marca = marca_obj.nombre
        else:
            if marca !='' and len(marca) >= 2:
                print(f'Marca no existe =|{marca}| creando Marca')
                marca_obj = Marcas(
                    nombre=marca,
                    es_marca=False
                )
                marca_obj.save()
                marca = marca
            else:
                marca = None

    return nombre, marca

def separate_numbers_from_text(words):
    """
    Separate numbers from adjacent text in a given string.
    Parameters:
        text (str): The input string.
    Returns:
        str: The modified string with numbers separated from adjacent text.
    """
    return re.sub(r'(\d+)([a-zA-Z]+)', r'\1 \2', words)

def to_lowercase(words):
    """Convert all characters to lowercase from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    return new_words

def remove_some_chars(words):
    chars_to_remove= '-'
    new_words = []
    for word in words:
        word = word.replace(chars_to_remove,' ')
        new_words.append(word)

    return new_words

def remove_stopwords(words):
    """Remove stop words from list of tokenized words"""
    new_words = []
    for word in words:
        if word not in stopwords.words('spanish'):
            new_words.append(word)
    return new_words

def normalize(words):
    words = to_lowercase(words)
    words = remove_some_chars(words)
    # words = remove_non_ascii(words)
    
    # words = remove_punctuation(words)
    
    # words = replace_numbers(words)
    words = remove_stopwords(words)
    return words

def get_marcas_que_me_apuntan(marca_default):
    otras_marcas_lst = Unifica.objects.filter(entonces_marca=marca_default, automatico=False).values_list('si_marca__nombre', flat=True).distinct()
    # otras_marcas_lst = Unifica.objects.filter(entonces_marca=marca_default).values_list('si_marca__nombre', flat=True).distinct()
    return otras_marcas_lst

## Create Products
####################
def create_prods(
        urls, 
        registros, 
        articulos_nombre_vacio, 
        debug, 
        campoMarcaObj, 
        listamarcas,
        sin_marca,
        COLORES,
        PALABRAS_INUTILES,
        ENVASES,
        SUJIFOS_NOMBRE,
        TALLAS,
        UMEDIDAS,
        PACKS,
        UNIDADES,
        ean_13_site_ids,
        site,
        articulos_existentes,
        articulos_creados,
        Posicion,
        createRule
    ):
    
    reglas_creados          = 0
    articulos_marca_vacio   = 0

    for url in urls:
        registros = registros + 1
        cantidad    = 1
        grados      = ''
        talla       = ''
        color       = ""
        dimension   = ''
        newmarca    = None
        nombre      = ''
        nombre_original = ''
        descripcion = ''

        if url.nombre :
            nombre = url.nombre
            nombre_original = url.nombre
            descripcion = url.descripcion
        else:
            articulos_nombre_vacio = articulos_nombre_vacio + 1
            ## Si no hay nombre, loop
            continue

        unidades    = url.unidades
        medida_um   = url.medida_um
        medida_cant = url.medida_cant
        newmarca_str = url.marca
        tags        = url.tags.all()

        #######
        nombre = html.unescape(nombre)
        nombre = nombre.lower()
        tipo   = url.tipo 
        debug_nombre('1.- Inicio: '+ nombre, debug)
        #######

        nombre                  = reemplaza_palabras(nombre)
        nombre, newmarca_str    = obtener_marca(nombre, newmarca_str)
        nombre                  = separate_numbers_from_text(nombre)
        
        if Marcas.objects.filter(nombre=newmarca_str).exists():
            newmarca = Marcas.objects.filter(nombre=newmarca_str).get()
            # or not newmarca_str:
        else:
            articulos_marca_vacio = articulos_marca_vacio + 1
            continue

        otras = get_marcas_que_me_apuntan(newmarca)

        nombre = replace_comma_in_degrees(nombre)

        ###----------------------------
        words = nltk.word_tokenize(nombre)
        # print('3->', words)
        words = normalize(words)
        # print('4->', words)
        nombre = ' '.join(words)
        ###----------------------------

        otras_inutiles, nombre = remueveYGuardaSinSplit(otras, nombre, remover=True, todos=True)
        # print(f'otras_inutiles={otras_inutiles}')
        
        # ## 1.4 Remueve colores
        # color, nombre = remueveYGuarda(COLORES, nombre, " ", remover=True, todos=True)
        # color = color.replace(',', '')
        
        # # 1.5 rremueve todos los ', 1 Un'
        inutiles, nombre = remueveYGuardaSinSplit(PALABRAS_INUTILES, nombre, remover=True, todos=True)
        debug_nombre('3.- Inutiles: '+inutiles, debug)
        

        # 2.2 mueve envases
        envase, nombre = remueveYGuarda(ENVASES, nombre, " ", remover=True, todos=True)
        debug_nombre('4.- Envase: '+envase, debug)

        res = get_palabras_con_numychar(nombre)
        for palabra in res:
            palas = re.split('([A-Za-z]+[\d@]+[\w@]*|[\d@]+[A-Za-z]+[\w@]*)', palabra.strip())
            reemplaza_con = ''
            for pa in palas:
                if pa != '':
                    if len(get_palabras_con_numychar(pa)) > 0 :
                        digitos = re.split('(\d+)', pa.strip())
                        for digito in digitos:
                            if digito != '':
                                reemplaza_con = reemplaza_con + digito + ' '
                    else:
                        reemplaza_con = reemplaza_con + pa 

            nombre = nombre.replace(palabra, reemplaza_con) 
            

        nombre,  grados = obtener_grados(nombre)

        ## Quito DE
        nombre =  nombre.replace(' de ',' ')
        
        ## 4 Retiro de sufijos como 'Aprox' 
        agregar_sufijos, nombre = remueveYGuarda(SUJIFOS_NOMBRE, nombre, " ", remover=True, todos=True)
        debug_nombre('5.- Quitar sufijos: '+agregar_sufijos, debug)

        ## 4.05 Anotacion de tallas
        talla, nombre = remueveYGuardaSinSplit(TALLAS, nombre, remover=True, todos=True)
        # debug_nombre('6.- Quitar Tallas: '+talla, debug)

        # 4.2 Unidad de medida
        dimension, nombre = extract_and_remove_weight_range_updated(nombre)

        if medida_cant == 0:
            nombre, medida_cant, medida_um, dimension = get_unidadMedida(nombre, UMEDIDAS)
        

        ## Packs y Sets
        debug_nombre('8.- Quita Pack: ', debug)
        
        arr_nombre = nombre.split(" ")
        for palabra in arr_nombre:
            if palabra in PACKS :
                busca = palabra + '.([0-9]+)'
                retorna, nombre = pack_search(nombre,busca)
                if retorna:
                    nombre = nombre.replace('un. ','')
                    nombre = nombre.replace('unidades ','')
                    if unidades == 1 :
                        unidades = retorna

                    break

        # 4.2 Unidades
        
        
        if unidades == 1:
            nombre, unidades = get_unidades2(nombre, unidades)

        if unidades == 1:
            nombre, unidades = get_unidades(nombre, UNIDADES)
            unidades = float(unidades) * float(cantidad)
            cantidad = 1

            nombre      =  nombre.strip()
            if unidades == 1 and nombre.endswith('x'):
                busca = '.([0-9]+).x'
                retorna, nombre = pack_search(nombre,busca)
                if retorna:
                    unidades = retorna

        debug_nombre('71.- Quitar Unidades: '+ str(unidades), debug)
        
        # 2.2 mueve ennvases NUEVAMENTE
        nombre      =  nombre.rstrip()            
        if envase == "":
            envase, nombre = remueveYGuarda(ENVASES, nombre, " ", remover=True)
            envase = envase.replace(',','')
            
        
        if envase == "" and descripcion:        ## Si envase continua vacio, es posible que el envase este en el campo descripcion
            envase, descripcion_modificada = remueveYGuarda(ENVASES, descripcion, " ", remover=True)
            envase = envase.replace(',','')


        debug_nombre('9.- Quirta envase: '+envase, debug)
                
        nombre      = nombre + ' ' +  agregar_sufijos 
        debug_nombre('11.- agrega sufijos:'+ nombre, debug)


        
        nombre = nombre.rstrip()
        if len(nombre)  > 1:
            if nombre[-1] == ','  or nombre[-1] == '-'  or nombre[-1] == '.' or nombre[-2] == ' y' or nombre[-1] == '+' or nombre[-1] == '–' or nombre[-2] == ' x':
                nombre = nombre[:-1] 
        
            if nombre.startswith(":") or nombre.startswith("!") or nombre.startswith("+") or nombre.startswith(" "):
                nombre = nombre[1:] 
                nombre = nombre.rstrip()

           
        nombre = nombre.rstrip()
        if nombre.endswith('-') or nombre.endswith('.'):
            nombre = nombre[:-1] 

        #     ## Quitamos Pack si aun lo tiene
        if nombre.startswith("pack "):
            nombre      = nombre.replace('pack ',' ')
        

        if nombre.startswith("- "):
            nombre =  nombre.replace('- ','')

        nombre =  remove_dollar_sign_and_following(nombre)
        nombre =  nombre.replace('.',' ')
        nombre =  nombre.replace(',',' ')
        envase =  envase.replace(',',' ')

        nombre      = nombre.strip()
        medida_um   = medida_um.strip()
        dimension   = dimension.strip()
        color       = color.strip()
        envase      = envase.strip()
        talla       = talla.strip()        

        debug_nombre('20.- FINAL: '+ nombre, debug)

        if site.pk in ean_13_site_ids:
            ean_13 = url.idproducto
            if url.idproducto:
                 
                ean_13 = ean_13.rstrip()
                ean_13 = ean_13.lstrip()
                ean_13 = ean_13.replace('[','')
                ean_13 = ean_13.replace('}','')
                if "'" in ean_13:
                    ean_13 = ean_13.replace("'","")
                if '-' in ean_13:
                    ean_arr = ean_13.split('-')
                    ean_13 = ean_arr[0]
                if 'x' in ean_13:
                    ean_arr = ean_13.split('x')
                    ean_13 = ean_arr[0]
                    if unidades == 1:
                        unidades = int(ean_arr[1])
                try:
                    ean_13_int = int(ean_13)
                    ean_13 = str(ean_13_int)
                except ValueError as e:
                    print('Problemas con ean_13 ', ean_13)
                    ean_13 = None
            
        else:
            ean_13 = None
        
        ## 2do cambio hecho, se hace reemplazo de frases o palabras
        nombre = reemplaza_palabras(nombre)
        ## Nuevamente se buscan tallas:
        

        if medida_cant == 0:
            nombre, medida_cant, medida_um, dimension = get_unidadMedida(nombre, UMEDIDAS)

        talla, nombre = obtener_talla(nombre, TALLAS)

        if grados == '':
            nombre,  grados = obtener_grados(nombre)
        # if unidades == 1:
        #     retorna, nombre = pack_search(nombre, '^\d{1,2}')

        ### Revisiones
        reglas      = []
        reglas, newmarca, nombre, grados, medida_cant, unidades, envase, talla = unificacion(newmarca, nombre, grados, medida_cant, unidades, envase, talla, debug, 3, reglas)

        ### Elimino marca que esta dentro del nombre    
        nombre = nombre.replace(newmarca.nombre, '')

        #### Grabacion
        ### Hacer get

        if not grados:
            grados = 0
        
        nombre = nombre.replace('  ', ' ')

        try:
            miarticulo  = Articulos.objects.get(
                marca=newmarca,
                nombre=nombre,
                medida_cant=medida_cant, 
                grados2=grados,
                unidades=unidades,
                envase=envase,
                talla=talla
            )
            articulos_existentes = articulos_existentes  + 1
        except MultipleObjectsReturned:
            print(f'MultipleObjectsReturned  newmarca={newmarca}, nombre={nombre}  medida_cant={medida_cant} grados={grados} unidades={unidades}')
            miarticulo  = Articulos.objects.filter(
                    marca=newmarca,
                    nombre=nombre,
                    medida_cant=medida_cant, 
                    grados2=grados,
                    unidades=unidades,
                    envase=envase,
                    talla=talla,
                ).first()
        except ObjectDoesNotExist:
            
            miarticulo  = create_article(newmarca, nombre, medida_cant, medida_um, nombre_original, unidades, dimension, color, envase, grados, ean_13, tipo, talla, tags)
            articulos_creados = articulos_creados + 1
            

        ### Tipo
        if tipo:
            if tipo.strip() != "":
                miarticulo.tipo = tipo

        if ean_13:
            miarticulo.ean_13 = ean_13

        miarticulo.tags.remove()
        if tags and site.obtiene_categorias:
            for tag in tags:
                miarticulo.tags.add(tag)
        miarticulo.save()


        ### Update ULR con reglas
        for regla in reglas:
            url.reglas.add(regla)

        ### Vendedores
        Vendedores.objects.update_or_create(articulo=miarticulo, vendidoen=url)
        if articulos_creados == 0:
            articulos_creados = 1

        if  registros % 1000 == 0:
            try:
                print(f'{site.siteName} articulos_marca_vacio={articulos_marca_vacio} reglas={reglas_creados} registros= {registros} creados = {articulos_creados} existentes= {articulos_existentes}  vacios={articulos_nombre_vacio}  Tasa={(articulos_existentes/articulos_creados)  * 100}')
            except:
                print("error al generar informe cada 1000")
                pass
        

    # return registros, articulos_creados, articulos_existentes

def create_article(newmarca, nombre, medida_cant, medida_um, nombre_original, unidades, dimension, color, envase, grados, ean_13, tipo, talla, tags):
    new_article = Articulos.objects.create(
            marca=newmarca,
            nombre=nombre,
            medida_cant=medida_cant, 
            medida_um=medida_um,
            nombre_original=nombre_original[0:349],
            unidades=unidades,
            dimension=dimension,
            color=color,
            envase=envase,
            grados2=grados,
            ean_13=ean_13,
            tipo=tipo,
            talla=talla
            
        )
    new_article.tags.set(tags)
    return new_article

def get_dics():
   
    PALABRAS_INUTILES = AllPalabras.objects.filter(tipo=TIPOPALABRA.INUTIL).values_list('palabra',flat=True).all()
    
    SUJIFOS_NOMBRE = AllPalabras.objects.filter(tipo=TIPOPALABRA.SUJIFO_NOMBRE).values_list('palabra',flat=True).all()
    ean_13_site_ids = list(Site.objects.filter(es_ean13=True).values_list('id', flat=True))

        
    UMEDIDAS = AllPalabras.objects.filter(tipo=TIPOPALABRA.UMEDIDA).values_list('palabra',flat=True).all()

    ###     genera columna unidades
    UNIDADES = AllPalabras.objects.filter(tipo=TIPOPALABRA.UNIDAD).values_list('palabra',flat=True).all()
    ## Packs y sets
    # PACKS      = list(Settings.objects.get(key='PACKS').valor_data)
    PACKS = AllPalabras.objects.filter(tipo=TIPOPALABRA.PACKS).values_list('palabra',flat=True).all()
    # 'verde' ,'negro',
    # TALLAS      = list(Settings.objects.get(key='TALLAS').valor_data)
    TALLAS = AllPalabras.objects.filter(tipo=TIPOPALABRA.TALLA).values_list('palabra',flat=True).all()
    # TALLAS   = ('xg/xxg', 'xg', 'xxg', 'xl', 'talla s-xl','talla xl', 'talla s', 'talla m', 'talla xs', 'talla xxg', 'talla xxl', 'talla unica', 'talla ch/m','talla s/m','talla g', 'talla 4', 'talla 6','talla 8','talla 10','tallas: s-m-l') 
    # COLORES = ('cromo','bronce','bicolor','roja','incolora','celeste',  'lila','amarilla','amarillo', 'naranjo', 'rojo', 'gris','cyan', 'beige', 'azul', 'rosada','rosado', 'rosa', 'roza', 'turquesa', 'morado', 'white', 'pink', 'turq', 'blank','silver')
    COLORES = AllPalabras.objects.filter(tipo=TIPOPALABRA.COLOR).values_list('palabra',flat=True).all()
    # ENVASES = ('caja,', 'caja', 'tarro',  'tarro,', 'botella', 'botella,', 'botellin', 'bolsa','bolsa,', 'lata,', 'lata', 'latas','latas,', 'tetra', 'botellon','botellón', 'frasco', 'otellín', 'pote', 'pote,','barril','tetrapak', 'bandeja','sobre', 'malla', 'bidon', 'doypack', 'squeeze','retornable', 'squeze', 'envase flexible', ' pet ', 'pouch')
    ENVASES = AllPalabras.objects.filter(tipo=TIPOPALABRA.ENVASE).values_list('palabra',flat=True).all()
    marcas = SiteURLResults.objects.exclude(marca__exact='', precio=0 ).distinct().all()
    listamarcas = Marcas.objects.values_list('nombre',flat=True).all()

    if len(listamarcas) < 3000 :
        print("menos de  3000")

        for marca in marcas:
            valor = marca.marca
            
            if valor != "" and valor != "." and valor:
                valor = valor.rstrip()
                valor = valor.lstrip()
                valor = valor.lower()
                if not check_sinum(valor):
                    Marcas.objects.update_or_create(nombre=valor)
    ## Adjunto las del sistema
    marcasistema = MarcasSistema.objects.all()


    sin_marca, created = Marcas.objects.update_or_create(nombre='-- sin marca --')
    listamarcas = Marcas.objects.values_list('nombre',flat=True).all()
    
    campoMarcaObj = Campos.objects.get(pk=8)

    return PALABRAS_INUTILES, \
            SUJIFOS_NOMBRE, \
            ean_13_site_ids, \
            UMEDIDAS, \
            UNIDADES, \
            PACKS, \
            TALLAS, \
            COLORES, \
            ENVASES, \
            marcas, \
            listamarcas, \
            marcasistema, \
            sin_marca,\
            listamarcas, \
            campoMarcaObj

def pack_search(en_que_texto, que_busco):
    x = re.findall(que_busco, en_que_texto, re.IGNORECASE)
    if x:
        en_que_texto = re.sub(que_busco, '', en_que_texto, flags=re.IGNORECASE)
        en_que_texto = en_que_texto.strip()
        unidades     = int(x[0])
        return unidades, en_que_texto
    else:
        return None, en_que_texto
    



# def cambiaPalabras(nombre):
#     nombre =  nombre.replace('brujas salamanca',' ')
#     nombre =  nombre.replace('artesanos cochiguaz',' ')
#     nombre =  nombre.replace('artesanos',' ')
#     nombre =  nombre.replace('º gl','° ')
#     nombre =  nombre.replace('º','°')
#     nombre =  nombre.replace('° gl','° ')
#     nombre =  nombre.replace('°c ','° ')
#     nombre =  nombre.replace('Â° ','° ')
#     nombre =  nombre.replace('°g ','° ')
#     nombre =  nombre.replace('°gl','° ')
#     nombre =  nombre.replace('40g ','40° ')
#     nombre =  nombre.replace('40g,','40°,')
#     nombre =  nombre.replace('14g ','14° ')
#     nombre =  nombre.replace('35g ','35° ')
#     nombre =  nombre.replace('35 g°','35° ')
#     nombre =  nombre.replace('4.5 botella','4.5° botella')
#     nombre =  nombre.replace('35 grados ','35° ')
#     nombre =  nombre.replace('14°gl ','14° ')
#     nombre =  nombre.replace('13g, ','13° ')
#     nombre =  nombre.replace('13,5 °, ','13.5° ')
#     nombre =  nombre.replace('13,5 ° gl, ','13.5° ')
#     nombre =  nombre.replace('13,6 gl, ','13.6° ')
#     nombre =  nombre.replace('12.5g, ','12.5° ')
#     nombre =  nombre.replace('14.5g, ','14.5° ')
#     nombre =  nombre.replace('14.2g, ','14.2° ')
#     nombre =  nombre.replace('14g, ','14° ')
#     nombre =  nombre.replace('12g, ','12° ')
#     nombre =  nombre.replace('pierna 15g, ','pierna 15° ')
#     nombre =  nombre.replace('6*90ml','6 un. 90 cc')
#     nombre =  nombre.replace('6*80ml','6 un. 80 cc')
#     nombre =  nombre.replace('3L*3 ','3 un. 3 l')
#     nombre =  nombre.replace('multipack','')
#     nombre =  nombre.replace('4 de 1,5 l','4 un. 1.5 l.')
#     nombre =  nombre.replace('grados ','° ')
#     nombre =  nombre.replace('u.)','unidades )')
#     nombre =  nombre.replace('*',' - ')
#     nombre =  nombre.replace('1,5l','1.5 l')
#     nombre =  nombre.replace('1.2l','1.2 l')
#     nombre =  nombre.replace('1,75l','1.75 l')
#     nombre =  nombre.replace('1.5l','1.5 l')
#     nombre =  nombre.replace('1.5lt','1.5 lt')
#     nombre =  nombre.replace('3.0lt pet','3.0 lt')
#     nombre =  nombre.replace('3.0lt','3.0 lt')
#     nombre =  nombre.replace('- 6unid',' 6 un. ')
#     nombre =  nombre.replace('- 3unid',' 3 un. ')
#     nombre =  nombre.replace('1/4 kg','250 gr.')
#     nombre =  nombre.replace('7kg','7 kg')
#     nombre =  nombre.replace('5kg','5 kg')
#     nombre =  nombre.replace('1kgr','1 kg')
#     nombre =  nombre.replace('1 kgr','1 kg')
#     nombre =  nombre.replace('tripack ','3 un. ')
#     nombre =  nombre.replace('pack x 6','6 un. ')
#     nombre =  nombre.replace('pack x6','6 un. ')
    

    # nombre =  nombre.replace('no retornable','desechable')
    ## Ojo  la  union entre  desechable  y retornable
    # nombre =  nombre.replace('desechable','')
    # nombre =  nombre.replace('no endulzado','sin endulzar')
    # nombre =  nombre.replace('pack x 12','12 un. ')
    # nombre =  nombre.replace('arandanos','arandano')
    # nombre =  nombre.replace('sugar free','sin azucar')
    # nombre =  nombre.replace('rissoto','risotto')
    # nombre =  nombre.replace('arroz primavera','arroz preparado primavera')
    # nombre =  nombre.replace('arroz pre graneado','arroz pregraneado')
    # nombre =  nombre.replace('arroz paella','arroz para paella')
    # nombre =  nombre.replace('arroz especial basmati pregraneado','arroz basmati')
    # nombre =  nombre.replace('arroz curry champinon','arroz especial preparado curry champinon')
    # nombre =  nombre.replace('arroz preparado primavera','arroz especial preparado primavera')
    # nombre =  nombre.replace('arroz primavera','arroz especial preparado primavera')
    # nombre =  nombre.replace('arroz para sushi','arroz preparado sushi')
    # nombre =  nombre.replace('arroz especial sushi grado 1','arroz preparado sushi')
    # nombre =  nombre.replace('arroz food service para sushi','arroz preparado sushi')
    # nombre =  nombre.replace('arroz especial preparado chaufan','arroz preparado chaufan')
    # nombre =  nombre.replace('virg.','virgen ')
    # nombre =  nombre.replace('aero.','aerosol ')
    # nombre =  nombre.replace('desinf.','desinfectante ')
    # nombre =  nombre.replace('desm.','desmenuzado ')
    # nombre =  nombre.replace('beb.','bebida ')
    # nombre =  nombre.replace('inst.','instantanea ')
    # nombre =  nombre.replace('cer. ','cereal ')
    # nombre =  nombre.replace('alim. ','alimento ')
    # nombre =  nombre.replace('c. cristal 4.6° pack botella 355 X 6u ','cerveza cristal 4.6° 355 cc 6 un. ')
    # nombre =  nombre.replace('c. sol ','cerveza sol ')
    # nombre =  nombre.replace(' zero azúcar',' sin azucar ')    
    # nombre =  nombre.replace('relleno con ','relleno ')
    # nombre =  nombre.replace('gelatina en polvo ','gelatina ')

    nombre =  nombre.replace('pack 2 ','2 un. ')
    nombre =  nombre.replace('pack 2x ','2 un. ')
    nombre =  nombre.replace('pack 3 ','3 un. ')
    nombre =  nombre.replace('pack 3x ','3 un. ')
    nombre =  nombre.replace('pack 3un ','3 un. ')
    nombre =  nombre.replace('pack 4 ','4 un. ')
    nombre =  nombre.replace('pack x 4','4 un. ')
    nombre =  nombre.replace('pack 5 ','5 un. ')
    nombre =  nombre.replace('pack 6 ','6 un. ')
    nombre =  nombre.replace('6x ','6 un. ')
    nombre =  nombre.replace('pack 7 ','7 un. ')
    nombre =  nombre.replace('pack 8 ','8 un. ')
    nombre =  nombre.replace('pack 9 ','9 un. ')
    nombre =  nombre.replace('pack 10 ','10 un. ')
    nombre =  nombre.replace('pack 10u ','10 un. ')
    nombre =  nombre.replace('pack 12 ','12 un. ')
    nombre =  nombre.replace('pack 12x ','12 un. ')
    nombre =  nombre.replace('6 latas','6 un. lata')
    nombre =  nombre.replace('12 latas','12 un. lata')
    nombre =  nombre.replace('18 latas','18 un. lata')
    nombre =  nombre.replace(' 4unid ',' 4 un. ')
    nombre =  nombre.replace(' 6unid ',' 6 un. ')
    nombre =  nombre.replace(' botellas,',' botella ')
    nombre =  nombre.replace(' 2 botellas',' 2 un. botella')
    nombre =  nombre.replace('light, 4 de',' 4 un. light')
    nombre =  nombre.replace('2.4lt','2.4 l')
    nombre =  nombre.replace(' 3 en 1',' 3 un. ')
    nombre =  nombre.replace(' 64un',' 64 un. ')
    nombre =  nombre.replace(' 8 und','  8 un. ')
    nombre =  nombre.replace(' 45 und',' 45 un. ')
    nombre =  nombre.replace(' 48un',' 48 un. ')
    nombre =  nombre.replace(' 52un',' 52 un. ')
    nombre =  nombre.replace(' 54 und',' 54 un. ')
    nombre =  nombre.replace(' 68 und',' 68 un. ')
    nombre =  nombre.replace('Display 6 ','6 un. ')
    nombre =  nombre.replace('x54 unid','54 un. ')
    nombre =  nombre.replace('2x1 unidades','2 un. ')
    nombre =  nombre.replace('6X isotonica','6 un. isotonica')
    nombre =  nombre.replace('12 Latas ','12 un. lata ')
    nombre =  nombre.replace('rinde 1 l','')
    nombre =  nombre.replace('2,25l','2.25 lt.')
    nombre =  nombre.replace('2,5l','2.5 lt.')
    nombre =  nombre.replace('2,5mts.','2.5 mt.')
    nombre =  nombre.replace('2,7lt.','2.7 lt.')
    nombre =  nombre.replace('2,8lt','2.8 lt.')
    nombre =  nombre.replace(' zero ',' sin azucar ')
    nombre =  nombre.replace('bebidas','bebida')
    nombre =  nombre.replace('bbonnet','bonnet')
    
    

    ## saco annios
    nombre =  nombre.replace(' 2006','')
    nombre =  nombre.replace(' 2012','')
    nombre =  nombre.replace(' 2013','')
    nombre =  nombre.replace(' 2014','')
    nombre =  nombre.replace(' 2015','')
    nombre =  nombre.replace(' 2016','')
    nombre =  nombre.replace(' 2017','')
    nombre =  nombre.replace(' 2018','')
    nombre =  nombre.replace(' 2019','')
    nombre =  nombre.replace(' 2020','')
    nombre =  nombre.replace(' 2021','')
    nombre =  nombre.replace('ml',' ml')
    nombre =  nombre.replace(',','.')

    return nombre


def getMarca(en_que_texto, que_sitio, campoMarcaObj, listamarcas, sin_marca, debug):
    texto_trabajo = en_que_texto
    
    try:
        camposMarca = CamposEnSitio.objects.filter(site=que_sitio.site, campo=campoMarcaObj, enabled=True).get()
        sitio_con_marrca = True
    except ObjectDoesNotExist:
        sitio_con_marrca = False


    newmarca_str = ''
    newmarca = None
    if sitio_con_marrca:
        if que_sitio.marca != "":

            try:
                newmarca = Marcas.objects.filter(nombre=que_sitio.marca).get()
                newmarca_str = newmarca.nombre
            except ObjectDoesNotExist:
                debug_nombre('1.- Marca buscada : |'+ que_sitio.marca + '|', debug)
                newmarca = Marcas.objects.get(pk=sin_marca.pk)
                newmarca_str = '-- sin marca --'
            
        else:
            sitio_con_marrca = False

    if not sitio_con_marrca:
        texto_trabajo =  ' ' + texto_trabajo + ' '
        texto_trabajo =  texto_trabajo.replace(',',' , ')
        texto_trabajo =  texto_trabajo.replace('.',' . ')
        
        for posible_marrca in listamarcas:

            test_marca = posible_marrca
            if ( ' ' + test_marca+' ' in texto_trabajo ) :
                
                newmarca = Marcas.objects.filter(nombre= posible_marrca).get()
                newmarca_str = newmarca.nombre
                
                break
        
        if not newmarca:
            newmarca = Marcas.objects.get(pk=sin_marca.pk)
            newmarca_str = '-- sin marca --'
        texto_trabajo = texto_trabajo.replace(' , ',',')
        texto_trabajo = texto_trabajo.replace(' . ','.')
        texto_trabajo = texto_trabajo.lstrip()

    if newmarca_str != "":
        old_nombre = texto_trabajo
        texto_trabajo =  texto_trabajo.replace(newmarca_str+'','')
        if texto_trabajo == "":
            texto_trabajo = old_nombre
    
    return texto_trabajo, newmarca, newmarca_str


def debug_nombre(texto,debug):
    if debug:
        print(texto)


def get_unidadMedida( en_que_texto, UMEDIDAS):
    ### Area Unidad de medida

    en_que_texto =  ' ' + en_que_texto + ' '
    
    arr_nombre = en_que_texto.split(" ")

    dimension = ""
    um_text = ""
    um_cant = ""
    palabra = 1
    max_palabras = len(arr_nombre)
    retira = ""
    
    # for um in UMEDIDAS:
    #     pattern = re.compile(rf'(\d+\s*{um})', re.IGNORECASE)
    #     match = re.search(pattern, en_que_texto)
    #     if match:
    #         um_text = match.group(1)
    #         um_cant = re.search(r'(\d+)', um_text).group(1)
    #         en_que_texto = en_que_texto.replace(um_text, '')
    #         en_que_texto = en_que_texto.lstrip()
    #         return en_que_texto, int(um_cant), um, dimension
    
    while True:
        um_text = arr_nombre[len(arr_nombre)-palabra]
        um_cant = arr_nombre[len(arr_nombre)-(palabra+1)]
        um_text = um_text.rstrip()
        
        if um_text in UMEDIDAS and check_sinum(um_cant):
            retira = um_cant  + ' ' + um_text
            break
        else:
            paso = getStringAndNumbers(um_text)
            if len(paso) == 1:
                # print("paso 1")
                um_text = paso[0]
                if um_text in UMEDIDAS :
                    um_cant = '1'
                    retira = um_text
                    break

            if len(paso) == 2:
                print('larrgo  2')

            if len(paso) == 3:
                # print("paso 3")
                um_text = paso[2]
                um_cant = paso[1]
                if um_text in UMEDIDAS :
                    if check_sinum(um_cant):
                        retira = um_cant  + '' + um_text
                        break
                    else:
                        print(um_cant)
                        ## Podria ser:   1/4 o nada
            if len(paso) == 5:
                if paso[2] == "X" or paso[2] == "x":
                    # print("es dimension")
                    um_cant = ""
                    um_text = ""
                    dimension = paso[1]+paso[2]+paso[3]+paso[4]
                    retira = paso[1]+paso[2]+paso[3]+paso[4]
                else:
                    # print("paso 5")
                    # for uni in paso:
                    #     print(uni)
                    if um_text in UMEDIDAS:
                        um_text = paso[4]
                        # um_cant = paso[1]+paso[2]+paso[3]
                        um_cant = paso[1]+paso[3]
                        # retira = um_cant  + '' + um_text
                        retira = paso[1]+paso[2]+paso[3]+paso[4]
                    else:
                        um_cant = ""
                        um_text = ""
                break

        palabra = palabra + 1
        if palabra > max_palabras:
            
            um_text = ""
            um_cant = ""
            break
    
    um_text = normalizeUM(um_text)
    um_cant, um_text = normalizeCANTyUM(um_cant, um_text, True)
    
    if um_cant > 0 :
        medida = str(um_cant) + ' ' + um_text
    else:
        medida =  um_text
    en_que_texto =  en_que_texto.replace(retira,'')

    en_que_texto = en_que_texto.lstrip()

    return en_que_texto, um_cant, um_text, dimension


def getStringAndNumbers( donde):
    return  re.split('(\d+)',donde)


def remueveYGuardaSinSplit( OBJETO, en_que_texto, remover=False, todos=False):
    salir = False
    devuelve_palabra = ''
    en_que_texto = ' ' + en_que_texto + ' '

    for sacable in OBJETO:
        if ' ' + sacable + ' ' in en_que_texto  :
            devuelve_palabra = devuelve_palabra + ' ' + sacable
            if remover:
                en_que_texto = en_que_texto.replace(sacable,' ')

            if not todos:
                salir = True
                break
        
        if salir:
            break
            
    en_que_texto        = en_que_texto.rstrip()
    devuelve_palabra    = devuelve_palabra.strip()

    return devuelve_palabra, en_que_texto


def obtener_grados(frase):
    palabras = frase.split()
    nombre = ""
    grados = None
    for i, palabra in enumerate(palabras):
        if '°' in palabra:
            try:
                grados = float(palabra.replace('°', ''))
            except ValueError:
                nombre += " " + palabra
        elif i == 0:
            nombre += palabra
        else:
            nombre += " " + palabra
    return nombre, grados


def check_sinum( valor):
    valor = valor.replace(".","")
    valor = valor.replace(",","")
    return valor.isdigit()


def get_unidades(en_que_texto, UNIDADES):
    
    unidades = 1

    en_que_texto = en_que_texto.rstrip()
    en_que_texto = en_que_texto + ' '
    arr_nombre = en_que_texto.split(" ")
    palabra = 1
    max_palabras = len(arr_nombre)
    while True:
        um_text = arr_nombre[len(arr_nombre)-palabra]
        um_cant = arr_nombre[len(arr_nombre)-(palabra+1)]
        um_text = um_text.rstrip()
        if um_text in UNIDADES and check_sinum(um_cant):
            um_cant = um_cant.replace(',','.')
            unidades = um_cant
            retira = um_cant  + ' ' + um_text
            en_que_texto =  en_que_texto.replace(retira,'')

            unidades  =  float(unidades)

        palabra = palabra + 1
        if palabra > max_palabras:
            break

    return en_que_texto, unidades


def normalizeCANTyUM(um_cant, um_text, change=True):

    um_cant = um_cant.strip()
    if um_cant == "":
        um_cant = 0
    else:
        um_cant = um_cant.replace(",", ".")

    try:
        um_cant = float(um_cant)
    except:
        print(f'Error en cantidad = {um_cant}')
        um_cant = 1

    if um_text == 'galon' and change:
        um_cant = um_cant * 3.785411784
        um_text = 'lt'

    if um_text == 'cl'  and change:
        um_cant = um_cant * 10
        um_text = 'cc'

    if um_text == 'lt' and um_cant <= 5 and change:
        um_cant = um_cant * 1000
        um_text = 'cc'

    if um_text == 'kg' and um_cant <= 5 and change:
        um_cant = um_cant * 1000
        um_text = 'gr'

    return um_cant, um_text


def normalizeUM(UnMed):
    retorna = UnMed

    if  UnMed == 'c'        or UnMed == 'c.'        or UnMed == 'c,'    or \
        UnMed == 'cc'       or UnMed == 'cc.'       or UnMed == 'cc,'   or \
        UnMed == 'c.c'      or UnMed == 'c.c.'      or UnMed == 'c.c,'  or \
        UnMed == 'cl'       or UnMed == 'cl.'       or UnMed == 'cl,'   or \
        UnMed == 'ml'       or UnMed == 'ml.'       or UnMed == 'ml,' :
        retorna = 'cc' 

    if  UnMed == 'l'         or UnMed == 'l.'        or UnMed == 'l,' or\
        UnMed == 'lt'       or UnMed == 'lt.'       or UnMed == 'lt,' or \
        UnMed == 'lts'      or UnMed == 'lts.'      or UnMed == 'lts,'or \
        UnMed == 'litro'    or UnMed == 'litro.'    or UnMed == 'litro,' or\
        UnMed == 'litros'   or UnMed == 'litros.'   or UnMed == 'litros,' :
        retorna = 'lt' 

    if  UnMed == 'g'        or UnMed == 'g.'        or UnMed == 'g,' or \
        UnMed == 'gr'       or UnMed == 'gr.'       or UnMed == 'gr,' or \
        UnMed == 'grs'      or UnMed == 'grs.'      or UnMed == 'grs,' or \
        UnMed == 'grms'     or UnMed == 'grms.'     or UnMed == 'grms,':
        retorna = 'gr' 
    
    if UnMed == 'watts' :
        retorna = 'w' 

    if UnMed == 'lum' :
        retorna = 'lumenes' 
    
    if UnMed == 'plazas' :
        retorna = 'plaza' 

    if UnMed == 'pulgada' :
        retorna = 'pulgadas' 

    if  UnMed == 'k'        or UnMed == 'k.'        or UnMed == 'k,'    or \
        UnMed == 'kl'       or UnMed == 'kl.'       or UnMed == 'kl,'   or \
        UnMed == 'kg'       or UnMed == 'kg.'       or UnMed == 'kg,'   or \
        UnMed == 'kgr'      or UnMed == 'kgr.'      or UnMed == 'kgr,'  or \
        UnMed == 'kilo'     or UnMed == 'kilo.'     or UnMed == 'kilo,' or \
        UnMed == 'kilos'    or UnMed == 'kilos.'    or UnMed == 'kilos,' :
        retorna = 'kg' 

    if  UnMed == 'm'        or UnMed == 'm.'        or UnMed == 'm,'     or \
        UnMed == 'mt'       or UnMed == 'mt.'       or UnMed == 'mt,'    or \
        UnMed == 'mts'      or UnMed == 'mts.'      or UnMed == 'mts,'   or \
        UnMed == 'metro'    or UnMed == 'metro.'    or UnMed == 'metro,' or \
        UnMed == 'metros'   or UnMed == 'metros.'   or UnMed == 'metros,' :
        retorna = 'mt'

    return retorna


def remueveYGuarda(OBJETO, en_que_texto, split_por, remover=False, todos=False):
    salir = False
    arr_nombre = en_que_texto.split(split_por)[1:]
    devuelve_palabra = ''
    for sacable in OBJETO:
        for palabra in arr_nombre:
            if palabra == sacable or palabra == sacable+'.' or palabra == sacable+',':
                devuelve_palabra = devuelve_palabra + ' ' + palabra
                if remover:
                    en_que_texto = en_que_texto.replace(palabra,'')

                if not todos:
                    salir = True
                    break
        
        if salir:
            break

    en_que_texto = en_que_texto.rstrip()

    return devuelve_palabra, en_que_texto


def unificacion( marca, nombre, grados, medida_cant, unidades, envase, talla, debug, k, reglas):
    if (k>0):
        nombre = " ".join(nombre.split())
        query = Q()
        

        if nombre == '':
            nombre = None
        if not grados:
            grados = 0
        if envase == '':
            envase = None
        # reglas      = []
        
        ##  Fix completo
        query = Q()
        query.add(Q(si_marca=marca), Q.AND)
        query.add(Q(si_nombre__iexact=nombre), Q.AND)
        query.add(Q(si_grados2=float(grados)), Q.AND)
        query.add(Q(si_medida_cant=float(medida_cant)), Q.AND)
        query.add(Q(si_unidades=unidades), Q.AND)
        query.add(Q(si_envase=envase), Q.AND)
        query.add(Q(si_talla=talla), Q.AND)
        uniones = Unifica.objects.filter(query)  
        for uni in uniones:
            debug_nombre('1.- unificacion: '+ marca.nombre + ' Rule: '+ str(uni.pk) + ' ' , debug)
            reglas.append(uni)
            uni.contador = uni.contador + 1
            uni.save()
            
            marca       = uni.entonces_marca
            nombre      = uni.entonces_nombre
            grados      = uni.entonces_grados2
            medida_cant = uni.entonces_medida_cant
            unidades    = uni.entonces_unidades
            envase      = uni.entonces_envase
            talla       = uni.entonces_talla

        

        if not nombre :
            nombre = marca.nombre
        
        reglas, marca, nombre, grados, medida_cant, unidades, envase, talla = unificacion(marca, nombre, grados, medida_cant, unidades, envase, talla, debug, k-1, reglas)
        

    return reglas, marca, nombre, grados, medida_cant, unidades, envase, talla

