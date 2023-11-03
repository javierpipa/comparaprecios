from precios.models import (
    Settings,
    Site, 
    Marcas, 
    Articulos,
    Vendedores,
    Unifica,
)

# Required Libraries
from django.db.models import F, Sum, Count, Min, Max
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from tabulate import tabulate

from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def is_vendedores_in(a_quienes, b_quienes, debug=False):
    # Verificar si alguna de las listas está vacía
    if not a_quienes or not b_quienes:
        # print(f'---> NOT  a_quienes={a_quienes} b_quienes={b_quienes} ')
        return True
    
    # Verificar si algún elemento de a_quienes está en b_quienes
    si_esta = any(a in b_quienes for a in a_quienes)

    if debug:
        print(f'---> a_quienes={a_quienes} b_quienes={b_quienes} esta={si_esta}')

    return si_esta

def check_sailers(c, minimo, fuz_level=70, debug=False):
    '''
    This function performs checks on the 'sailers' in the DataFrame.

    Parameters:
    - c (DataFrame): The DataFrame to be processed.
    - minimo (int): The minimum threshold for performing the check.
    - debug (bool): Flag to print debug information.

    Returns:
    - DataFrame: The processed DataFrame.
    '''

    for _, row in c.iterrows():
        if len(row['quienesvenden']) <= minimo:
            
            query_str = build_query_string(row)

            # print(len(row['quienesvenden']) , minimo, query_str)
            df_matches = c.query(query_str)
                        
            if len(df_matches) > 0:
                best_match = find_best_match(row, df_matches, fuz_level)
                
                if best_match is not None:
                    c = update_dataframe(c, row, best_match)
                    c = add_vendedores(c, row.name, best_match.name)
                    
    return c


def build_query_string(row):
    # condition_dict = {'lo__unidades': row['lo__unidades'], 'articulo__pk': row['articulo__pk']}
    condition_dict = {'lo__unidades': row['lo__unidades']}
    
    if row['lo__grados2'] != 0:
        condition_dict['lo__grados2'] = row['lo__grados2']

    if row['lo__medida_cant'] != 0:
        condition_dict['lo__medida_cant'] = row['lo__medida_cant']

    if row['lo__envase'].strip() != "":
        condition_dict['lo__envase'] = f"'{row['lo__envase'].strip()}'"

    if row['lo__talla']:
        if row['lo__talla'].strip() != "":
            condition_dict['lo__talla'] = f"'{row['lo__talla'].strip()}'"

    query_str = ' & '.join([f"({key} == {value})" for key, value in condition_dict.items()])
    query_str += f" & (articulo__pk != {row['articulo__pk']})"
    
    return query_str

