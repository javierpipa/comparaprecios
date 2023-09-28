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

import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from tabulate import tabulate

from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist

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

    # Marcas
    marcas = articulos.values('marca__nombre','marca_id').annotate(Count('id', distinct=True)).order_by()
    filtro['marcas'] = marcas

    # Grados
    grados = articulos.values('grados2').order_by('grados2').annotate(Count('id', distinct=True))
    filtro['grados'] = grados

    # Envase
    envase = articulos.values('envase').exclude(envase=None).annotate(Count('id', distinct=True)).order_by()
    filtro['envase'] = envase

    # Color
    color = articulos.values('color').annotate(Count('id', distinct=True)).order_by()
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

    # Unidad de talla
    medida_um = articulos.values('talla').annotate(Count('id', distinct=True)).order_by()
    filtro['talla'] = medida_um

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

def createRule(si_marca, 
                si_nombre, 
                si_grados, 
                si_medida_cant,
                si_unidades,
                si_envase,
                si_talla,
                entonces_marca='',
                entonces_nombre='',
                entonces_grados='',
                entonces_medida_cant='',
                entonces_unidades='',
                entonces_envase='',
                entonces_talla='',
                tipo='',
              ):
    # entonces_nombre = reemplaza_palabras(entonces_nombre)
    if si_nombre == '':
        si_nombre = None

    if si_envase == '':
        si_envase = None
    

    if entonces_envase == '':
        entonces_envase = None

    try:
        obj = Unifica.objects.get(
                si_marca=si_marca,
                si_nombre=si_nombre, 
                si_grados2=si_grados, 
                si_medida_cant=si_medida_cant,
                si_unidades=si_unidades,
                si_envase=si_envase,
                si_talla=si_talla
        )
        

        obj.entonces_marca          = entonces_marca
        obj.entonces_nombre         = entonces_nombre

        if entonces_envase != '':
            obj.entonces_envase         = entonces_envase

        if entonces_grados != 0:
            obj.entonces_grados2        = entonces_grados

        if entonces_medida_cant !=0:
            obj.entonces_medida_cant    = entonces_medida_cant

        obj.entonces_unidades       = entonces_unidades
        obj.entonces_talla          = entonces_talla
        obj.tipo                    = tipo
        obj.contador                = 0
        obj.automatico              = True
        print('Regla modificada')
        obj.save()

    except Unifica.DoesNotExist:
        obj = Unifica(
                si_marca=si_marca,
                si_nombre=si_nombre, 
                si_grados2=si_grados, 
                si_medida_cant=si_medida_cant,
                si_unidades=si_unidades,
                si_envase=si_envase,
                si_talla=si_talla,
                entonces_marca=entonces_marca,
                entonces_nombre=entonces_nombre,
                entonces_grados2=entonces_grados,
                entonces_medida_cant=entonces_medida_cant,
                entonces_unidades=entonces_unidades,
                entonces_envase=entonces_envase,
                entonces_talla=entonces_talla,
                tipo=tipo,
                contador=0,
                automatico=True
        )
        obj.save()
    except Exception as error:
        print(f'MAL !! si_marca={si_marca} si_nombre={si_nombre} si_grados={si_grados}, si_medida_cant={si_medida_cant}, si_unidades={si_unidades}, si_envase={si_envase}')
        print("An exception occurred:", type(error).__name__, "–", error) # An exception occurred: ZeroDivisionError – division by zero
        
    
###############

def generate_rules(rules, debug):
    if not debug:
        for rule in rules:
            si_marca        = Marcas.objects.filter(id=rule['si_marca']).get()
            entonces_marca  = Marcas.objects.filter(id=rule['entonces_marca']).get()
            if  si_marca                != entonces_marca               or \
                rule['si_nombre']       != rule['entonces_nombre']      or \
                rule['si_grados']       != rule['entonces_grados']      or \
                rule['si_medida_cant']  != rule['entonces_medida_cant'] or \
                rule['si_unidades']     != rule['entonces_unidades']    or \
                rule['si_envase']       != rule['entonces_envase']      or \
                rule['si_talla']        != rule['entonces_talla']    :   
                createRule(
                    si_marca,
                    rule['si_nombre'],
                    rule['si_grados'],
                    rule['si_medida_cant'],
                    rule['si_unidades'],
                    rule['si_envase'],
                    rule['si_talla'],

                    entonces_marca,
                    rule['entonces_nombre'],
                    rule['entonces_grados'],
                    rule['entonces_medida_cant'],
                    rule['entonces_unidades'],
                    rule['entonces_envase'],
                    rule['entonces_talla'],
                    rule['tipo'],
                )
            else:
                print('no agrega regla')


def is_vendedores_in(a_quienes, b_quienes, debug=False):
    si_esta = False
    # arr_a_quienes   = ' '.join(str(e) for e in a_quienes)
    # arr_b_quienes   = ' '.join(str(e) for e in b_quienes)

    if debug:
        print(f'a_quienes{a_quienes}')
        print(f'b_quienes{b_quienes}')

    for a in a_quienes:
        # print(f'a={a}')
        for b in b_quienes:
            if b == a:
                si_esta = True

    return si_esta

