from precios.models import (
    Settings,
    Site, 
    Marcas, 
    Articulos,
    Vendedores,
    Unifica,
)
from django.db.models import F, Sum, Count, Min, Max
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from tabulate import tabulate

from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist

def is_vendedores_in(a_quienes, b_quienes, debug=False):
    # Verificar si alguna de las listas está vacía
    if not a_quienes or not b_quienes:
        print(f'---> NOT  a_quienes={a_quienes} b_quienes={b_quienes} ')
        return True
    
    # Verificar si algún elemento de a_quienes está en b_quienes
    si_esta = any(a in b_quienes for a in a_quienes)



    if debug:
        print(f'---> a_quienes={a_quienes} b_quienes={b_quienes} esta={si_esta}')

    return si_esta

def check_sailers(c, minimo, fuz_level=70, debug=False):
    for _, row in c.iterrows():
        if len(row['quienesvenden']) <= minimo:
            query_str = build_query_string(row)
            df_matches = c.query(query_str)
                        
            if len(df_matches) > 0:
                best_match = find_best_match(row, df_matches, fuz_level)
                
                if best_match is not None:
                    c = update_dataframe(c, row, best_match)
                    c = add_vendedores(c, row.name, best_match.name)
                    
    return c


def build_query_string(row):
    condition_dict = {'lo__unidades': row['lo__unidades'], 'articulo__pk': row['articulo__pk']}
    
    if row['lo__grados2'] != 0:
        condition_dict['lo__grados2'] = row['lo__grados2']
    if row['lo__medida_cant'] != 0:
        condition_dict['lo__medida_cant'] = row['lo__medida_cant']
    if row['lo__envase'].strip() != "":
        condition_dict['lo__envase'] = f"'{row['lo__envase'].strip()}'"
    if row['lo__talla'].strip() != "":
        condition_dict['lo__talla'] = f"'{row['lo__talla'].strip()}'"

    query_str = ' & '.join([f"({key} == {value})" for key, value in condition_dict.items()])
    query_str += f" & (articulo__pk != {row['articulo__pk']})"
    
    return query_str



# def check_sailers(c, minimo, fuz_level=70, debug=False):
#     for cuenta0, row0 in c.iterrows():
#         arr_quienes_vender  = row0['quienesvenden']
#         cuantos_venden = len(arr_quienes_vender)
#         if cuantos_venden <= minimo:
#             if debug:        
#                 df_debug = c.loc[
#                     (c['articulo__pk']       == row0['articulo__pk'])
#                 ]
#                 print('**************************** ME INTERESA *********************************')
#                 print(tabulate(df_debug, headers = 'keys', tablefmt = 'fancy_grid'))

#             este_pk             = row0['articulo__pk']
#             este_marca          = row0['articulo__marca']
#             este_nombre         = row0['lo__nombre']
#             este_grados         = row0['lo__grados2']
#             este_medida_cant    = row0['lo__medida_cant']
#             este_unidades       = row0['lo__unidades']
#             este_envase         = row0['lo__envase']
#             este_talla          = row0['lo__talla']
#             este_ean_13         = row0['lo__ean_13']
#             arr_quienes_vender  = row0['quienesvenden']
#             este_envase         = este_envase.strip()

#             # Inicializa un diccionario con las condiciones que siempre aplicarán
#             condition_dict = {'lo__unidades': este_unidades, 'articulo__pk': este_pk}

#             # Añade condiciones adicionales basadas en las variables
#             if este_grados != 0:
#                 condition_dict['lo__grados2'] = este_grados
#             if este_medida_cant != 0:
#                 condition_dict['lo__medida_cant'] = este_medida_cant
#             if este_envase != "":
#                 condition_dict['lo__envase'] = este_envase
#             if este_talla != "":
#                 condition_dict['lo__talla'] = este_talla

#             # Construye la consulta
#             query_str = ' & '.join([f"(c['{key}'] == {value})" for key, value in condition_dict.items()])
#             query_str += f" & (c['articulo__pk'] != {este_pk})"

