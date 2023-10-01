from django.core.management.base import BaseCommand
import pandas as pd
import numpy as np
import unidecode
from django.db.models import F, Sum, Count, Q
from precios.models import SiteURLResults, Articulos, Unifica, Marcas, Vendedores, MarcasSistema, Site, Settings, AllPalabras, ReemplazaPalabras
from django.core import management
from precios.pi_get import obtener_grados

from precios.pi_functions import (
    
    setMessage, 
    # buscar_articulos_con_y_sin_grados,
    # get_num_url_in_sites_per_brand,
    # get_articles_from_site,
    # get_url_from_site_mul,
    # get_url_from_site,

)   
from precios.pi_rules import (
    intenta_marca,
    createRule, 
    imprime_reglas,
    generate_rules,
    create_PD_From,
)
from precios.pi_get import reemplaza_palabras        

from fuzzywuzzy import fuzz, process



class Command(BaseCommand):
    help = "Start the simulation"

    def __init__(self):
        super().__init__()


    def buscar_articulos_nombre_parecido(self, df):
        # Ordenar el dataframe por dcount en orden descendente
        df = df.sort_values(by=['dcount'], ascending=False)

        # Crear una lista de nombres de artículo únicos
        nombres_articulos_unicos = df['nombre'].unique()

        # Crear una lista de posibles nombres de artículo que suenan igual
        posibles_nombres = []

        # Buscar nombres de artículo que suenan igual
        nombres_comparados = [] # lista para almacenar los nombres ya comparados
        for i, nombre in enumerate(nombres_articulos_unicos):
            if nombre not in nombres_comparados: # verificar si el nombre ya ha sido comparado
                # buscar los nombres de artículo que tienen una puntuación de coincidencia de al menos el 90% y una diferencia de dcount menor o igual a 10
                nombres_coincidentes = []
                for j in range(i+1, len(nombres_articulos_unicos)):
                    
                    if nombres_articulos_unicos[j] not in nombres_comparados:
                        
                        if fuzz.token_sort_ratio(nombre, nombres_articulos_unicos[j]) >= 90 and abs(df[df['nombre']==nombre]['dcount'].iloc[0] - df[df['nombre']==nombres_articulos_unicos[j]]['dcount'].iloc[0]) <= 10:
                            print('******* ',nombres_articulos_unicos[j], fuzz.token_sort_ratio(nombre, nombres_articulos_unicos[j]))
                            nombres_coincidentes.append(nombres_articulos_unicos[j])
                if nombres_coincidentes:
                    # agregar el nombre de artículo y su lista de nombres de artículo coincidentes a la lista de posibles nombres
                    posibles_nombres.append((nombre, nombres_coincidentes)) 
                    # agregar el nombre actual a la lista de nombres comparados
                    nombres_comparados.append(nombre)
                    # agregar los nombres coincidentes a la lista de nombres comparados
                    nombres_comparados += nombres_coincidentes

        # mostrar la lista de posibles nombres
        return posibles_nombres


    # def find_duplicates(self, row):
    #     articulo = row['nombre']
    #     medida_cant = row['medida_cant']
    #     unidades = row['unidades']
    #     marca = row['marca']
    #     grados = row['grados2']
        
    #     df_matches = df_articulos.loc[
    #         (df_articulos['marca'] == marca) & 
    #         (df_articulos['medida_cant'] == medida_cant) & 
    #         (df_articulos['unidades'] == unidades) & 
    # #         (~df_articulos['ean_13'].isnull()) & 
    #         (df_articulos['nombre'] != articulo)
    #     ]
        
    #     max_ratio = 0
    #     max_match = None
        
    #     for _, match in df_matches.iterrows():
    #         ratio = fuzz.token_set_ratio(articulo.lower(), match['nombre'].lower())
    #         if ratio > max_ratio:
    #             max_ratio = ratio
    #             max_match = match
        
    #     if max_ratio >= 90:
    #         return {
    #             'marca': marca,
    #             'medida_cant': medida_cant,
    #             'unidades': unidades,
    #             'articulo_con_grados': articulo,
    #             'ean_13_con_grados': row['ean_13'],
    #             'articulo_sin_grados': max_match['nombre'],
    #             'ean_13_sin_grados': max_match['ean_13'],
    #         }
        
    #     return None



    # def obtener_articulos_nombre_diferente(self, que_busco, donde):
    #     nombre      = que_busco['nombre']
    #     medida_cant = que_busco['medida_cant']
    #     unidades    = que_busco['unidades']
    #     marca       = que_busco['marca']
    #     grados      = que_busco['grados2']
        
    #     df_matches = donde.loc[
    #         (donde['marca'] == marca) & 
    #         (donde['medida_cant'] == medida_cant) & 
    #         (donde['unidades'] == unidades) & 
    #         # (donde['grados'] == grados) & 
    #         (donde['nombre'] != nombre)
    #     ]
    #     return df_matches

    ## Uno por ean13
    # def crear_rules_ean13(self, cuantos_minimo):
    #     subquery = Articulos.objects.exclude(ean_13='').values('ean_13', 'marca_id', 'medida_cant').annotate(count=Count('ean_13')).filter(count__gt=cuantos_minimo).values('ean_13')
    #     query = Articulos.objects.filter(ean_13__in=subquery).exclude(ean_13='').order_by('ean_13', '-grados2').values(
    #         'nombre', 
    #         'marca_id', 
    #         'ean_13', 
    #         'grados2', 
    #         'unidades', 
    #         'medida_cant',
    #         'envase',
    #         'talla',
    #         )

    #     primero = True
    #     ean13 = float(0)

    #     cuenta_primeros = 0
    #     cuenta_segundos = 0

    #     si_marca            = None
    #     si_nombre           = None
    #     si_grados           = None
    #     si_medida_cant      = None
    #     si_unidades         = None
    #     si_envase           = None

    #     entonces_marca      = None
    #     entonces_nombre     = None
    #     entonces_grados2    = None
    #     entonces_medida_cant= None
    #     entonces_unidades   = None
    #     entonces_envase     = None

    #     for art in query:
    #         if primero or ean13 != art['ean_13']:
    #             cuenta_primeros = cuenta_primeros + 1
    #             ean13 = art['ean_13']
    #             primero = False
                
    #             entonces_marca = Marcas.objects.filter(id=art['marca_id']).get()
    #             entonces_nombre     = art['nombre']
    #             entonces_grados2    = art['grados2']
    #             entonces_medida_cant= art['medida_cant']
    #             entonces_unidades   = art['unidades']
    #             entonces_envase     = art['envase']

                
    #         else:
    #             cuenta_segundos = cuenta_segundos  + 1
    #             print(f'{cuenta_segundos}  marca= {entonces_marca.nombre} nombre=', art['nombre'])

    #             si_marca        = Marcas.objects.filter(id=art['marca_id']).get()
    #             si_nombre       = art['nombre']
    #             si_grados       = art['grados2']
    #             si_medida_cant  = art['medida_cant']
    #             si_unidades     = art['unidades']
    #             si_envase       = art['envase']

    #             createRule(
    #                 si_marca, 
    #                 si_nombre, 
    #                 si_grados, 
    #                 si_medida_cant, 
    #                 si_unidades, 
    #                 si_envase,
    #                 entonces_marca, 
    #                 entonces_nombre, 
    #                 entonces_grados2, 
    #                 entonces_medida_cant, 
    #                 entonces_unidades ,
    #                 entonces_envase,
    #                 'ean_13'
    #             )
    #             ean13 = art['ean_13']

    #     print('cuenta_primeros', cuenta_primeros, cuenta_segundos)

    def create_articles(self, marcaid):
        if marcaid:
            sites = Site.objects.filter(enable=True)
            posicion = 0
            for site in sites:
                posicion = posicion + 1
                management.call_command('createProds', site.id, posicion, f'--marcaid={marcaid}')

        else:
            # Articulos.objects.all().delete()
            sites = Site.objects.filter(enable=True)
            sites = sorted(sites, key=lambda a: a.urlCount, reverse=True)
            posicion = 0
            for site in sites:
                posicion = posicion + 1
                print(site.siteName)
                print('===========================================')
                management.call_command('createProds', site.id, posicion)

    def rules_marcas(self, marcaid):
        ### Articulos debe estar lleno !!!
        
        ### de todas las reglas no automaticas
        ### que tengan si_nombre y entonces_nombre en blanco
        ### Se generan reglas automaticas

        queryRules = Unifica.objects.filter(automatico=False, si_nombre=None, entonces_nombre=None).all()
        if marcaid:
            marcaObj = Marcas.objects.filter(id=marcaid).get()
            queryRules = Unifica.objects.filter(automatico=False, si_marca=marcaObj).all()

        print(f'reglas de cambio de marca = {len(queryRules)}')
        num_articulos_cambio_marca = 0
        for rule in queryRules:
            print(f'si marca={rule.si_marca}')
            si_marca        = rule.si_marca
            entonces_marca  = rule.entonces_marca

            filtrado_por_marca = Articulos.objects.filter(marca=si_marca)

            num_articulos_cambio_marca = num_articulos_cambio_marca + len(filtrado_por_marca)
            print(f'num_articulos_cambio_marca = {num_articulos_cambio_marca}')
            for rowarticulo in filtrado_por_marca:         ## Por cada marca
                if rowarticulo.envase == '' :
                    pon_envase = None
                else:
                    pon_envase = rowarticulo.envase
                if rowarticulo.nombre == '' :
                    pon_nombre = None
                else:
                    pon_nombre = rowarticulo.nombre
                    
                pon_nombre = reemplaza_palabras(pon_nombre)
                createRule(
                        si_marca, 
                        pon_nombre, 
                        rowarticulo.grados2, 
                        rowarticulo.medida_cant, 
                        rowarticulo.unidades, 
                        pon_envase, 
                        rowarticulo.talla, 

                        entonces_marca, 
                        pon_nombre, 
                        rowarticulo.grados2, 
                        rowarticulo.medida_cant, 
                        rowarticulo.unidades,
                        pon_envase,
                        rowarticulo.talla, 
                        'cambio de marca'
                    )
                
            si_marca_obj        = rule.si_marca
            entonces_marca_obj  = rule.entonces_marca

            si_marca_obj.es_marca = False
            si_marca_obj.save()

            entonces_marca_obj.es_marca = True
            entonces_marca_obj.save()

        print(f'TOTAL num_articulos_cambio_marca = {num_articulos_cambio_marca}')

    def elimina_relacion_reglas(self):
        urls = SiteURLResults.objects.all()

        for url in urls:
            url.reglas.clear()

    def add_arguments(self, parser):
        parser.add_argument('--marcaid', type=int, help='Marca id', default=None)
        parser.add_argument('--crear', type=bool, help='Solo crar articulos', default=False)

    def handle(self, *args, **options):
        marcaid     = options["marcaid"]
        crear       = options["crear"]
        if crear:
            setMessage('Generando articulos especial')
            ## Pongo en 0 num_rules_created
            
            rules = Settings.objects.get(key='num_rules_created')
            rules.value = 0
            rules.save()
            
            Unifica.objects.filter(automatico=True).delete() 

            Vendedores.objects.all().delete()
            Articulos.objects.all().delete()
            setMessage('Eliminando relacion con reglas')
            self.elimina_relacion_reglas()

            setMessage('Generando articulos Inicial')
            self.create_articles(marcaid)
            

        ### Articulos debe estar lleno !!!
        setMessage('Generando reglas de marcas')
        self.rules_marcas(marcaid)

        ## 2do conjunto de reglas
        setMessage('Generando REGLAS 1/1')
        if options['marcaid']:
            marcas = Marcas.objects.filter(id=marcaid)
        else:
            marcas = Marcas.objects.filter(es_marca=True)

        for marca in marcas:
            intenta_marca(marca, False)
    

        setMessage('Eliminando articulos')
        ######################################### INICIO      ###################
        if marcaid:
            marcaObj = Marcas.objects.filter(id=marcaid).get()
            Articulos.objects.filter(marca=marcaObj).delete()
            Unifica.objects.filter(si_marca=marcaObj).update(contador=0)
        else:
            # Articulos.objects.all().delete()
            Unifica.objects.all().update(contador=0)
            AllPalabras.objects.all().update(contador=0)
            ReemplazaPalabras.objects.all().update(contador=0)

            setMessage('Eliminando vendedores')
            Vendedores.objects.all().delete()
            setMessage('Eliminando relacion con reglas')
            self.elimina_relacion_reglas()
        
        ######################################### FIN INICIO  ###################
        
        ## 1eras reglas
        setMessage('Generando articulos 1/1')
        self.create_articles(marcaid)


        setMessage('Elimina reglas automaticas sin uso')
        Unifica.objects.filter(automatico=True, contador=0).delete()  ### Borra reglas sin uso

        setMessage('Elimina productos sin vendedores')
        arts = Articulos.objects.all()
        cuenta = 0
        nocuenta = 0
        for art in arts:
            if art.cuanntosvenden == 0:
                try:
                    art.delete()
                    cuenta = cuenta + 1
                except Exception as e:
                    print(e)
            else:
                nocuenta = nocuenta + 1

        print(f'Se eliminan {cuenta} no se eliminan={nocuenta}')
        
        if not marcaid:
            setMessage('Actualizando numero de veces que reglas han sido creadas')
            rules = Settings.objects.get(key='num_rules_created')
            rules.value = str(int(rules.value) + 1)
            rules.save()

        setMessage('')
    
        ######## FIN  Programa #########

    