def check_sailers(c, minimo, fuz_level=70, debug=False):
    for cuenta0, row0 in c.iterrows():
        arr_quienes_vender  = row0['quienesvenden']
        cuantos_venden = len(arr_quienes_vender)
        if cuantos_venden <= minimo:
            if debug:        
                df_debug = c.loc[
                    (c['articulo__pk']       == row0['articulo__pk'])
                ]
                print('**************************** ME INTERESA *********************************')
                print(tabulate(df_debug, headers = 'keys', tablefmt = 'fancy_grid'))

            este_pk             = row0['articulo__pk']
            este_marca          = row0['articulo__marca']
            este_nombre         = row0['lo__nombre']
            este_grados         = row0['lo__grados2']
            este_medida_cant    = row0['lo__medida_cant']
            este_unidades       = row0['lo__unidades']
            este_envase         = row0['lo__envase']
            este_ean_13         = row0['lo__ean_13']
            arr_quienes_vender  = row0['quienesvenden']
            este_envase         = este_envase.strip()
            if este_grados == 0 and este_medida_cant == 0 and este_envase == "":
                df_matches = c.loc[
                    (c['lo__unidades']       == este_unidades) & 
                    (c['articulo__pk']      != este_pk)
                ]
            if este_grados == 0 and este_medida_cant == 0 and este_envase != "":
                df_matches = c.loc[
                    (c['lo__unidades']       == este_unidades) & 
                    (c['lo__envase']         == este_envase) & 
                    (c['articulo__pk']      != este_pk)
                ]
            if este_grados == 0 and este_medida_cant != 0 and este_envase == "":
                df_matches = c.loc[
                    (c['lo__unidades']       == este_unidades) & 
                    (c['lo__medida_cant']    == este_medida_cant) & 
                    (c['articulo__pk']      != este_pk)
                ]
            if este_grados == 0 and este_medida_cant != 0 and este_envase != "":
                df_matches = c.loc[
                    (c['lo__unidades']       == este_unidades) & 
                    (c['lo__medida_cant']    == este_medida_cant) & 
                    (c['lo__envase']         == este_envase) & 
                    (c['articulo__pk']      != este_pk)
                ]

            if este_grados != 0 and este_medida_cant == 0 and este_envase == "":
                df_matches = c.loc[
                    (c['lo__unidades']       == este_unidades) & 
                    (c['lo__grados2']        == este_grados) & 
                    (c['articulo__pk']      != este_pk)
                ]
            if este_grados != 0 and este_medida_cant == 0 and este_envase != "":
                df_matches = c.loc[
                    (c['lo__unidades']       == este_unidades) & 
                    (c['lo__grados2']        == este_grados) & 
                    (c['lo__envase']         == este_envase) & 
                    (c['articulo__pk']      != este_pk)
                ]
            if este_grados != 0 and este_medida_cant != 0 and este_envase == "":
                df_matches = c.loc[
                    (c['lo__unidades']       == este_unidades) & 
                    (c['lo__grados2']        == este_grados) & 
                    (c['lo__medida_cant']    == este_medida_cant) & 
                    (c['articulo__pk']      != este_pk)
                ]
            if este_grados != 0 and este_medida_cant != 0 and este_envase != "":
                df_matches = c.loc[
                    (c['lo__unidades']       == este_unidades) & 
                    (c['lo__grados2']        == este_grados) & 
                    (c['lo__medida_cant']    == este_medida_cant) & 
                    (c['lo__envase']         == este_envase) & 
                    (c['articulo__pk']      != este_pk)
                ]
            

            cuantos_encuento = len(df_matches)
            if cuantos_encuento > 0:

                # Tokenizar las palabras
                word_tokens = [word for sentence in df_matches['lo__nombre'] for word in word_tokenize(sentence)]
                # Calcular la frecuencia de las palabras
                word_freq = FreqDist(word_tokens)
                # Encontrar la palabra más común
                if word_freq:
                    most_common_word = word_freq.most_common(1)[0][0]
                else:
                    most_common_word = ''

                best_fuz = 0
                best_id  = None
                if debug:        
                    print(f'cuantos encuento={cuantos_encuento}')
                    print(tabulate(df_matches, headers = 'keys', tablefmt = 'psql'))
                for cuenta02, row02 in df_matches.iterrows():
                    if  not is_vendedores_in(arr_quienes_vender, row02['quienesvenden']):
                        otro_pk             = row02['articulo__pk']
                        otro_marca          = row02['articulo__marca']
                        otro_nombre         = row02['lo__nombre']
                        otro_grados         = row02['lo__grados2']
                        otro_medida_cant    = row02['lo__medida_cant']
                        otro_unidades       = row02['lo__unidades']
                        otro_envase         = row02['lo__envase']
                        otro_ean_13         = row02['lo__ean_13']
                        arr_otro_vender     = row0['quienesvenden']

                        fuz         = fuzz.token_sort_ratio(este_nombre, otro_nombre)
                        
                        if fuz < fuz_level:
                            paso_nombre = otro_nombre.replace(most_common_word,'')
                            fuz         = fuzz.token_sort_ratio(este_nombre, paso_nombre)

                        if fuz > best_fuz and fuz > fuz_level:
                            if debug:        
                                print(f'check_sailers --- Grados Modificado !! fuz={fuz}, fuz_level={fuz_level}')

                            best_fuz            = fuz
                            best_id             = otro_pk
                            best_grados         = otro_grados
                            best_nombre         = otro_nombre
                            best_medida_cant    = otro_medida_cant
                            best_envase         = otro_envase
                            linea               = cuenta02
                            

                if best_id:
                    c.at[cuenta0,'lo__nombre']  = best_nombre 
                    c.at[cuenta0,'lo__grados2'] = best_grados

                    c.at[cuenta0,'r_nombre'] = 1
                    c.at[cuenta0,'r_grados'] = 1
                    c.at[cuenta0,'rule'] = f'check_sailers 1'


                    # if este_envase == '' and otro_envase !='' and row02['r_envase'] == 0 \

                    if este_envase == "":
                        c.at[cuenta0,'lo__envase']      = best_envase
                        c.at[cuenta0,'rule']            = f'check_sailers envase'
                        c.at[cuenta0,'r_envase'] = 1

                    if este_medida_cant == 0:
                        c.at[cuenta0,'lo__medida_cant'] = best_medida_cant

                    c = add_vendedores(c, cuenta0, linea)
                    
                    # else:
                    #     if debug:        
                    #         print('Vendedor ya esta')
            
            
    return c