def check_pd(c, 
             check_nombre=False, 
             check_ean=False, 
             check_grados=False, 
             check_medida_cant=False, 
             check_envase=False, 
             check_unidades=False,
             check_talla=False,
             fuz_level=70, 
             debug=False,
             level=1):
    
    for cuenta0, row0 in c.iterrows():
        este_pk             = row0['articulo__pk']
        este_marca          = row0['articulo__marca']
        este_nombre         = row0['lo__nombre']
        este_grados         = row0['lo__grados2']
        este_medida_cant    = row0['lo__medida_cant']
        este_unidades       = row0['lo__unidades']
        este_envase         = row0['lo__envase']
        este_ean_13         = row0['lo__ean_13']
        este_talla          = row0['lo__talla']
        este_get_price      = row0['get_price']
        arr_quienes_vender  = row0['quienesvenden']
        este_r_grados       = row0['r_grados']
        este_r_envase       = row0['r_envase']
        este_r_medida       = row0['r_medida']
        este_r_talla        = row0['r_talla']

        if check_ean and este_ean_13 !='':
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
                otro_talla          = row02['lo__talla']
                otro_get_price      = row02['get_price']
                fuz_precio  = fuzz.token_sort_ratio(este_get_price, otro_get_price)
                if  not is_vendedores_in(arr_quienes_vender, row02['quienesvenden']):
                    # print('4 Inicio')
                    if debug:        
                        print('SUPERIOR')
                        print(tabulate(df_matches, headers = 'keys', tablefmt = 'psql'))
                    

                    c.at[cuenta02,'r_grados'] = 1
                    c.at[cuenta02,'lo__grados2']  = este_grados
                    c.at[cuenta02,'rule'] = 'ean grados 2'
                    
                    c.at[cuenta02,'lo__envase']  = este_envase
                    c.at[cuenta02,'r_envase'] = 1
                    c.at[cuenta02,'rule'] = 'ean envase 2'
                        
                    c.at[cuenta02,'lo__medida_cant']  = este_medida_cant
                    c.at[cuenta02,'r_medida'] = 1
                    c.at[cuenta02,'rule'] = 'ean medida_cant 2'

                    if este_unidades != otro_unidades :
                        print(f'fuz_precio={fuz_precio}')
                        if fuz_precio > 73:
                            c.at[cuenta02,'lo__unidades']  = este_unidades    

                    c.at[cuenta02,'lo__talla']  = este_talla
                    c.at[cuenta02,'r_talla'] = 1
                    c.at[cuenta02,'rule'] = 'ean talla 1'

                    c.at[cuenta02,'lo__nombre']  = este_nombre
                    c.at[cuenta02,'r_nombre'] = 1
                    c.at[cuenta02,'rule'] = 'ean nombre 2'

                    c.at[cuenta02,'r_ean'] = 1
                    if c.at[cuenta02,'rule'] == '' :
                        c.at[cuenta02,'rule'] = 'check_ean'
                    
                    c = add_vendedores(c, cuenta0, cuenta02)
                    if debug:        
                        df_matches2 = c.loc[
                            (c['lo__ean_13']        == este_ean_13) 
                        ]
                        print('inferior')
                        print(tabulate(df_matches2, headers = 'keys', tablefmt = 'psql'))
            return c
        else:  
            df_matches = c.loc[
                (c['articulo__pk']      != este_pk)
            ]
            if check_grados:
                if este_grados == 0 and este_r_grados == 0:
                    df_matches = df_matches.loc[
                        (c['lo__medida_cant']   == este_medida_cant) & 
                        (c['lo__unidades']      == este_unidades) &
                        (c['lo__envase']        == este_envase) &
                        (c['lo__talla']         == este_talla) &
                        (c['lo__grados2']       != 0) 
                    ]
                else:
                    ## Si es check_grados pero la regla grados ya esta, saltamos este registro
                    continue
            if check_envase:
                if este_envase == '' and este_r_envase == 0:
                    
                    df_matches = df_matches.loc[
                        (c['lo__medida_cant']   == este_medida_cant) & 
                        (c['lo__unidades']      == este_unidades) &
                        (c['lo__grados2']       == este_grados) &
                        (c['lo__talla']         == este_talla) &
                        (c['lo__envase']       != '') 
                    ]
                    # print('En Envase', len(df_matches))
                else:
                    continue
            if check_medida_cant:
                if este_r_medida == 0 and este_medida_cant == 0:
                    df_matches = df_matches.loc[
                        (c['lo__unidades']      == este_unidades) &
                        (c['lo__envase']        == este_envase) &
                        (c['lo__grados2']       == este_grados) &
                        (c['lo__talla']         == este_talla) &
                        (c['lo__medida_cant']   != 0) 
                    ]
                else:
                    continue
            if check_talla:
                if este_r_talla == 0 and este_talla == '':
                    df_matches = df_matches.loc[
                        (c['lo__medida_cant']   == este_medida_cant) & 
                        (c['lo__unidades']      == este_unidades) &
                        (c['lo__envase']        == este_envase) &
                        (c['lo__grados2']       == este_grados) &
                        (c['lo__talla']         != '') 
                    ]
                else:
                    continue
            if check_unidades:
                pass

            if check_nombre:
                if level == 3:
                    df_matches = df_matches.loc[
                        (c['lo__medida_cant']   == este_medida_cant) & 
                        (c['lo__unidades']      == este_unidades) &
                        (c['lo__grados2']       == este_grados) &
                        (c['lo__envase']        == este_envase) &
                        (c['lo__talla']         == este_talla) 
                    ]
                if level == 2:
                    df_matches = df_matches.loc[
                        (c['lo__medida_cant']   == este_medida_cant) & 
                        (c['lo__unidades']      == este_unidades) &
                        (c['lo__grados2']       == este_grados) &
                        (c['lo__talla']         == este_talla) 
                    ]
                if level == 1:
                    df_matches = df_matches.loc[
                        (c['lo__unidades']      == este_unidades) &
                        (c['lo__grados2']       == este_grados) &
                        (c['lo__talla']         == este_talla) 
                    ]
                
        ## Queremos arreglar este_ osea cuenta0 o row0
        for cuenta02, row02 in df_matches.iterrows():
            otro_nombre         = row02['lo__nombre']
            otro_grados         = row02['lo__grados2']
            otro_medida_cant    = row02['lo__medida_cant']
            otro_unidades       = row02['lo__unidades']
            otro_envase         = row02['lo__envase']
            otro_talla          = row02['lo__talla']
            otro_get_price      = row02['get_price']
            arr_otro_vender     = row02['quienesvenden']
           
            fuz         = fuzz.token_sort_ratio(este_nombre, otro_nombre)
            fuz_precio  = fuzz.token_sort_ratio(este_get_price, otro_get_price)

            if fuz > fuz_level and not is_vendedores_in(arr_quienes_vender, arr_otro_vender):     ### Hay proximidad de nombre y no ha sido copiado
                if debug:
                    print(f'basado_en_linea={cuenta0} fuz={fuz}  linea = {cuenta02} vs otro_nombre={otro_nombre}')

                if check_grados:
                    c.at[cuenta0,'lo__grados2'] = otro_grados
                    c.at[cuenta0,'r_grados'] = 1
                    c.at[cuenta0,'rule'] = 'pd_grados'
                    
                if check_envase:
                    c.at[cuenta0,'lo__envase'] = otro_envase
                    c.at[cuenta0,'r_envase'] = 1
                    c.at[cuenta0,'rule'] = 'pd_envase'
                    
                if check_medida_cant:
                    c.at[cuenta0,'lo__medida_cant'] = otro_medida_cant
                    c.at[cuenta0,'r_medida'] = 1
                    c.at[cuenta0,'rule'] =  'pd_medida_cant'
                if check_talla:
                    c.at[cuenta0,'lo__talla'] = otro_talla
                    c.at[cuenta0,'r_talla'] = 1
                    c.at[cuenta0,'rule'] = 'pd_talla'
                    
                if check_unidades:
                    pass

                if check_nombre and otro_nombre != '':
                    if fuz == 100:
                        if este_medida_cant == 0:
                            c.at[cuenta0,'lo__medida_cant'] = otro_medida_cant
                        if este_envase == '':
                            c.at[cuenta0,'lo__envase'] = otro_envase
                        c.at[cuenta0,'rule'] = 'pd_nombre fuz=100'
                        c.at[cuenta0,'lo__nombre'] = otro_nombre
                    else:
                        c.at[cuenta0,'r_nombre'] = 1
                        c.at[cuenta0,'lo__nombre'] = otro_nombre
                        c.at[cuenta0,'rule'] = 'pd_nombre'
                    
                    c = add_vendedores(c, cuenta0, cuenta02)

    return c

