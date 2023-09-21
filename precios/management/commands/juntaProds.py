from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from precios.models import (
    Site, 
    Campos,
    CamposEnSitio,
    SiteURLResults,
    SELECTOR,
    DONDESEUSA,
    PAGECRAWLER,
    Marcas, 
    Articulos,
    Vendedores,
    MarcasSistema,
    Unifica
)
from itertools import combinations





# 1. ciclo por marca
#     set cuantos_productos_en_marca

#     1.1 todas las reglas de esta marca
#         1.1.1 Eliminar reglas con contador = 0

#     1.2 todos los articulos de esta marca
#         1.2.1 Si hay un solo vendedor y cuantos_productos_en_marca > 1
#             1.2.1.1 
#                 - Leer campos:
#                     tengo_marca         = marca
#                     tengo_nombre        = nombre
#                     tengo_grados        = grados
#                     tengo_medida_cant   = medida_cant
#                     tengo_unidades      = unidades

#                 1.2.1.1.1 Si tengo algun campo en blanco ?

#                     - Si Existe articulo que coincida con tengo_marca,     , tengo_grados, tengo_medida_cant, tengo_unidades y que este vendedor no exista
#                     - Si Existe articulo que coincida con tengo_marca, tengo_nombre,   , tengo_medida_cant, tengo_unidades y que este vendedor no exista
#                     - Si Existe articulo que coincida con tengo_marca, tengo_nombre, tengo_grados,     , tengo_unidades y que este vendedor no exista
#                     - Si Existe articulo que coincida con tengo_marca, tengo_nombre, tengo_grados, tengo_medida_cant,  y que este vendedor no exista
                    
                        
#                         Entonces: Crear regla con:
#                             Si:
#                                 marca       = tengo_marca
#                                 Nombre      = tengo_nombre
#                                 grados      = tengo_grados
#                                 medida_cant = tengo_medida_cant
#                                 unidades    = tengo_unidades
#                             Entonces:
#                                 marca       = tengo_marca
#                                 Nombre      = tengo_nombre
#                                 grados      = tengo_grados
#                                 medida_cant = tengo_medida_cant
#                                 unidades    = tengo_unidades
#                             contador = 0
#                             automatico = True



#                  Si coincide (marca), nombre, grados, medida_cant
#                     crear regla 
#                     , unidades


#         1.2.2 Hay vendedores duplicados
#             Hay alguno de productos con regla ?
#                 indicar que regla es posiblemente mala