def actualizar_registros(data_df):
    # Iterar sobre cada fila del dataframe
    for index, row in data_df.iterrows():
        # Definir las columnas que queremos comparar
        columns_to_compare = ['lo__nombre', 'lo__medida_cant', 'lo__unidades', 'lo__grados2', 'lo__envase']
        
        # Si 'lo__ean_13' tiene un valor, usarlo para identificar coincidencias
        if pd.notnull(row['lo__ean_13']) and row['lo__ean_13'] != '':
            matching_rows = data_df[data_df['lo__ean_13'] == row['lo__ean_13']]
        else:
            # Identificar coincidencias basándonos en una comparación difusa de 'lo_nombre' (con umbral del 80%), y coincidencias exactas en 'lo_unidades' y 'lo__medida_cant'
            matching_rows = data_df[
                (data_df['lo__unidades'] == row['lo__unidades']) & 
                (data_df['lo__medida_cant'] == row['lo__medida_cant']) &
                (data_df['lo__nombre'].apply(lambda x: fuzz.ratio(x, row['lo__nombre']) >= 80 if pd.notnull(x) else False)) & 
                (data_df.index != index)
            ]
        
        # Iterar sobre las filas que coinciden y verificar la columna 'quienesvenden'
        for match_index, match_row in matching_rows.iterrows():
            if match_index == index:
                # Ignorar la fila actual
                continue

            # Verificar si 'quienesvenden' es diferente
            if row['quienesvenden'] != match_row['quienesvenden']:
                # Modificar las columnas con prefijo 'lo_' en la fila coincidente para igualar las de la fila principal
                data_df.at[match_index, columns_to_compare] = row[columns_to_compare]

    return data_df


def check_pd(c, check_nombre=False, check_ean=False, check_grados=False, check_medida=False, check_envase=False, fuz_level=70, debug=False):
    for cuenta0, row0 in c.iterrows():
        este_pk             = row0['articulo__pk']
        este_marca          = row0['articulo__marca']
        este_nombre         = row0['lo__nombre']
        este_grados         = row0['lo__grados2']
        este_medida_cant    = row0['lo__medida_cant']
        este_unidades       = row0['lo__unidades']
        este_envase         = row0['lo__envase']
        este_ean_13         = row0['lo__ean_13']
        este_get_price      = row0['get_price']
        arr_quienes_vender  = row0['quienesvenden']

        if debug:        
            print(f'==================================')
            print(f'este_nombre={este_nombre} este_grados={este_grados} este_medida_cant={este_medida_cant} arr_quienes_vender={arr_quienes_vender} este_ean={este_ean_13}')
            print(f'==================================')
        if check_ean:
            df_matches = c.loc[
                (c['lo__ean_13']        == este_ean_13) & 
                (c['articulo__pk']      != este_pk)
            ]
            for cuenta02, row02 in df_matches.iterrows():
                otro_pk             = row02['articulo__pk']
                otro_nombre         = row02['lo__nombre']
                otro_grados         = row02['lo__grados2']
                otro_medida_cant    = row02['lo__medida_cant']
                otro_unidades       = row02['lo__unidades']
                otro_envase         = row02['lo__envase']
                otro_ean_13         = row02['lo__ean_13']
                # print('1')
                if row02['r_nombre'] == 0 :
                    # print('2')
                    if row0['r_nombre'] == 0:
                        # print('3')
                        if  not is_vendedores_in(arr_quienes_vender, row02['quienesvenden']):
                            # print('4 Inicio')
                            if debug:        
                                print('SUPERIOR')
                                print(tabulate(df_matches, headers = 'keys', tablefmt = 'psql'))
                            

                            ### Cual esta mal ??
                            ##### revisa grados
                            if este_grados == 0 and otro_grados == 0: 
                                ### Ambos grados iguales, no se corrige
                                pass
                            elif este_grados == 0 and otro_grados != 0: 
                                c.at[cuenta0,'r_grados'] = 1
                                c.at[cuenta0,'lo__grados2']  = otro_grados
                                c.at[cuenta0,'rule'] = 'check_ean grados 1'
                            elif este_grados != 0 and otro_grados == 0: 
                                c.at[cuenta02,'r_grados'] = 1
                                c.at[cuenta02,'lo__grados2']  = este_grados
                                c.at[cuenta02,'rule'] = 'check_ean grados 2'
                                print(f'cuenta origen={cuenta0} cuenta destino={cuenta02}')


                            pon_nombre = este_nombre
                            if este_envase == '' and otro_envase == '':
                                ### Ambos grados iguales, no se corrige
                                pass
                            elif este_envase == '' and otro_envase != '':
                                c.at[cuenta0,'lo__envase']  = otro_envase
                                c.at[cuenta0,'r_envase'] = 1
                                c.at[cuenta0,'rule'] = 'check_ean envase 1'
                            elif este_envase != '' and otro_envase == '':
                                c.at[cuenta02,'lo__envase']  = este_envase
                                c.at[cuenta02,'r_envase'] = 1
                                c.at[cuenta02,'rule'] = 'check_ean envase 2'
                            
                            if este_medida_cant > otro_medida_cant :
                                c.at[cuenta02,'lo__medida_cant']  = este_medida_cant
                                c.at[cuenta02,'r_medida'] = 1
                            else:
                                c.at[cuenta0,'lo__medida_cant']  = otro_medida_cant
                                c.at[cuenta0,'r_medida'] = 1

                            if este_unidades != otro_unidades :
                                c.at[cuenta02,'lo__unidades']  = este_unidades    

                            c.at[cuenta02,'lo__nombre']  = pon_nombre
                            c.at[cuenta02,'r_nombre'] = 1
                            c.at[cuenta02,'r_ean'] = 1
                            if c.at[cuenta02,'rule'] == '' :
                                c.at[cuenta02,'rule'] = 'check_ean'
                            
                            c = add_vendedores(c, cuenta0, cuenta02)
                            # print('4 Fin')
                            if debug:        
                                df_matches = c.loc[
                                    (c['lo__ean_13']        == este_ean_13) 
                                ]
                                print('inferior')
                                print(tabulate(c, headers = 'keys', tablefmt = 'psql'))
        else:  
            df_matches = c.loc[
                (c['lo__medida_cant']   == este_medida_cant) & 
                (c['lo__unidades']      == este_unidades) &
                (c['articulo__pk']      != este_pk)
            ]
        
        # if debug:
        #     print(tabulate(df_matches, headers = 'keys', tablefmt = 'psql'))

        for cuenta02, row02 in df_matches.iterrows():
            otro_pk             = row02['articulo__pk']
            otro_marca          = row02['articulo__marca']
            otro_nombre         = row02['lo__nombre']
            otro_grados         = row02['lo__grados2']
            otro_medida_cant    = row02['lo__medida_cant']
            otro_unidades       = row02['lo__unidades']
            otro_envase         = row02['lo__envase']
            otro_get_price      = row02['get_price']
            arr_otro_vender     = row02['quienesvenden']
           
            # if este_pk != otro_pk:
            fuz         = fuzz.token_sort_ratio(este_nombre, otro_nombre)
            
            fuz_precio = fuzz.token_sort_ratio(este_get_price, otro_get_price)

            if fuz > fuz_level:        ### Hay proximidad de nombre
                if debug:
                    print(f'basado_en_linea={cuenta0} fuz={fuz}  linea = {cuenta02} vs otro_nombre={otro_nombre}')

                if check_grados:
                    # print('Y deberia entrar aca 1')
                    if este_grados == 0 and otro_grados !=0:
                        # print('pasa grados 1 ')
                        if row02['r_grados'] == 0:
                            # print('pasa grados 2 ')
                            if  not is_vendedores_in(arr_quienes_vender, arr_otro_vender):
                                # print('pasa grados 3 ')
                                c.at[cuenta0,'lo__grados2'] = otro_grados
                                c.at[cuenta0,'r_grados'] = 1

                                c.at[cuenta0,'r_nombre'] = 1
                                c.at[cuenta0,'lo__nombre'] = otro_nombre

                                c.at[cuenta0,'rule'] = 'check_grados+Nombre'

                                c = add_vendedores(c, cuenta0, cuenta02)
                if check_envase:
                    if este_envase == '' and otro_envase !='' and row02['r_envase'] == 0 \
                        and not is_vendedores_in(arr_quienes_vender, arr_otro_vender, debug=True):
                        c.at[cuenta0,'lo__envase'] = otro_envase
                        c.at[cuenta0,'r_envase'] = 1
                        c.at[cuenta0,'rule'] = 'REGLA check_envase'
                        c = add_vendedores(c, cuenta0, cuenta02)
                if check_nombre:
                    if row02['r_nombre'] == 0 and row0['r_nombre'] == 0 and este_medida_cant == otro_medida_cant \
                        and not is_vendedores_in(arr_quienes_vender, arr_otro_vender):
                        if fuz_precio > fuz_level:
                        
                            c.at[cuenta0,'r_nombre'] = 1
                            c.at[cuenta0,'lo__nombre'] = otro_nombre
                            c.at[cuenta0,'rule'] = 'check_nombre'

                            # c.at[cuenta02,'r_nombre'] = 1
                            print(f'********* check_nombre *********** {fuz_precio}')
                            c = add_vendedores(c, cuenta0, cuenta02)
            
                

    return c