def add_vendedores(arreglo_datos, linea_destino, linea_origen):
    destino  = arreglo_datos.at[linea_destino,'quienesvenden']
    origen   = arreglo_datos.at[linea_origen,'quienesvenden']

    destino_array   = list(destino)
    origen_array    = list(origen)
    cambian         = 0
    
    for dato in origen_array:
        destino_array.append(int(dato))
        cambian = cambian + 1

    # print(arr_aquienes)
    arreglo_datos.at[linea_destino,'quienesvenden']   = destino_array
    arreglo_datos.at[linea_destino,'cuantos_venden']  = arreglo_datos.at[linea_destino,'cuantos_venden'] + cambian
    
    arreglo_datos.at[linea_origen,'quienesvenden']    = ''
    arreglo_datos.at[linea_origen,'cuantos_venden']   = 0

    return arreglo_datos

def imprime_reglas(rules):
    print("--------inicio reglas -----------")
    contador = 0
    for rule in rules:
        contador = contador + 1
        
        print(f"#{contador}:{rule['tipo']},{rule['fuz']},nombre=|{rule['si_nombre']}|,grados={rule['si_grados']},si_m_cant={rule['si_medida_cant']},si_env={rule['si_envase']},si_und={rule['si_unidades']} si_talla={rule['si_talla']}  '--', etc_nombre=|{rule['entonces_nombre']}|,etc_grados={rule['entonces_grados']},etc_m_cant={rule['entonces_medida_cant']}, etc_envase={rule['entonces_envase']} ,etc_und={rule['entonces_unidades']}, etc_talla={rule['entonces_talla']}")
        
    print("--------fin    reglas -----------")