class Command(BaseCommand):
    help = "Start the simulation"

    def __init__(self):
        super().__init__()


    def elimina_reglas_con_cero(self, si_marca):
        # 1.1.1 Eliminar reglas con contador = 0

        # print(f'reglas de marca {si_marca} = {Unifica.objects.filter(si_marca=si_marca, automatico=True, contador=0).count()}')
        Unifica.objects.filter(si_marca=si_marca, automatico=True, contador=0).delete()


        # busca_articulo(tengo_marca, tengo_nombre, tengo_grados, tengo_medida_cant, tengo_unidades, pero_no, nombre_none, grados_none, medida_cant_none, unidades_none)
    def busca_articulo(self, newmarca, nombre, grados, medida_cant, unidades, pero_no, nombre_none, grados_none, medida_cant_none, unidades_none):
        # print(f'pero_no llegado ={pero_no}')
        # Buscamos todas las combinaciones posibles de palabras
        # print(f'En la busqeda articulos llega nombre={nombre}, pero_np={pero_no}')
        palabras = nombre.lower().split()
        combinaciones_palabras = []
        for i in range(1, len(palabras) + 1):
            combinaciones_palabras.extend(list(combinations(palabras, i)))

        
        # Buscamos si alguna combinación de palabras encuentra un articulo
        articulo_encontrado = None
        salir = False
        intentos = 0
        metodo = None
        for combinacion in combinaciones_palabras:
            nombre_articulo = " ".join(combinacion)
            
            ## Completo
            if Articulos.objects.filter(nombre__istartswith=nombre_articulo, marca__nombre__iexact=newmarca, medida_cant=medida_cant, unidades=unidades, grados=grados).exclude(id=pero_no).exists():
                articulos = Articulos.objects.filter(nombre__istartswith=nombre_articulo, marca__nombre__iexact=newmarca, medida_cant=medida_cant, unidades=unidades, grados=grados).exclude(id=pero_no)
                # if articulos.__len__() == 1 :
                for mm_articulo in articulos:
                    # print(f'Debeser={nombre}   busconombre_articulo= {nombre_articulo} Encuentra={mm_articulo.nombre} {len(articulos)}')
                    intentos = intentos + 1
                    if nombre in mm_articulo.nombre :
                        articulo_encontrado = mm_articulo
                        metodo = "entero"
                        salir = True
                        break
                if salir:
                    break

            # ## Sin grados
            # if Articulos.objects.filter(nombre__istartswith=nombre_articulo, marca__nombre__iexact=newmarca, medida_cant=medida_cant, unidades=unidades).exclude(id=pero_no).exists() and not articulo_encontrado:
            #     articulos = Articulos.objects.filter(nombre__istartswith=nombre_articulo, marca__nombre__iexact=newmarca, medida_cant=medida_cant, unidades=unidades).exclude(id=pero_no)
            #     # if articulos.__len__() == 1 :
            #     for mm_articulo in articulos:
            #         # print(f'Sin grados Debeser={nombre}   busconombre_articulo= {nombre_articulo} Encuentra={mm_articulo.nombre} {len(articulos)}')
            #         intentos = intentos + 1
            #         if nombre in mm_articulo.nombre :
            #             articulo_encontrado = mm_articulo
            #             metodo = "singrados"
            #             salir = True
            #             break
            #     if salir:
            #         break
        return articulo_encontrado, metodo

    def ciclo_articulos(self, articulos, cuantos_productos_en_marca): 
        for articulo in articulos:
            cuantos_venden = articulo.resultsCount
            if cuantos_venden == 1 and cuantos_productos_en_marca > 1:

                ## Pero no me busque a mi
                pero_no = articulo.pk
                # print(f'pero_no={pero_no}')

                # - Leer campos:
                tengo_marca         = articulo.marca
                tengo_nombre        = articulo.nombre
                tengo_grados        = articulo.grados
                tengo_medida_cant   = articulo.medida_cant
                tengo_unidades      = articulo.unidades

                marca_none          = False         ## Siempre hay marca
                nombre_none         = False
                grados_none         = False
                medida_cant_none    = False
                unidades_none       = False
                if tengo_nombre.strip() == '':
                    nombre_none         = True

                if tengo_grados.strip() == '':
                    grados_none         = True

                if tengo_medida_cant == 0.0 :
                    medida_cant_none    = True

                if tengo_unidades == 0:
                    unidades_none       = True


                art_enco, metodo = self.busca_articulo(tengo_marca, tengo_nombre, tengo_grados, tengo_medida_cant, tengo_unidades, pero_no, nombre_none, grados_none, medida_cant_none, unidades_none)

                if art_enco:
                    print(f'Exito con metodo={metodo} id={articulo.pk} cuantos_venden = {cuantos_venden}')
                    si_marca        =   articulo.marca
                    si_nombre       =   articulo.nombre
                    si_grados       =   articulo.grados
                    si_medida_cant  =   articulo.medida_cant
                    si_unidades     =   articulo.unidades

                    entonces_marca  =   art_enco.marca
                    entonces_nombre =   art_enco.nombre
                    # if metodo == "singrados":
                    #     entonces_grados = articulo.grados
                    # else:
                    entonces_grados = art_enco.grados

                    entonces_medida_cant= art_enco.medida_cant
                    entonces_unidades   = art_enco.unidades

                    # print(f'Si          marca={si_marca}: nombre={si_nombre} grados={si_grados} medida_cant={si_medida_cant} unidades={si_unidades}')
                    # print(f'Entonces    marca={entonces_marca}: nombre={entonces_nombre} grados={entonces_grados} medida_cant={entonces_medida_cant} unidades={entonces_unidades} ')
                    Unifica.objects.update_or_create(
                        si_marca=si_marca,
                        si_nombre=si_nombre,
                        si_grados=si_grados, 
                        si_medida_cant=si_medida_cant,
                        si_unidades=si_unidades,
                        entonces_marca=entonces_marca,
                        entonces_nombre=entonces_nombre,
                        entonces_grados=entonces_grados,
                        entonces_medida_cant=entonces_medida_cant,
                        entonces_unidades=entonces_unidades,
                        contador=0,
                        automatico=True
                        )
                    # reglas_creados = reglas_creados + 1

                    

                # 1.2.1.1.1 Si tengo algun campo en blanco ?
                # if nombre_none or grados_none or medida_cant_none or unidades_none:
                #     # print('Tengo algo en blanco ==================================')
                #     # print(f'marca={articulo.marca.nombre}: nombre={articulo.nombre} grados={articulo.grados} medida_cant={articulo.medida_cant} unidades={articulo.unidades}   cuantos_venden = {cuantos_venden}')

                #     # if nombre_none :
                #     #     print(f'tengo nombre en blanco = {tengo_nombre}')
                #     # if grados_none :
                #     #     print(f'tengo tengo_grados en blanco = {tengo_grados}')
                #     # if medida_cant_none:
                #     #     print(f'tengo tengo_medida_cant en blanco = {tengo_medida_cant}')
                #     # if unidades_none:
                #     #     print(f'tengo tengo_unidades en blanco = {tengo_unidades}')
                    
                #     art_enco, metodo = self.busca_articulo(tengo_marca, tengo_nombre, tengo_grados, tengo_medida_cant, tengo_unidades, pero_no, nombre_none, grados_none, medida_cant_none, unidades_none)
                #     if art_enco:
                #         print(f'Exito con metodo={metodo} marca={articulo.marca.nombre}: nombre={articulo.nombre} grados={articulo.grados} medida_cant={articulo.medida_cant} unidades={articulo.unidades}')
                #         print(f'Si          marca={articulo.marca.nombre}: nombre={articulo.nombre} grados={articulo.grados} medida_cant={articulo.medida_cant} unidades={articulo.unidades}   cuantos_venden = {cuantos_venden}')
                #         print(f'Entonces    marca={art_enco.marca.nombre}: nombre={art_enco.nombre} grados={art_enco.grados} medida_cant={art_enco.medida_cant} unidades={art_enco.unidades}   cuantos_venden = {cuantos_venden}')
                # else:
                    
                #     art_enco, metodo = self.busca_articulo(tengo_marca, tengo_nombre, tengo_grados, tengo_medida_cant, tengo_unidades, pero_no)
                #     if art_enco:
                #         print(f'Exito con metodo={metodo} marca={articulo.marca.nombre}: nombre={articulo.nombre} grados={articulo.grados} medida_cant={articulo.medida_cant} unidades={articulo.unidades}')
                #         # print('Tengo todos los datos ==================================')
                #         # print(f'Si          marca={articulo.marca.nombre}: nombre={articulo.nombre} grados={articulo.grados} medida_cant={articulo.medida_cant} unidades={articulo.unidades}   cuantos_venden = {cuantos_venden}')
                #         # print(f'Entonces    marca={art_enco.marca.nombre}: nombre={art_enco.nombre} grados={art_enco.grados} medida_cant={art_enco.medida_cant} unidades={art_enco.unidades}   cuantos_venden = {cuantos_venden}')
                #         # print(art_enco)


    def ciclo_marcas(self, cuantas_marcas_cuenta):
        # 1.2 todos los articulos de esta marca
        self.cuenta_marcas = 0

        marcas = Marcas.objects.all()
        for marca in marcas:
            self.cuenta_marcas = self.cuenta_marcas + 1
            # 1.1.1 Eliminar reglas con contador = 0
            self.elimina_reglas_con_cero(marca)

            cuantos_productos_en_marca  = marca.resultsCount
            quienes_venden              = marca.vendedoresList
            cuantos_venden              = len(list(quienes_venden))
            
            if cuantos_venden > 1 and cuantos_productos_en_marca > 1:
                # print(f'marca={marca}   cuantos_venden={cuantos_venden}  cuantos_productos_en_marca={cuantos_productos_en_marca}')
                articulos = Articulos.objects.filter(marca=marca)
                self.ciclo_articulos(articulos, cuantos_productos_en_marca)
            # else:
            #     print(f'salto')

            if self.cuenta_marcas > cuantas_marcas_cuenta:
                return

    def handle(self, *args, **options):
        # 1. ciclo por marca
        mm_marcas = self.ciclo_marcas(6000)





    def otro():
        pass
        # ### Primera ejecucion
        # arts = Articulos.objects.all()
        # arts = arts.exclude(ean_13 ='')
        # arts = arts.order_by('ean_13')
        # cuenta_encontrados = self.junta_ean13(arts)
        # print("cuenta_encontrados= ", cuenta_encontrados)


        # # ### Bien, ejecutar !!!
        # arts = Articulos.objects.all()
        # arts = arts.exclude(ean_13 ='')
        # arts = arts.filter(grados='')
        # cuenta_encontrados = self.limpia_grados(arts)
        # print("cuenta_encontradoscuenta_encontrados= ", cuenta_encontrados)

        ## Se juntan aquellos con mismas caracteristicas de:
        #  - Marca
        #  - unidad de medida
        #  - unidades
        #  - Nombre parecido
        # arts = Articulos.objects.all()
        # arts = arts.order_by('pk')
        # cuenta_encontrados = self.limpia_nombre(arts)
        # print("cuenta_encontradoscuenta_encontrados= ", cuenta_encontrados)





        # arts = Articulos.objects.all()
        # arts = arts.filter(grados='')
        # arts = arts.order_by('pk')
        # cuenta_encontrados = self.limpia(arts, 1)
        

        # print("cuenta_encontradoscuenta_encontrados= ", cuenta_encontrados)

            # def limpia_grados(self, arts):
        #     cuenta_encontrados = 0
        #     print(len(arts))
        #     for art in arts:
        #         id_correcto           = art.pk
                
        #         nombre_correcto       = art.nombre
        #         marca_correcto        = art.marca
        #         um_cant_correcto      = art.medida_cant
        #         grados_correcto       = art.grados
        #         unidades_correcto     = art.unidades

        #         grados_correcto = grados_correcto.strip()
                    
        #         busqueda = Articulos.objects.filter(
        #             marca                   = marca_correcto,
        #             nombre__iexact          = nombre_correcto,
        #             medida_cant             = um_cant_correcto,
        #             unidades                = unidades_correcto,
        #             # ean_13                  = ''
        #             ).exclude(id=id_correcto)

        #         for encontrado in busqueda:
        #             print("nombre correcto.. ", nombre_correcto, "  nombre encontrado= ", encontrado.nombre )
        #             # ," Marca=", marca_correcto, ' Y venden=', encontrado.cuanntosvenden)
                    
        #             ### El vendedor
        #             vendidoen = Vendedores.objects.filter(
        #                 articulo = encontrado
        #             )
        #             if grados_correcto == '' and grados_correcto != encontrado.grados:
        #                 # print('diferencia de grados, correcto=', grados_correcto, ' enncontrado', encontrado.grados)
        #                 art.grados = encontrado.grados
        #                 art.save()
        #             for ven in vendidoen:
        #                 ven.articulo = art
        #                 ven.save()
        #             encontrado.delete()

        #             cuenta_encontrados = cuenta_encontrados + 1
                            
        #     return cuenta_encontrados

        # def limpia_nombre(self, arts):
        #     cuenta_encontrados = 0
        #     print(len(arts))
        #     for art in arts:
        #         id_malito           = art.pk
                
        #         nombre_malito       = art.nombre
        #         marca_malito        = art.marca
        #         um_cant_malito      = art.medida_cant
        #         grados_malito       = art.grados
        #         unidades_malito     = art.unidades

        #         grados_malito = grados_malito.strip()
                    
        #         busqueda = Articulos.objects.filter(
        #             marca                   = marca_malito,
        #             nombre__startswith      = nombre_malito,
        #             medida_cant             = um_cant_malito,
        #             unidades                = unidades_malito,
        #             grados                  = grados_malito
        #             ).exclude(id=id_malito)
        #         if busqueda:
        #             print('Cuantos  ', len(busqueda))
        #             for encontrado in busqueda:
        #                 print("Buscando.. ", nombre_malito, " Marca=", marca_malito, um_cant_malito, unidades_malito)
        #                 # print("encontro.. ", encontrado.nombre, " Marca=",encontrado.marca, encontrado.medida_cant, encontrado.unidades, ' Y venden=', encontrado.cuanntosvenden)

        #                 if encontrado.cuanntosvenden > 0:
        #                     ## Intento mover el vendedor Malito
        #                     id_articulo_correcto = encontrado
        #                     ### El vendedor
        #                     vendidoen = Vendedores.objects.filter(
        #                         articulo = id_malito
        #                     )
        #                     if vendidoen:
        #                         for ven in vendidoen:
        #                             ven.articulo = id_articulo_correcto
        #                             ven.save()
        #                         art.delete()

        #                     cuenta_encontrados = cuenta_encontrados + 1
                        
        #     return cuenta_encontrados

        # def junta_ean13(self, arts):
        #     cuenta_encontrados = 0
        #     print(len(arts))
        #     for art in arts:
        #         id_malito           = art.pk
        #         ean_13_malito       = art.ean_13
        
        #         busqueda = Articulos.objects.filter(
        #             ean_13                  = ean_13_malito,
        #             ).exclude(id=id_malito)
                
                
        #         for encontrado in busqueda:
        #             print('Cuantos  ', len(busqueda))
                    
        #             ## Intento mover el vendedor Malito
        #             id_articulo_correcto = encontrado
        #             ### El vendedor
        #             vendidoen = Vendedores.objects.filter(
        #                 articulo = id_malito
        #             )
        #             if vendidoen:
        #                 for ven in vendidoen:
        #                     ven.articulo = id_articulo_correcto
        #                     ven.save()
        #                 art.delete()

        #             cuenta_encontrados = cuenta_encontrados + 1
                        
        #     return cuenta_encontrados