def add_vendedores(arreglo_datos, linea_destino, linea_origen):
    destino  = arreglo_datos.at[linea_destino,'quienesvenden']
    origen   = arreglo_datos.at[linea_origen,'quienesvenden']

    destino_array   = list(destino)
    origen_array    = list(origen)
    
    for dato in origen_array:
        destino_array.append(int(dato))

    # print(arr_aquienes)
    arreglo_datos.at[linea_destino,'quienesvenden']   = destino_array
    
    arreglo_datos.at[linea_origen,'quienesvenden']   = ''
    

    return arreglo_datos

def imprime_reglas(rules):
    print("--------inicio reglas -----------")
    contador = 0
    for rule in rules:
        contador = contador + 1
        
        print(f"#{contador}:{rule['tipo']},{rule['fuz']},nombre={rule['si_nombre']},grados={rule['si_grados']},si_m_cant={rule['si_medida_cant']},si_env={rule['si_envase']},si_und={rule['si_unidades']} '--', etc_nombre={rule['entonces_nombre']},etc_grados={rule['entonces_grados']},etc_m_cant={rule['entonces_medida_cant']}, etc_envase={rule['entonces_envase']} ,etc_und={rule['entonces_unidades']}")
        
    print("--------fin    reglas -----------")


def find_best_match(df_matches, este_nombre):
    """
    Encuentra el mejor match en df_matches para este_nombre basado en una puntuación de coincidencia difusa.
    """
    best_fuz = 0
    best_match = None
    
    for _, row in df_matches.iterrows():
        otro_nombre = row['lo__nombre']
        fuz = fuzz.token_sort_ratio(este_nombre, otro_nombre)
        
        if fuz > best_fuz:
            best_fuz = fuz
            best_match = row
    
    return best_match

def update_record(c, current_index, best_match, reason):
    print("Dentro de update_record:", c.columns)
    """
    Actualiza el registro en c en el índice current_index con los valores de best_match.
    """
    c.at[current_index, 'lo__nombre'] = best_match['lo__nombre']
    c.at[current_index, 'lo__grados2'] = best_match['lo__grados2']
    c.at[current_index, 'lo__medida_cant'] = best_match['lo__medida_cant']
    c.at[current_index, 'r_grados'] = 1
    c.at[current_index, 'r_nombre'] = 1
    c.at[current_index, 'rule'] = reason
    
    # Nota: La función add_vendedores debería estar definida antes de llamar a esta función
    c = add_vendedores(c, current_index, best_match.name)
    
    return c

def find_best_match_for_medida(c, row2, valor, debug=False):
    este_nombre = row2['lo__nombre']
    este_pk = row2['articulo__pk']
    a_medida_cant = row2['lo__medida_cant']
    a_unidades = row2['lo__unidades']
    arr_quienes_vender = row2['quienesvenden']
    
    df_matches = c.loc[
        (c['lo__medida_cant'] != a_medida_cant) & 
        (c['lo__unidades'] == a_unidades) & 
        (c['articulo__pk'] != este_pk)
    ]
    
    if debug:
        print('se encuentran')
        print(tabulate(df_matches, headers='keys', tablefmt='psql'))
    
    return find_best_match(df_matches, este_nombre)