def find_best_match(row, df_matches, fuz_level):
    best_fuz = 0
    best_match = None
    
    for _, row_match in df_matches.iterrows():
        if not is_vendedores_in(row['quienesvenden'], row_match['quienesvenden']):
            fuz = fuzz.token_sort_ratio(row['lo__nombre'], row_match['lo__nombre'])
            
            if fuz > best_fuz and fuz > fuz_level:
                best_fuz = fuz
                best_match = row_match
                
    return best_match

def update_dataframe(c, row, best_match):
    c.at[row.name, 'lo__nombre']        = best_match['lo__nombre']
    c.at[row.name, 'lo__grados2']       = best_match['lo__grados2']
    c.at[row.name, 'lo__envase']        = best_match['lo__envase']
    c.at[row.name, 'lo__medida_cant']   = best_match['lo__medida_cant']
    c.at[row.name, 'lo__talla']         = best_match['lo__talla']

    c.at[row.name, 'r_nombre'] = 1
    c.at[row.name, 'r_grados'] = 1
    c.at[row.name, 'rule'] = 'check_sailers 1'

       
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

# Función para encontrar el mejor nombre basado en la similitud del coseno
def find_best_name(similarities, index, names):
    max_sim = 0
    best_name = ''
    for i in range(len(similarities)):
        if i != index:
            sim = similarities[i]
            if sim > max_sim:
                max_sim = sim
                best_name = names[i]
    return best_name

# Función para encontrar los prefijos más frecuentes
def prefixes_to_remove(names):
    prefix_count = {}
    for name in names:
        prefix = name.split(' ')[0]
        if prefix in prefix_count:
            prefix_count[prefix] += 1
        else:
            prefix_count[prefix] = 1
    frequent_prefixes = [k for k, v in prefix_count.items() if v > 1]
    return frequent_prefixes

# Función para remover prefijos
def remove_prefixes(df, column_name, prefixes):
    df[column_name] = df[column_name].apply(lambda x: ' '.join(word for word in x.split() if word not in prefixes))

def lkernel(c):
    # Obtener prefijos para remover
    frequent_prefixes = prefixes_to_remove(c['lo__nombre'])
    # print(frequent_prefixes)
    # return c

    # Remover prefijos del DataFrame
    remove_prefixes(c, 'lo__nombre', frequent_prefixes)

    # Encontrar el prefijo más largo (o el primero en caso de empate)
    if frequent_prefixes:
        longest_prefix = max(frequent_prefixes, key=len)
        # Agregar el prefijo más largo a los nombres
        longest_prefix = longest_prefix.strip(" ")
        c['lo__nombre'] = longest_prefix + " " + c['lo__nombre']
        

        # Calcular la matriz TF-IDF
        tfidf_vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = tfidf_vectorizer.fit_transform(c['lo__nombre'])

            # Calcular la similitud del coseno entre cada par de elementos
            cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

            # Encontrar y corregir el mejor nombre para cada grupo de productos similares
            threshold = 0.6  # Este es el umbral que encontraste útil
            for i in range(len(c)):
                for j in range(i + 1, len(c)):
                    if cosine_similarities[i][j] > threshold:
                        # arr_quienes_vender  = c.loc[c.index == i, 'quienesvenden']
                        # arr_otro_vender     = c.loc[c.index == j, 'quienesvenden']
                        # print(f'arr_quienes_vender={arr_quienes_vender}  arr_otro_vender={arr_otro_vender}')
                        # if not is_vendedores_in(arr_quienes_vender, arr_otro_vender):
                        best_name = find_best_name(cosine_similarities[i], i, list(c['lo__nombre']))
                        if best_name:
                            c.loc[c.index == j, 'lo__nombre'] = best_name
                            c.loc[c.index == j, 'rule'] = 'lkernel'
                            c = add_vendedores(c, j, i)
        except Exception as e:
            print(str(e))

    else:
        # print("frequent_prefixes está vacía")
        longest_prefix = None  # O asignar un valor predeterminado


    return c


def check_grados_func(c, df_grados_uno, debug):
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
                        (c['lo__grados2']       != valor) &
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
                        fuz         = fuzz.token_sort_ratio(este_nombre, otro_nombre)
                        if fuz > best_fuz:
                            best_fuz    = fuz
                            best_id     = cuenta3
                            best_grados = row3['lo__grados2']
                            best_nombre = row3['lo__nombre']
                    if best_id:
                        c.at[cuenta2,'lo__grados2'] = best_grados
                        c.at[cuenta2,'r_grados'] = 1
                        c.at[cuenta2,'rule'] = 'Check Grados'
                        # c = add_vendedores(c, cuenta2, cuenta3)
    return c


