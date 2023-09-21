from asyncore import loop
import unidecode
from cgitb import enable
from curses.ascii import isdigit
import re
from celery import shared_task, app
from django.conf import settings

from django.core import management
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
    Results,
    PAGECRAWLER,
    Marcas, 
    Articulos,
    Vendedores,
    MarcasSistema

)


## UM
UM = ('"' ,'cc' , 'c' , 'ml' , 'ml.' ,'ml,', 'l' , 'lt' , 'lt.', 'litro', 'litros', 'g', 'g,', 'g.','gr' ,'gr,', 'gr.', 'grs' , 'grs.' 'm' ,  'mm' ,   'k' ,  'kg' ,  'kg.' ,  'kl' , 'cm' ,  'cm,'
              'meses' , 'gb' , 'mt'  , 'mts'  , 'metro' , 'metros' , 'plaza', 'plazas','btu', 'galon' )


UNIDADES = ('u', 'un' , 'un.', 'un,', 'unidades',  'unid' ,'sobres' ,'cápsulas', 'bolsas', 'bolsitas', 'hojas', 'tabletas' ,  'pieza', 'piezas', 'pzas')
SUJIFOS_NOMBRE = ('aprox', 'c/u', 'drenado', 'congelado')
COLORES = ('blanco', 'amarrillo', 'naranja', 'verde' ,'negro', 'rojo', 'gris','cyan',
           'papaya',  'frutilla',  'frambuesa',  'maracuyá', 'coco' ,  'plátano',  'manzana', 'mora' ,'damasco',  'alcayota',  'piña', 
            'vainilla',  'pera',  'almendra',  'guinda', 'sandía', 'banana', 'azul','naranjo', 'rosado', 'rosa', 'roza', 'turquesa', 'morado')
ENVASES = ('caja,', 'caja', 'tarro',  'tarro,', 'botella', 'botella,', 'botellin', 'bolsa','bolsa,', 'lata,', 'lata', 'latas','latas,', 'tetra', 'botellon','botellón', 'frasco', 'otellín', 'pote', 'pote,','barril','tetrapak')

ELIMINA_CARACTERES = ('®', '(', ')')
##### celery --app=scrap worker
# celery --app=scrap beat
# celery --app=scrap flower
# celery --app=scrap worker -Q core_calc  -n worker1.%h
# celery --app=scrap worker -Q core_front -n worker2.%h
##########
# creacionn de articulos

def check_sinum(valor):
    valor = valor.replace(".","")
    valor = valor.replace(",","")
    return valor.isdigit()
        


def normalizeUM(UnMed):
    retorna = UnMed

    if UnMed == 'ml' or UnMed == 'ml,' or UnMed == 'ml.':
        retorna = 'cc' 

    if UnMed == 'l' or UnMed == 'litros' or UnMed == 'litro':
        retorna = 'lt' 

    if UnMed == 'g' or UnMed == 'gr.' or UnMed == 'grs' or UnMed == 'grs.' or UnMed == 'g.' or UnMed == 'g,':
        retorna = 'gr' 
    
    if UnMed == 'kl'  or UnMed == 'k' :
        retorna = 'kg' 

    if UnMed == 'mts'  or \
        UnMed == 'metro' or \
        UnMed == 'metros':
        retorna = 'mt'

    return retorna


def normalizeCANTyUM(um_cant, um_text):

    um_cant = um_cant.strip()
    if um_cant == "":
        um_cant = 0
    else:
        um_cant = um_cant.replace(",", ".")

    um_cant = float(um_cant)

    # 3,785411784
    if um_text == 'galon':
        um_cant = um_cant * 3.785411784
        um_text = 'lt'

    if um_text == 'lt' and um_cant <= 30:
        um_cant = um_cant * 1000
        um_text = 'cc'

    if um_text == 'kg' and um_cant <= 30:
        um_cant = um_cant * 1000
        um_text = 'gr'

    um_cant = int(um_cant)

    return um_cant, um_text


def getStringAndNumbers(donde):
    return  re.split('(\d+)',donde)

def quita_word(donde, que_busca):
    arr_words = donde.split(' ')
    the_word = ''
    for word in arr_words:
        if que_busca in word:
            donde = donde.replace(word,'')
            the_word =  word
  
    return donde, the_word