def check_medida_cant(c, df_medida_cant_uno, debug=False):
    for _, row in df_medida_cant_uno.iterrows():
        valor = row['lo__medida_cant']
        matching_records = c.loc[c['lo__medida_cant'] == valor]
        
        for cuenta2, row2 in matching_records.iterrows():
            best_match = find_best_match_for_medida(c, row2, valor, debug=debug)
            
            if best_match is not None:
                c = update_record(c, cuenta2, best_match, 'check_medida_cant')
    
    return c



def check_grados_func(c, df_grados_uno, debug=False):
    for cuenta, row in df_grados_uno.iterrows():
        valor = row['lo__grados2']
        matching_records = c[(c['lo__grados2'] == valor) & (c['lo__grados2'] == 0.0)]
        
        for cuenta2, row2 in matching_records.iterrows():
            este_nombre = row2['lo__nombre']
            este_pk = row2['articulo__pk']
            a_medida_cant = row2['lo__medida_cant']
            a_unidades = row2['lo__unidades']
            
            df_matches = c[(c['lo__medida_cant'] == a_medida_cant) & 
                           (c['lo__unidades'] == a_unidades) & 
                           (c['lo__grados2'] != valor) & 
                           (c['articulo__pk'] != este_pk)]
            
            if debug:
                print(tabulate(df_matches, headers='keys', tablefmt='psql'))
            
            best_match = find_best_match(df_matches, este_nombre)
            
            if best_match is not None:
                c = update_record(c, cuenta2, best_match, 'check_grados')
                
    return c


def get_value_counts_df(c, column_name):
    """
    Obtiene un DataFrame con el recuento de valores únicos en la columna especificada que tienen un recuento de 1.
    
    :param c: DataFrame de entrada
    :param column_name: Nombre de la columna para obtener el recuento de valores
    :return: DataFrame con el recuento de valores únicos con un recuento de 1
    """
    value_counts = c[column_name].value_counts()
    value_counts_uno = value_counts.loc[lambda x : x==1]
    return value_counts_uno.to_frame('counts').reset_index()