#             # Ejecuta la consulta
#             df_matches = c.query(query_str)

            
#             #     ]
            

#             cuantos_encuento = len(df_matches)
#             if cuantos_encuento > 0:

#                 # # Tokenizar las palabras
#                 # word_tokens = [word for sentence in df_matches['lo__nombre'] for word in word_tokenize(sentence)]
#                 # # Calcular la frecuencia de las palabras
#                 # word_freq = FreqDist(word_tokens)
#                 # # Encontrar la palabra más común
#                 # if word_freq:
#                 #     most_common_word = word_freq.most_common(1)[0][0]
#                 # else:
#                 #     most_common_word = ''

#                 best_fuz = 0
#                 best_id  = None
#                 if debug:        
#                     print(f'cuantos encuento={cuantos_encuento}')
#                     print(tabulate(df_matches, headers = 'keys', tablefmt = 'psql'))
#                 for cuenta02, row02 in df_matches.iterrows():
#                     if  not is_vendedores_in(arr_quienes_vender, row02['quienesvenden']):
#                         otro_pk             = row02['articulo__pk']
#                         otro_marca          = row02['articulo__marca']
#                         otro_nombre         = row02['lo__nombre']
#                         otro_grados         = row02['lo__grados2']
#                         otro_medida_cant    = row02['lo__medida_cant']
#                         otro_unidades       = row02['lo__unidades']
#                         otro_envase         = row02['lo__envase']
#                         otro_talla          = row02['lo__talla']
#                         otro_ean_13         = row02['lo__ean_13']
#                         arr_otro_vender     = row0['quienesvenden']

#                         fuz         = fuzz.token_sort_ratio(este_nombre, otro_nombre)
                        
#                         # if fuz < fuz_level:
#                         #     paso_nombre = otro_nombre.replace(most_common_word,'')
#                         #     fuz         = fuzz.token_sort_ratio(este_nombre, paso_nombre)

#                         if fuz > best_fuz and fuz > fuz_level:
#                             if debug:        
#                                 print(f'check_sailers --- Grados Modificado !! fuz={fuz}, fuz_level={fuz_level}')

#                             best_fuz            = fuz
#                             best_id             = otro_pk
#                             best_grados         = otro_grados
#                             best_nombre         = otro_nombre
#                             best_medida_cant    = otro_medida_cant
#                             best_envase         = otro_envase
#                             best_talla          = otro_talla
#                             linea               = cuenta02
                            

#                 if best_id:
#                     c.at[cuenta0,'lo__nombre']  = best_nombre 
#                     c.at[cuenta0,'lo__grados2'] = best_grados

#                     c.at[cuenta0,'r_nombre'] = 1
#                     c.at[cuenta0,'r_grados'] = 1
#                     c.at[cuenta0,'rule'] = f'check_sailers 1'


#                     # if este_envase == '' and otro_envase !='' and row02['r_envase'] == 0 \

#                     if este_envase == "":
#                         c.at[cuenta0,'lo__envase']      = best_envase
#                         c.at[cuenta0,'rule']            = f'check_sailers envase'
#                         c.at[cuenta0,'r_envase'] = 1

#                     if este_medida_cant == 0:
#                         c.at[cuenta0,'lo__medida_cant'] = best_medida_cant

#                     c = add_vendedores(c, cuenta0, linea)

            
            
#     return c



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
    c.at[row.name, 'lo__nombre'] = best_match['lo__nombre']
    c.at[row.name, 'lo__grados2'] = best_match['lo__grados2']
    c.at[row.name, 'r_nombre'] = 1
    c.at[row.name, 'r_grados'] = 1
    c.at[row.name, 'rule'] = 'check_sailers 1'

    if row['lo__envase'].strip() == "":
        c.at[row.name, 'lo__envase'] = best_match['lo__envase']
        c.at[row.name, 'rule'] = 'check_sailers envase'
        c.at[row.name, 'r_envase'] = 1

    if row['lo__medida_cant'] == 0:
        c.at[row.name, 'lo__medida_cant'] = best_match['lo__medida_cant']
        
    return c


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