@shared_task(queue='core_calc',bind=True)
def CreateProds(request):


    articulos_creados = 0
    articulos_existentes = 0
    articulos_nombre_vacio = 0
    articulos_marca_vacio = 0
    print("Inicio CreateProds")
    ## Settings
    campoMarcaObj = Campos.objects.get(pk=8)
    

    # Marcas.objects.all().delete()   ## Intentando no borrar

    camposMarca = CamposEnSitio.objects.filter(campo=campoMarcaObj)
    
    marcas = Results.objects.values('valor').filter(campoEnSitio_id__in=camposMarca).distinct()
    print("Marcas Crear - Inicio")
    for marca in marcas:
        if marca['valor'] != "" and marca['valor'] != ".":
            Marcas.objects.update_or_create(nombre=marca['valor'])
    print("Marcas Crear - FIN")
    

     ## Articulos
    print("Articulos Borrado - Inicio")
    Articulos.objects.all().delete()
    print("Articulos Borrado - FIN")

    # return
    # sites = Site.objects.filter(pk=11)
    sites = Site.objects.all()
    for site in sites:
        print(site.siteName)
        print('===========================================')

        

        urls = SiteURLResults.objects.filter(site=site).all()
        registros = 0
        for url in urls:

            try:
                camposMarca = CamposEnSitio.objects.filter(site=url.site, campo=campoMarcaObj, enabled=True).get()
                sitio_con_marrca = True
            except ObjectDoesNotExist:
                ## Sitio no usa marcas
                sitio_con_marrca = False


            registros = registros + 1
            vendedor = url.site
            existe_marca = True
            
            ## Nombre
            try:
                campoNombreObj = Campos.objects.get(pk=10)
                camposNombre = CamposEnSitio.objects.filter(campo=campoNombreObj)
                nombrepaso =  Results.objects.filter(URLResult=url, campoEnSitio_id__in=camposNombre).get()
                nombre = nombrepaso.valor
                nombre_original = nombrepaso.valor

            except ObjectDoesNotExist:
                nombre = ''
                nombre_original = ''
                ## Si no hay nombre, loop
                articulos_nombre_vacio = articulos_nombre_vacio + 1
                continue

            ## Marca
            newmarca_str = ''
            if sitio_con_marrca:
                
                try:
                    oldmarca =  Results.objects.filter(URLResult=url, campoEnSitio_id=camposMarca).get()
                   
                except ObjectDoesNotExist:
                    ## Este rergistrro no tiene MARCA
                    # print('No existe Results Anterior')

                    ## NO SE AGRERGA
                    articulos_marca_vacio = articulos_marca_vacio + 1
                    continue
                    ## Marca no existe, hay que crearla
                    # newmarca, created = Marcas.objects.get_or_create(nombre=la_marca.nombre)

                try:
                    newmarca = Marcas.objects.filter(nombre=oldmarca.valor).get()
                except ObjectDoesNotExist:
                    articulos_marca_vacio = articulos_marca_vacio + 1
                    continue
                    # print('Registro sin Marca')

                newmarca_str = newmarca.nombre.lower()

            #     ## Sitio no usa marcas
            else:
                # try:

                # except ObjectDoesNotExist:
                nombre = nombre.lower()
                
                newmarca = None
                existe_marca = False

                # lista_marcas = Marcas.objects.all()
                # for la_marca in lista_marcas:
                #     if la_marca.nombre.lower() in nombre:
                #         # print(f'marca ennconntrada {la_marca.nombre}')
                #         newmarca = Marcas.objects.filter(nombre=la_marca.nombre).get()
                #         newmarca_str = newmarca.nombre.lower()
                #         existe_marca = True
                #         break

                # if not existe_marca:
                #     ### Nueva lista de Marcas
                #     lista_marcas = MarcasSistema.objects.all()
                #     for la_marca in lista_marcas:
                        
                #         if la_marca.nombre.lower() in nombre:

                #             try:
                #                 # print(f'Agegando marca {la_marca.nombre}')
                #                 newmarca, created = Marcas.objects.get_or_create(nombre=la_marca.nombre)
                #             except:
                #                 print('Algunn tipo de errrorr')

                #             newmarca_str = newmarca.nombre.lower()
                            
                #             existe_marca = True
                #             break
                        
                #         # if existe_marca:
                #         #     break
                
                if not existe_marca:
                    # newmarca = Marcas.objects.filter(nombre='').get()
                    # newmarca_str = newmarca.nombre.lower()
                     ## NO SE AGRERGA
                    articulos_marca_vacio = articulos_marca_vacio + 1
                    continue

                
            #### Limpieza del nombre
            # 0, pasa a minusculas
            nombre = nombre.lower()
            # 1, si marca existe dentro del nombre entonces quitar la marca dentro del nombre
            #    Registros de articulo: Antes=30127, Despues=30128
            ##   al 28-10 18.40  = 28062
            ##   al 30-10 17.03  = 26863
            ##   al 30-10 17.35  = 26718
            ##   al 30-10 18.37  = 26329
            ##   al 31-10 10.25  = 29617             ## Sin incluir Cugat
            ##   al 31-10 18.39  = 20750    # Jumbo en proceso
            ##   al 31-10 19.00  = 21663
            ##   al  2-11 12.03  = 45024
            ##   al  2-11 15.00  = 47522
            ##   al  2-11 15.39  = 47285 - 123 paginas sinn marca -- queda 98
            ##   al  2-11 16.43  = 47139 -  98 paginas 
            ##   al  2-11 17.06  = 47093 -  
            ##   al  3-11 09.49  = 46898
            ##   al  3-11 13.12  = 47632
            ##   al  3-11 16.14  = 47572
            ##   al  4-11 08.55  = 48518
            ##   al  4-11 09.31  = 49360  tasa 4.0013
            ##   al  4-11 10.37  = 50350  tasa 4.611552140702613 Easy en imporrtacionn
            ##   al  4-11 10.37  = 51061  tasa 4.642959004458321 Easy en imporrtacionn
            ##   al  4-11 12.39  = 49260  tasa 5.622397922157289 Easy en imporrtacionn
            ##   al  4-11 19.19  = 56822  tasa 5.65621526959216  Falabella en importacion

            # ## 1.1 rermueve palabras duplicadas
            # nombre = nombre.split()
            # nombre = (" ".join(sorted(set(nombre), key=nombre.index)))

            ## 1.


            # nombre =  nombre.replace(newmarca.nombre,'')
            ### Esto  genera  errores,  por  ejemplo:
            #  Si nombre  es  'Vino Carmenere Winemaker'S 750 Cc'
            #  y la marca es 'Carmen'
            #  Entonces el nombre queda 'Vino ere Winemaker'S'
            ## Se modifica agrregando un espacio a la marca
            # if newmarca.get('nombre') != "":
            if newmarca_str != "":
                nombre =  nombre.replace(newmarca_str+' ','')


            def remueveYGuarda(OBJETO, en_que_texto, split_por, remover=False):
                salir = False
                arr_nombre = en_que_texto.split(split_por)
                devuelve_palabra = ''
                for sacable in OBJETO:
                    for palabra in arr_nombre:
                        if palabra == sacable:
                            devuelve_palabra = palabra
                            if remover:
                                en_que_texto = en_que_texto.replace(palabra,'')
                            salir = True
                            break
                    
                    if salir:
                        break
                
                return devuelve_palabra, en_que_texto


            ## 1.4 Remueve colores
            color, nombre = remueveYGuarda(COLORES, nombre, " ", remover=True)
            # color = ''
            # arr_nombre = nombre.split(" ")
            # salir = False
            # for sufijo_color in COLORES:
            #     for palabra in arr_nombre:
            #         if palabra == sufijo_color:
            #             color = palabra
            #             nombre = nombre.replace(palabra,'')
            #             salir = True
            #             break
                
            #     if salir:
            #         break

            # 1.5 rremueve todos los ', 1 Un'
            # nombre =  nombre.replace(', 1 un','')
            # nombre =  nombre.replace(', 1 un.','')
            # nombre =  nombre.replace(' 1 un','')
            # nombre =  nombre.replace(' 1 un.','')
            nombre =  nombre.replace('display','')
            

            # 2, rrremovver palabras  inutiles, como 'c/u'
            nombre =  nombre.replace('c/u','')

            # 2.1, Descomposicion de palabras del nombre
            arr_nombre = nombre.split(" ")

            # 2.2 mueve ennvases
            envase, nombre = remueveYGuarda(COLORES, nombre, " ", remover=True)
            # envase = ''
            # salir = False
            # for tipoenvase in ENVASES:
            #     for palabra in arr_nombre:
            #         palabra = palabra.rstrip()
            #         if tipoenvase == palabra:
            #             envase = palabra
            #             nombre = nombre.replace(palabra,'')
            #             salir = True
            #             break
            #     if salir:
            #         break

            nombre =  nombre.rstrip()

            # 2.5 remueve palabras que contienen tal caracter
            # nombre =  nombre.replace('°','° ')
            # nombre      = quita_word(nombre,'°')
            # º Gl
            nombre =  nombre.replace('º gl','° ')
            nombre,  grados = quita_word(nombre,'°')
            


            # 3, Descomposicion de palabras del nombre
            arr_nombre = nombre.split(" ")


            ## 4 Rretiro de sufijos como 'Aprox' 
            agregar_sufijos = ''
            for sufijo in SUJIFOS_NOMBRE:
                for palabra in arr_nombre:
                    palabra = palabra.rstrip()
                    if sufijo == palabra:
                        agregar_sufijos = agregar_sufijos + ' ' + palabra
                        nombre = nombre.replace(palabra,'')
            
            # 4.1, RRegenera Descomposicion de palabras del nombre
            arr_nombre = nombre.split(" ")

            # 4.2 Unidades
            unidades = 1
            um_text = arr_nombre[len(arr_nombre)-1]
            um_cant = arr_nombre[len(arr_nombre)-2]
            um_text = um_text.rstrip()
            if um_text in UNIDADES and check_sinum(um_cant):
                unidades = um_cant
                retira = um_cant  + ' ' + um_text
                nombre =  nombre.replace(retira,'')

            unidades  =  float(unidades)
            # 4.3, RRegenera Descomposicion de palabras del nombre
            arr_nombre = nombre.split(" ")

            um_text = ""
            um_cant = ""
            palabra = 1
            max_palabras = len(arr_nombre)
            retira = ""
            while True:
                um_text = arr_nombre[len(arr_nombre)-palabra]
                um_cant = arr_nombre[len(arr_nombre)-(palabra+1)]

                um_text = um_text.rstrip()
                # print(um_text,' ->',  um_cant)
                
                if um_text in UM and check_sinum(um_cant):
                    retira = um_cant  + ' ' + um_text
                    break
                else:
                    paso = getStringAndNumbers(um_text)
                    if len(paso) == 1:
                        um_text = paso[0]
                        if um_text in UM :
                            um_cant = '1'
                            retira = um_text
                            break

                    if len(paso) == 2:
                        print('larrgo  2')

                    if len(paso) == 3:
                        um_text = paso[2]
                        um_cant = paso[1]
                        if um_text in UM :
                            if check_sinum(um_cant):
                                retira = um_cant  + '' + um_text
                                # retira = um_cant  + ' ' + um_text
                                break
                            else:
                                print(um_cant)
                                ## Podria ser:   1/4 o nada

                    # # else:
                    # #     um_text = ""
                    # #     um_cant = ""
                    # #     break

                palabra = palabra + 1
                if palabra > max_palabras:
                    um_text = ""
                    um_cant = ""
                    break
               
            um_text = normalizeUM(um_text)
            # um_cant = normalizeCANT(um_cant)
            um_cant, um_text = normalizeCANTyUM(um_cant, um_text)
            
            if um_cant > 0 :
                medida = str(um_cant) + ' ' + um_text
            else:
                medida =  um_text
            nombre =  nombre.replace(retira,'')

             # 2.2 mueve ennvases NUEVAMENTE
            salir = False
            nombre      =  nombre.rstrip()
            arr_nombre = nombre.split(" ")
            if envase == "":
                for tipoenvase in ENVASES:
                    for palabra in arr_nombre:
                        palabra = palabra.rstrip()
                        if tipoenvase == palabra:
                            envase = palabra
                            nombre = nombre.replace(palabra,'')
                            salir = True
                            break
                    if salir:
                        break
            

            nombre      =  nombre.rstrip()
            medida      =  medida.rstrip()

             ## 1.2 Quitar acentos
            nombre = unidecode.unidecode(nombre)

            nombre      = nombre + ' ' +  agregar_sufijos 

            nombre = nombre.rstrip()
            if  len(nombre)  > 1:
                if nombre[-1] == ','  or nombre[-1] == '-'  or nombre[-1] == '.' :
                    nombre = nombre[:-1] 
            
                
            nombre = nombre.title()


            
            try:
                miarticulo, created = Articulos.objects.get_or_create (\
                    marca=newmarca,
                    nombre=nombre,
                    medida=medida, 
                    nombre_original=nombre_original,
                    unidades=unidades,
                    color=color,
                    envase=envase,
                    grados=grados

                    )
                articulos_creados = articulos_creados + 1
            except:
                miarticulo  = Articulos.objects.get(
                    marca=newmarca,
                    nombre=nombre,
                    medida=medida
                )
                articulos_existentes = articulos_existentes  + 1

            # except ObjectDoesNotExist:


            ### Vendedores
            Vendedores.objects.update_or_create(articulo=miarticulo, vendidoen=url)
            
            if  registros % 300 == 0:
                print(f'{site.siteName} registros= {registros} creados = {articulos_creados} existentes= {articulos_existentes}  vacios={articulos_nombre_vacio}  Tasa={(articulos_existentes/articulos_creados)  * 100}')
            if registros > 500:
                break


    print("Fin CreateProds")