def intenta_marca(marca_obj, debug):
    num_rules_created   = int(Settings.objects.get(key='num_rules_created').value)
    
    reglas              = []

    sites = Vendedores.objects.select_related('articulo','vendidoen')
    sites = sites.filter(articulo__marca=marca_obj)
    sites = sites.exclude(vendidoen__precio=0)
    sites = sites.exclude(vendidoen__error404=True)
    sites = sites.values('vendidoen__site')
    sites = sites.annotate(total=Count('vendidoen__site'))
    sites = sites.order_by('-total')
    if not sites:
        return
    
    all_sites   = list(sites)
    
    if debug:
        print(f'all_sites={all_sites} ')

    all_sites_arr = []
    for site in all_sites:
        all_sites_arr.append(site['vendidoen__site'])

    articles_from_all = Vendedores.objects.select_related('articulo','vendidoen')
    articles_from_all = articles_from_all.filter(articulo__marca=marca_obj)
    articles_from_all = articles_from_all.filter(vendidoen__site__in=all_sites_arr)
    articles_from_all = articles_from_all.exclude(vendidoen__precio=0)
    articles_from_all = articles_from_all.exclude(vendidoen__error404=True)
    articles_from_all = articles_from_all.distinct()
    c = create_PD_From(articles_from_all)
    if debug:
        print(tabulate(c, headers = 'keys', tablefmt = 'double_outline'))

    
    # # Tokenizar las palabras
    # word_tokens = [word for sentence in c['articulo__nombre'] for word in word_tokenize(sentence)]

    # # Calcular la frecuencia de las palabras
    # word_freq = FreqDist(word_tokens)

    # # Encontrar la palabra más común
    # most_common_word = word_freq.most_common(1)[0][0]


    ## Caso grados que haya solo 1 registro
    if debug:
        print("######### Check Grados ###############")
    
    
    # df_medida_cant_uno = get_value_counts_df(c, 'lo__medida_cant')
    # c = check_medida_cant(c, df_medida_cant_uno, debug=debug)


    df_grados_uno = get_value_counts_df(c, 'lo__grados2')
    # c = check_grados_func(c, df_grados_uno, debug=debug)
    

    
    if debug:
        print(f'cuantos = {len(df_grados_uno)}')
        print(tabulate(df_grados_uno, headers = 'keys', tablefmt = 'psql'))

    for cuenta, row in df_grados_uno.iterrows():
        valor       = row['lo__grados2']
        a           = c.loc[c['lo__grados2'] == valor]
        for cuenta2, row2 in a.iterrows():
            if debug:        
                print(tabulate(a, headers = 'keys', tablefmt = 'psql'))
            
            este_nombre         = row2['lo__nombre']
            este_pk             = row2['articulo__pk']
            a_grados            = row2['lo__grados2']
            a_unidades          = row2['lo__unidades']
            a_medida_cant       = row2['lo__medida_cant']
            a_envase            = row2['lo__envase']
            arr_quienes_vender  = row2['quienesvenden']
            if float(a_grados) == 0.0 :
                df_matches = c.loc[
                        (c['lo__medida_cant']   == a_medida_cant) & 
                        (c['lo__unidades']      == a_unidades) & 
                        (c['lo__grados2']      != valor) &
                        (c['articulo__pk']      != este_pk)
                    ]
                if debug:
                    print('se encuentran')
                    print(tabulate(df_matches, headers = 'keys', tablefmt = 'psql'))
                best_fuz = 0
                best_id  = None
                if len(df_matches) > 0:
                    for cuenta3, row3 in df_matches.iterrows():
                        otro_nombre         = row3['lo__nombre']
                        otro_pk             = row3['articulo__pk']
                        fuz         = fuzz.token_sort_ratio(este_nombre, otro_nombre)
                        print(f'y hace fuz={fuz}')
                        if fuz > best_fuz:
                            best_fuz    = fuz
                            best_id     = cuenta3
                            best_grados = row3['lo__grados2']
                            best_nombre = row3['lo__nombre']
                    if best_id:
                        c.at[cuenta2,'lo__nombre'] = best_nombre
                        c.at[cuenta2,'lo__grados2'] = best_grados
                        c.at[cuenta2,'r_grados'] = 1
                        c.at[cuenta2,'r_nombre'] = 1
                        c.at[cuenta2,'rule'] = 'Check Grados'
                        add_vendedores(c, cuenta2, cuenta3)
                        


    # fuz_levels = (90,89,88, )
    # c = actualizar_registros(c, cuantos_campos_comparo=4)

    fuz_levels = (88, )
    for fuzl in fuz_levels:
        if debug:
            print("Check- EAN")
        c = check_pd(c, check_nombre=False, check_ean=True,  check_grados=False, check_medida=False, check_envase=False,  fuz_level=fuzl, debug=debug)

        if debug:
            print("Check- Grados")
        c = check_pd(c, check_nombre=False, check_ean=False, check_grados=True,  check_medida=False, check_envase=False,  fuz_level=fuzl, debug=debug)

        if debug:
            print("Check- envase")
        c = check_pd(c, check_nombre=False, check_ean=False, check_grados=False, check_medida=False, check_envase=True,   fuz_level=fuzl, debug=debug)

        if debug:
            print("Check- Nombre")
        c = check_pd(c, check_nombre=True,  check_ean=False, check_grados=False, check_medida=False, check_envase=False,  fuz_level=fuzl, debug=debug)
    

    if num_rules_created > 10:
        fuz_levels = (93,)
    else:
        fuz_levels = (93,)

    for fuzl in fuz_levels:
        if debug:
            print(f"Check sailers min=1 fuz={fuzl}")
        c = check_sailers(c, 1, fuzl, debug)

        if debug:
            print(f"Check sailers min=2 fuz={fuzl}")
        c = check_sailers(c, 2, fuzl, debug)

    

    # ###### Casos especiales, donde hay 1 registro solamente
    # ### Caso envase que haya solo 1 registro
    # envase_list    = c.lo__envase.value_counts() 
    # envase_uno     = envase_list.loc[lambda x : x==1]
    # df_envase_uno  = envase_uno.to_frame('counts').reset_index()
    # df_envases     = envase_list.to_frame('counts').reset_index()
    
    
    # if debug:
    #     print("######### Check Envases ###############")
    #     print(tabulate(df_envases, headers = 'keys', tablefmt = 'psql'))

    # for cuenta, row in df_envase_uno.iterrows():
    #     valor       = row['lo__envase']
    #     a           = c.loc[c['lo__envase'] == valor]
    #     for cuenta3, row3 in df_envases.iterrows():
    #         envase      = row3['lo__envase']
    #         # a_quienes   = ' '.join(str(e) for e in row3['quienesvenden'])

    #         fuz         = fuzz.token_sort_ratio(valor, envase)
    #         if fuz !=100 and fuz > 80:
    #             b   = c.loc[ (c['lo__envase']            == valor)  ] 

    #             if debug:
    #                 print(f'fuz={fuz}')
    #                 print(tabulate(b, headers = 'keys', tablefmt = 'psql'))

    #             for cuenta4, row4 in b.iterrows():
    #                 # if not is_vendedores_in(row3['quienesvenden'], row4['quienesvenden']):
    #                 #     print("Envases - Bien.. No esta.. agregarlo")

    #                 c.at[cuenta4,'lo__envase'] = envase
    #                 c.at[cuenta4,'r_envase'] = 1


    ### Caso medida_cant que haya solo 1 registro
    # if debug:
    #     print("######### Check medida_cant ###############")
        
    # medida_cant_list    = c.lo__medida_cant.value_counts() 
    # medida_cant_uno     = medida_cant_list.loc[lambda x : x==1]
    # df_medida_cant_uno  = medida_cant_uno.to_frame('counts').reset_index()
    # if debug:
    #     print(tabulate(df_medida_cant_uno, headers = 'keys', tablefmt = 'psql'))
    
    # for cuenta, row in df_medida_cant_uno.iterrows():
    #     valor       = row['lo__medida_cant']
    #     a           = c.loc[c['lo__medida_cant'] == float(valor)]
    #     for cuenta2, row2 in a.iterrows():
    #         no_id       = row2['articulo__pk']
    #         a_nombre    = row2['articulo__nombre']
    #         a_grados    = row2['articulo__grados2']
    #         a_unidades  = row2['articulo__unidades']
    #         a_quienes   = ' '.join(str(e) for e in row2['quienesvenden'])

    #         if debug:
    #             print(tabulate(a, headers = 'keys', tablefmt = 'psql'))

    #         b           = c.loc[(c['articulo__nombre']      == a_nombre) & \
    #                             (c['articulo__grados2']     == float(a_grados)) & \
    #                             (c['articulo__unidades']    == float(a_unidades)) & \
    #                             (c['articulo__pk']          != no_id)  ] 
            
    #         for cuenta3, row3 in b.iterrows():
    #             b_quienes = ' '.join(str(e) for e in row3['quienesvenden'])
    #             if not is_vendedores_in(row2['quienesvenden'], row3['quienesvenden']):
    #                 # print("Bien.. No esta.. agregarlo")
                
    #                 c.at[cuenta2,'lo__medida_cant'] = c.at[cuenta3,'articulo__medida_cant']
    #                 c.at[cuenta2,'r_medida'] = 1

    #                 narray = list(row3['quienesvenden'])
    #                 arr_aquienes = a_quienes.split()
    #                 for dato in arr_aquienes:
    #                     narray.append(int(dato))
    #                 c.at[cuenta2,'quienesvenden']   = narray

    #             else:
    #                 print("Si esta.. NO agregar")
                    
    #         if debug:
    #             print(tabulate(b, headers = 'keys', tablefmt = 'psql'))
    


    # for cuenta, row in df_nombres_uno.iterrows():
    #     valor       = row['lo__nombre']
    #     a           = c.loc[c['lo__nombre'] == valor]
    #     # print(tabulate(a, headers = 'keys', tablefmt = 'psql'))

    #     for cuenta2, row2 in a.iterrows():
    #         no_id           = row2['articulo__pk']
    #         a_grados        = row2['lo__grados2']
    #         a_unidades      = row2['lo__unidades']
    #         a_medida_cant   = row2['lo__medida_cant']
    #         a_envase        = row2['lo__envase']
    #         a_quienes   = ' '.join(str(e) for e in row2['quienesvenden'])
            
    #         if len(row2['quienesvenden']) > 1:
    #             continue
            
    #         b           = c.loc[(c['lo__unidades']    == float(a_unidades)) & \
    #                             (c['lo__envase']      == a_envase) & \
    #                             (c['articulo__pk']    != no_id)  ] 
            
            
    #         for cuenta3, row3 in b.iterrows():
    #             b_nombre        = row3['lo__nombre']
    #             fuz             = fuzz.token_sort_ratio(valor, b_nombre)
    #             if fuz !=100 and fuz > 90:
    #                 # print(f'{b_nombre}, fuz={fuz}')
    #                 c.at[cuenta2,'lo__nombre'] = c.at[cuenta3,'lo__nombre']
    #                 c.at[cuenta2,'r_nombre'] = 1
    #                 break
    #             # else:
    #             #     print(f'menos !!  {b_nombre}, fuz={fuz}')
    #         if debug:
    #             print(tabulate(b, headers = 'keys', tablefmt = 'psql'))


    ### Caso nombre que haya solo 1 registro
    if debug:
        print("######### Check NOMBRES ###############")
    nombres_list        = c.lo__nombre.value_counts()
    nombres_list_uno    = nombres_list.loc[lambda x : x==1]
    df_nombres_uno      = nombres_list_uno.to_frame('counts').reset_index()
    if debug:
        print(f'cuantos = {len(df_nombres_uno)}')
        print(tabulate(df_nombres_uno, headers = 'keys', tablefmt = 'psql'))
    for cuenta, row in df_nombres_uno.iterrows():
        valor       = row['lo__nombre']
        a           = c.loc[c['lo__nombre'] == valor]
        for cuenta2, row2 in a.iterrows():      ### Por cada tipo de nombre
            if debug:
                print(tabulate(a, headers = 'keys', tablefmt = 'psql'))

            este_nombre         = row2['lo__nombre']
            este_pk             = row2['articulo__pk']
            a_grados            = row2['lo__grados2']
            a_unidades          = row2['lo__unidades']
            a_medida_cant       = row2['lo__medida_cant']
            a_envase            = row2['lo__envase']
            este_get_price      = row2['get_price']
            arr_quienes_vender  = row2['quienesvenden']
            df_matches = c.loc[
                    (c['lo__medida_cant']   == a_medida_cant) & 
                    (c['lo__unidades']      == a_unidades) & 
                    (c['lo__envase']        == a_envase) & 
                    (c['lo__grados2']       == a_grados) & 
                    (c['lo__nombre']        != este_nombre)
                ]
            if debug:
                print(tabulate(df_matches, headers = 'keys', tablefmt = 'psql'))
            
            best_fuz = 0
            best_id  = None
            if len(df_matches) > 0:
                for cuenta3, row3 in df_matches.iterrows():
                    # print('casi')
                    arr_otro_vender     = row3['quienesvenden']
                    pon_nombre          = row3['lo__nombre']
                    otro_get_price      = row3['get_price']
                    if not is_vendedores_in(arr_quienes_vender, arr_otro_vender):
                        fuz         = fuzz.token_sort_ratio(este_nombre, pon_nombre)
                        fuz_precio  = fuzz.token_sort_ratio(este_get_price, otro_get_price)
                        if fuz > best_fuz:
                            best_fuz    = fuz
                            best_id     = cuenta3
                            best_nombre = row3['lo__nombre']
                if best_id and best_fuz >= 90 and fuz_precio > 90:
                    c.at[cuenta2,'lo__nombre']  = best_nombre
                    c.at[cuenta2,'r_nombre'] = 1
                    c.at[cuenta2,'rule'] = f'Check NOMBRES fuz={best_fuz}'
                    add_vendedores(c, cuenta2, cuenta3)

    
    # for nombre in nombres:
    for cuenta0, row0 in c.iterrows():
        if      row0['articulo__nombre']        != row0['lo__nombre'] \
            or  row0['articulo__medida_cant']   != row0['lo__medida_cant'] \
            or  row0['articulo__unidades']      != row0['lo__unidades'] \
            or  row0['articulo__grados2']       != row0['lo__grados2'] \
            or  row0['articulo__envase']        != row0['lo__envase'] \
            or  row0['articulo__talla']         != row0['lo__talla']    :
            reglas.append({
                'si_marca'              : row0['articulo__marca'],
                'si_nombre'             : row0['articulo__nombre'],
                'si_grados'             : row0['articulo__grados2'],
                'si_medida_cant'        : row0['articulo__medida_cant'],
                'si_unidades'           : row0['articulo__unidades'],
                'si_envase'             : row0['articulo__envase'],
                'si_talla'              : row0['articulo__talla'],
                'entonces_marca'        : row0['articulo__marca'],
                'entonces_nombre'       : row0['lo__nombre'],
                'entonces_grados'       : row0['lo__grados2'],
                'entonces_medida_cant'  : row0['lo__medida_cant'],
                'entonces_unidades'     : row0['lo__unidades'],
                'entonces_envase'       : row0['lo__envase'],
                'entonces_talla'        : row0['lo__talla'],
                'tipo'                  : row0['rule'],
                'fuz'                   : 100,
            })

    if debug:
        imprime_reglas(reglas)
    
    sin_reglas = 0
    for cuenta2, row2 in c.iterrows():
        if row2['r_grados'] == 0 and row2['r_medida'] == 0 and row2['r_nombre'] == 0 and row2['r_envase'] == 0:
            sin_reglas = sin_reglas + 1
    print(f"{marca_obj.slug} articulos a {len(c)} art. Con reglas={len(reglas)}")
    if debug:
        print(tabulate(c, headers = 'keys', tablefmt = 'psql'))
        print('===================')

    if not debug:
        generate_rules(reglas, debug)

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