def get_sites(marca_obj):
    sites = Vendedores.objects.select_related('articulo','vendidoen')
    sites = sites.filter(articulo__marca=marca_obj)
    sites = sites.exclude(vendidoen__precio=0)
    sites = sites.exclude(vendidoen__error404=True)
    sites = sites.values('vendidoen__site')
    sites = sites.annotate(total=Count('vendidoen__site'))
    sites = sites.order_by('-total')
    # print(sites.query)

    return sites

def get_articles_from_all(marca_obj, nombre, all_sites_arr):
    articles_from_all = Vendedores.objects.select_related('articulo','vendidoen')
    articles_from_all = articles_from_all.filter(articulo__marca=marca_obj)
    if nombre:
        articles_from_all = articles_from_all.filter(articulo__nombre=nombre)
    articles_from_all = articles_from_all.filter(vendidoen__site__in=all_sites_arr)
    articles_from_all = articles_from_all.exclude(vendidoen__precio=0)
    articles_from_all = articles_from_all.exclude(vendidoen__error404=True)
    articles_from_all = articles_from_all.order_by('articulo__nombre', 'articulo__unidades','articulo__medida_cant','articulo__grados2')
    articles_from_all = articles_from_all.distinct()

    return articles_from_all

def intenta_marca(marca_id, debug, nombre=None):
    num_rules_created   = int(Settings.objects.get(key='num_rules_created').value)
    marca_obj           = Marcas.objects.get(id=marca_id)
    reglas              = []
    all_sites_arr       = []
    sites               = get_sites(marca_obj)
    
    if not sites:
        return
    
    for site in list(sites):
        all_sites_arr.append(site['vendidoen__site'])

    articles_from_all = get_articles_from_all(marca_obj, nombre, all_sites_arr)

    c = create_PD_From(articles_from_all)
    if debug:
        print(tabulate(c, headers = 'keys', tablefmt = 'double_outline'))

    # cuenta = 0
    # while True:
    #     print(cuenta)
    #     cuenta = cuenta + 1
    #     if cuenta > 100:
    #         break

    grouped_ean = c.groupby(['lo__ean_13', ])
    list_of_processed_groups = []
    for name, group in grouped_ean:
        if len(group) > 1:
        
            group_sorted = group.sort_values(by=['cuantos_venden'], ascending=False)
            if debug:
                print(f'Largo grupo={len(group)}')
                print('evaluo grupo', name)
                print(tabulate(group_sorted, headers = 'keys', tablefmt = 'double_outline'))
            processed_group = check_pd(group_sorted, 
                    check_nombre=False, 
                    check_ean=True,
                    check_grados=False, 
                    check_medida_cant=False, 
                    check_envase=False, 
                    check_unidades=False,
                    check_talla=False,
                    fuz_level=93, 
                    debug=debug)
            list_of_processed_groups.append(processed_group)
        else:
            list_of_processed_groups.append(group)

    c = pd.concat(list_of_processed_groups, ignore_index=True)
    
    
    #### Desde aca null
    ## Caso grados que haya solo 1 registro
    if debug:
        print("######### Check Grados ###############")

    df_grados_uno = get_value_counts_df(c, 'lo__grados2')
    c = check_grados_func(c, df_grados_uno, debug=debug)
    
    
    fuz_levels = (95,93 )
    for fuzl in fuz_levels:
        ## Envase
        c = check_pd(c, check_nombre=False, check_ean=False, check_grados=False, check_medida_cant=False, check_envase=True, check_unidades=False, check_talla=False, fuz_level=fuzl, debug=debug)
        ## Grados
        c = check_pd(c, check_nombre=False, check_ean=False, check_grados=True, check_medida_cant=False, check_envase=False, check_unidades=False, check_talla=False, fuz_level=fuzl, debug=debug)
        ## Medida_cant
        c = check_pd(c, check_nombre=False, check_ean=False, check_grados=False, check_medida_cant=True, check_envase=False, check_unidades=False, check_talla=False, fuz_level=fuzl, debug=debug)
        ## Talla
        c = check_pd(c, check_nombre=False, check_ean=False, check_grados=False, check_medida_cant=False, check_envase=False, check_unidades=False, check_talla=True, fuz_level=fuzl, debug=debug)
        
    c = check_pd(c, 
                     check_nombre=True,         ## Cierto .. debe ser al final
                     check_ean=False, 
                     check_grados=False, 
                     check_medida_cant=False, 
                     check_envase=False,  
                     check_unidades=False,
                     check_talla=False,
                     fuz_level=93, 
                     debug=debug,
                     level=3
                     )
    c = check_pd(c, 
                     check_nombre=True,         ## Cierto .. debe ser al final
                     check_ean=False, 
                     check_grados=False, 
                     check_medida_cant=False, 
                     check_envase=False,  
                     check_unidades=False,
                     check_talla=False,
                     fuz_level=93, 
                     debug=debug,
                     level=2
                     )
    c = check_pd(c, 
                     check_nombre=True,         ## Cierto .. debe ser al final
                     check_ean=False, 
                     check_grados=False, 
                     check_medida_cant=False, 
                     check_envase=False,  
                     check_unidades=False,
                     check_talla=False,
                     fuz_level=93, 
                     debug=debug,
                     level=1
                     )
    
    fuz_levels = (95,90 )
    for fuzl in fuz_levels:
        if debug:
            print("Check- envase")
        c = check_pd(c, 
                     check_nombre=False, 
                     check_ean=False, 
                     check_grados=False, 
                     check_medida_cant=False, 
                     check_envase=True,         ## Cierto
                     check_unidades=False,
                     check_talla=False,
                     fuz_level=fuzl, 
                     debug=debug)
        
        # if debug:
        #     print("Check- EAN")
        # c = check_pd(c, 
        #              check_nombre=False, 
        #              check_ean=True,            ## Cierto
        #              check_grados=False, 
        #              check_medida_cant=False, 
        #              check_envase=False, 
        #              check_unidades=False,
        #              check_talla=False,
        #              fuz_level=fuzl, 
        #              debug=debug)

        if debug:
            print("Check- Grados")
        c = check_pd(c, 
                     check_nombre=False, 
                     check_ean=False, 
                     check_grados=True,         ## Cierto
                     check_medida_cant=False, 
                     check_envase=False,  
                     check_unidades=False,
                     check_talla=False,
                     fuz_level=fuzl, 
                     debug=debug)

        if debug:
            print("Check- medida_cant")
        c = check_pd(c, 
                     check_nombre=False, 
                     check_ean=False, 
                     check_grados=False, 
                     check_medida_cant=True,    ## Cierto
                     check_envase=False, 
                     check_unidades=False,
                     check_talla=False,
                     fuz_level=fuzl, 
                     debug=debug)
        
        if debug:
            print("Check- talla")
        c = check_pd(c, 
                     check_nombre=False, 
                     check_ean=False, 
                     check_grados=False, 
                     check_medida_cant=False,    
                     check_envase=False, 
                     check_unidades=False,
                     check_talla=True,          ## Cierto
                     fuz_level=fuzl, 
                     debug=debug)
        
        if debug:
            print("Check- unidades")
        c = check_pd(c, 
                     check_nombre=False, 
                     check_ean=False, 
                     check_grados=False, 
                     check_medida_cant=False,    
                     check_envase=False, 
                     check_unidades=True,
                     check_talla=False,
                     fuz_level=fuzl, 
                     debug=debug)
        
        if debug:
            print("Check- Nombre")
        c = check_pd(c, 
                     check_nombre=True,         ## Cierto .. debe ser al final
                     check_ean=False, 
                     check_grados=False, 
                     check_medida_cant=False, 
                     check_envase=False,  
                     check_unidades=False,
                     check_talla=False,
                     fuz_level=fuzl, 
                     debug=debug,
                     level=3
                     )
    
        
    # if c.shape[0] <= 50:
    # print(f'*** {marca_obj.slug}  c.size={c.shape[0]}')
    # grouped_estricto = c.groupby([
    #     'lo__medida_cant', 
    #     'lo__unidades', 
    #     'lo__grados2', 
    #     'lo__envase', 
    #     'lo__talla'
    # ])
    # list_of_processed_groups = []

    # for name, group in grouped_estricto:
    #     # print('***** lkernel group name', name)
    #     processed_group = lkernel(group)
    #     list_of_processed_groups.append(processed_group)

    # c = pd.concat(list_of_processed_groups, ignore_index=True)


    fuz_levels = (93,90)
    for fuzl in fuz_levels:
        if debug:
            print(f"Check sailers min=1 fuz={fuzl}")
        c = check_sailers(c, 1, fuzl, debug)

        if debug:
            print(f"Check sailers min=2 fuz={fuzl}")
        c = check_sailers(c, 2, fuzl, debug)
        
    if marca_obj.grados:
        c = check_pd(c, 
            check_nombre=True,         ## Cierto .. debe ser al final
            check_ean=False, 
            check_grados=False, 
            check_medida_cant=False, 
            check_envase=False,  
            check_unidades=False,
            check_talla=False,
            fuz_level=47, 
            debug=debug)
        
    if marca_obj.talla :
        c = check_pd(c, 
            check_nombre=True,         ## Cierto .. debe ser al final
            check_ean=False, 
            check_grados=False, 
            check_medida_cant=False, 
            check_envase=False,  
            check_unidades=False,
            check_talla=False,
            fuz_level=66, 
            debug=debug)
    
    if debug:
        print(tabulate(c, headers = 'keys', tablefmt = 'double_outline'))

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

    

    ### Genera lista de reglas
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
    
    if len(reglas) > 0:
        print(f"{marca_obj.slug} con {len(c)} articulos. Nuevas reglas={len(reglas)}")
        
    if debug:
        print(tabulate(c, headers = 'keys', tablefmt = 'psql'))
        print('===================')

    if not debug:
        generate_rules(reglas, debug)

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
    
    df_articulos['cuantos_venden']          = 0
    df_articulos['rule']                    = ''
    df_articulos['get_price']               = 0
    df_articulos['lo__nombre']              = ''
    df_articulos['lo__medida_cant']         = float(0)
    df_articulos['lo__unidades']            = 0
    df_articulos['lo__grados2']             = float(0)
    df_articulos['lo__envase']              = ''
    df_articulos['lo__talla']               = ''
    df_articulos['lo__ean_13']              = ''
    
    df_articulos['r_nombre']    = 0
    df_articulos['r_medida']    = 0
    df_articulos['r_grados']    = 0
    df_articulos['r_ean']       = 0
    df_articulos['r_envase']    = 0
    df_articulos['r_unidades']  = 0
    df_articulos['r_talla']     = 0
    
    df_articulos['quienesvenden']   = {}
    

    ## Fill some cols
    for cuenta, row in df_articulos.iterrows():
        art = Articulos.objects.get(pk=row['articulo__pk'])
        df_articulos.at[cuenta,'get_price']             = art.get_price
        df_articulos.at[cuenta,'quienesvenden']         = art.quienesvenden()
        df_articulos.at[cuenta,'cuantos_venden']         = art.cuanntosvenden()
        if art.envase:
            df_articulos.at[cuenta,'articulo__envase']      = art.envase.strip(" ")
        else:
            df_articulos.at[cuenta,'articulo__envase']      = ''


        df_articulos.at[cuenta,'lo__nombre']            = art.nombre.strip(" ")
        df_articulos.at[cuenta,'lo__medida_cant']       = float(art.medida_cant)
        df_articulos.at[cuenta,'lo__unidades']          = art.unidades
        df_articulos.at[cuenta,'lo__grados2']           = float(art.grados2)
        if art.envase:
            df_articulos.at[cuenta,'lo__envase']            = art.envase.strip(" ")
        else:
            df_articulos.at[cuenta,'lo__envase']            = ''
        if art.talla:
            df_articulos.at[cuenta,'lo__talla']            = art.talla.strip(" ")
        else:
            df_articulos.at[cuenta,'lo__talla']            = ''

        if art.ean_13:
            df_articulos.at[cuenta,'lo__ean_13']           = art.ean_13.strip(" ")
        else:
            df_articulos.at[cuenta,'lo__ean_13']           = ''


    return df_articulos

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
    # grouped_general = c.groupby([
    #     'lo__medida_cant',
    #     'lo__grados2',
    #     'lo__envase',
    #     'lo__talla'
    # ])
    # list_of_processed_groups = []
    # for name, group in grouped_general:
    #     processed_group = lkernel(group)
    #     list_of_processed_groups.append(processed_group)

    # c = pd.concat(list_of_processed_groups, ignore_index=True)

        # cuenta = 0
    # while True:
    #     print(cuenta)
    #     cuenta = cuenta + 1
    #     if cuenta > 100:
    #         break