#########


@shared_task(queue='core_calc',bind=True)
# @shared_task(bind=True)
def getSiteURLS(request):
    print("getSiteURLS")
    sites = Site.objects.filter(siteSearchEnabled=True)
    for site in sites:
        management.call_command('getSiteURL', site.id)
    print("Fin getSiteURLS")


# @shared_task(bind=True)
@shared_task(queue='core_front',bind=True)
def getProductsSelenium(request):
    # print("getProducts")
    sites = Site.objects.filter(productSearchEnabled=True,crawler=PAGECRAWLER.SELENIUM)
    for site in sites:
        management.call_command('getProducts-selenium', site.id)
    # print("Fin getProducts")s

@shared_task(queue='core_front',bind=True)
def getProductsBeautiful(request):
    # print("getProducts")
    sites = Site.objects.filter(productSearchEnabled=True,crawler=PAGECRAWLER.BEAUTIFULSOUP)
    for site in sites:
        management.call_command('getProducts-beautiful', site.id)
        # ret_val = management.call_command('graphservers', int(got_id))
    # print("Fin getProducts")s


# # print(ultima_palabra)
            # if  ultima_palabra == 'cc' or \
            #     ultima_palabra == 'c' or \
            #     ultima_palabra == 'ml' or \
            #     ultima_palabra == 'l' or \
            #     ultima_palabra == 'lt' or \
            #     ultima_palabra == 'un' or \
            #     ultima_palabra == 'g' or \
            #     ultima_palabra == 'gr' or \
            #     ultima_palabra == 'grs' or \
            #     ultima_palabra == 'm' or \
            #     ultima_palabra == 'mm' or \
            #     ultima_palabra == 'un' or \
            #     ultima_palabra == 'un.' or \
            #     ultima_palabra == 'k' or \
            #     ultima_palabra == 'kg' or \
            #     ultima_palabra == 'kg.' or \
            #     ultima_palabra == 'kl' or \
            #     ultima_palabra == 'cm' or \
            #     ultima_palabra == 'bolsitas' or \
            #     ultima_palabra == 'meses'  or \
            #     ultima_palabra == 'gb'  or \
            #     ultima_palabra == 'mt'  or \
            #     ultima_palabra == 'mts'  or \
            #     ultima_palabra == 'metro'  or \
            #     ultima_palabra == 'metros' :

            #     if ultima_palabra == 'l':
            #         ultima_palabra = 'lt' 

            #     if ultima_palabra == 'g' or ultima_palabra == 'grs' :
            #         ultima_palabra = 'gr' 
                
            #     if ultima_palabra == 'kl':
            #         ultima_palabra = 'kg' 
                
            #     if ultima_palabra == 'un.':
            #         ultima_palabra = 'un'

            #     if ultima_palabra == 'mts'  or \
            #         ultima_palabra == 'metro' or \
            #         ultima_palabra == 'metros':
            #         ultima_palabra = 'mt'