def create_PD_From(recordset):
    df_articulos = pd.DataFrame(list(recordset.values('articulo__pk',
                                                      'articulo__marca',
                                                      'articulo__nombre',
                                                      'articulo__medida_cant', 
                                                      'articulo__unidades', 
                                                      'articulo__grados2', 
                                                      'articulo__ean_13',
                                                      'articulo__envase',
                                                      'articulo__talla',
                                                      )
                                    )
                                )
    
    df_articulos['rule']                    = ''
    df_articulos['get_price']               = 0
    df_articulos['lo__nombre']              = ''
    df_articulos['lo__medida_cant']         = 0
    df_articulos['lo__unidades']            = 0
    df_articulos['lo__grados2']             = 0
    df_articulos['lo__envase']              = ''
    df_articulos['lo__talla']               = ''
    df_articulos['lo__ean_13']              = ''
    
    df_articulos['r_nombre']    = 0
    df_articulos['r_medida']    = 0
    df_articulos['r_grados']    = 0
    df_articulos['r_ean']       = 0
    df_articulos['r_envase']    = 0

    
    df_articulos['quienesvenden']   = {}

    ## Fill some cols
    for cuenta, row in df_articulos.iterrows():
        art = Articulos.objects.get(pk=row['articulo__pk'])
        df_articulos.at[cuenta,'get_price']             = art.get_price
        df_articulos.at[cuenta,'quienesvenden']         = art.quienesvenden()
        if art.envase:
            df_articulos.at[cuenta,'articulo__envase']      = art.envase.strip()
        else:
            df_articulos.at[cuenta,'articulo__envase']      = ''


        df_articulos.at[cuenta,'lo__nombre']            = art.nombre
        df_articulos.at[cuenta,'lo__medida_cant']       = art.medida_cant
        df_articulos.at[cuenta,'lo__unidades']          = art.unidades
        df_articulos.at[cuenta,'lo__grados2']           = art.grados2
        if art.envase:
            df_articulos.at[cuenta,'lo__envase']            = art.envase.strip()
        else:
            df_articulos.at[cuenta,'lo__envase']            = ''
        df_articulos.at[cuenta,'lo__talla']            = art.talla
        df_articulos.at[cuenta,'lo__ean_13']           = art.ean_13


    return df_articulos

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

def check_grados_b(b, fuz_level=70, reglas=[]):
    ### Veamos como esta b.
    for cuenta2, row2 in b.iterrows():
        ## Si no tengo grados
        if row2['articulo__grados2'] == 0 :
            ## Chequeo los a
            no_id = row2['articulo__pk']
            best_fuz = 0
            ## Tienen grados los otros ?
            for cuenta3, row3 in b.iterrows():
                if no_id != row3['articulo__pk'] :
                    the_fuz = fuzz.token_sort_ratio(row2['articulo__nombre'], row3['articulo__nombre'])

                    if the_fuz > best_fuz:
                        if row3['articulo__grados2'] > 0 and row2['r_grados'] == 0:
                            best_fuz            = the_fuz 
                            best_grados         = row3['articulo__grados2']
                            b.at[cuenta2,'r_grados'] = 1

                        if row3['articulo__medida_cant'] > 0 and row2['r_medida'] == 0:
                            best_medida_cant    = row3['articulo__medida_cant']
                            b.at[cuenta2,'r_medida'] = 1
                        else:
                            best_medida_cant    = row2['articulo__medida_cant']

                        if row3['articulo__envase'] != '' and row2['r_envase'] == 0:
                            best_envase         = row3['articulo__envase']
                            b.at[cuenta2,'r_envase'] = 1
                        else:
                            best_envase         = row2['articulo__envase']
            if best_fuz > fuz_level:
                reglas.append({
                    'si_marca':             row2['articulo__marca'],
                    'si_nombre':            row2['articulo__nombre'],
                    'si_grados':            row2['articulo__grados2'],
                    'si_medida_cant':       row2['articulo__medida_cant'],
                    'si_unidades':          row2['articulo__unidades'],
                    'si_envase'  :          row2['articulo__envase'],
                    'entonces_marca' :      row2['articulo__marca'],
                    'entonces_nombre' :     row2['articulo__nombre'],
                    'entonces_grados' :     best_grados,
                    'entonces_medida_cant': best_medida_cant,
                    'entonces_unidades' :   row2['articulo__unidades'],
                    'entonces_envase'   :   best_envase,
                    'tipo': f'grados de b en b fuz={best_fuz}',
                    'fuz': best_fuz,
                })
                
                break
            
    return b, reglas
####################
def buscar_articulos_con_y_sin_grados(df):
    articulos_sin_grados = []
    articulos_con_grados = []
    for i, row in df.iterrows():
        # si el artículo tiene valores en la columna "grados", buscamos otro registro con el mismo nombre, medida_cant y unidades pero sin valor en la columna "grados"
        # if pd.notnull(row['grados2']):
        if row['grados2'] != 0:
            filtro_sin_grados = (df['nombre'] == row['nombre']) & (df['medida_cant'] == row['medida_cant']) & (df['unidades'] == row['unidades']) & (df['grados2'] == 0)
            art_sin_grados = df.loc[filtro_sin_grados]
            # si se encuentra otro registro idéntico sin grados, lo agregamos a la lista
            if not art_sin_grados.empty:
#                 print(art_sin_grados.iloc[0]['nombre'])
                articulos_sin_grados.append({
                    'si_marca':             art_sin_grados.iloc[0]['marca'], 
                    'si_nombre':            art_sin_grados.iloc[0]['nombre'], 
                    'si_grados2':           art_sin_grados.iloc[0]['grados2'], 
                    'si_medida_cant':       art_sin_grados.iloc[0]['medida_cant'], 
                    'si_unidades':          art_sin_grados.iloc[0]['unidades'], 
                    'si_envase':            art_sin_grados.iloc[0]['envase'], 
                    'entonces_marca':       row['marca'],
                    'entonces_nombre':      row['nombre'],
                    'entonces_grados2':     row['grados2'],
                    'entonces_medida_cant': row['medida_cant'], 
                    'entonces_unidades':    row['unidades'], 
                    'entonces_envase':      row['envase'], 
                })

    return articulos_sin_grados

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