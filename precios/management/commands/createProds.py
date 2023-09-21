from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Count, Q
from precios.models import (
    Site, 
    SiteURLResults,
    Marcas,
)
import re


from precios.pi_get import (
    create_prods,
    get_dics
) 
class Command(BaseCommand):
    help = "Start the simulation"

    def __init__(self):
        super().__init__()
        self.links = []
        self.debug = False

        self.articulos_creados = 0
        self.articulos_existentes = 0
        self.articulos_nombre_vacio = 0
        self.articulos_marca_vacio = 0

        self.PALABRAS_INUTILES, \
            self.SUJIFOS_NOMBRE, \
            self.ean_13_site_ids, \
            self.UMEDIDAS, \
            self.UNIDADES, \
            self.PACKS, \
            self.TALLAS, \
            self.COLORES, \
            self.ENVASES, \
            self.marcas, \
            self.listamarcas,\
            self.marcasistema,\
            self.sin_marca, \
            self.listamarcas, \
            self.campoMarcaObj = get_dics()
        
        
        print(len(self.listamarcas))


    def add_arguments(self, parser):
        parser.add_argument('SiteId', type=int, help='Id of VM to get info')
        parser.add_argument('Posicion', type=int, help='Posicion', default=1)
        parser.add_argument('--numrecords', type=int, help='Records to create', default=None)
        parser.add_argument('--urlid', type=int, help='URL to process', default=0)
        parser.add_argument('--debug', type=bool, help='Show debug values', default=False)
        parser.add_argument('--createRule', type=bool, help='Create new Rule?', default=False)
        parser.add_argument('--marcaid', type=int, help='Marca id', default=None)
        

    def handle(self, *args, **options):

        SiteId      = options["SiteId"]
        numRecords  = options["numrecords"]
        Posicion    = options["Posicion"]
        createRule  = options["createRule"]
        marcaid     = options["marcaid"]
        

        site = Site.objects.filter(id=SiteId).get()
        
        if options['urlid']:
            urls = SiteURLResults.objects.filter(pk=options['urlid'])
        else:
            if options['marcaid']:
                marcaObj = Marcas.objects.filter(id=marcaid).get()
                marca = marcaObj.nombre
                urls = SiteURLResults.objects.filter(
                    marca=marca, 
                    error404=False, 
                )
            else:
                urls = SiteURLResults.objects.filter(
                    site=site, 
                    error404=False, 
                )
            # .exclude(precio=0)

        if options['numrecords']:
            urls = urls[:numRecords]

        if options['debug']:
            print("DEBUG")
            self.debug = True

        print(len(urls))
        registros = 0

        create_prods(
                urls, 
                registros, 
                self.articulos_nombre_vacio, 
                self.debug, 
                self.campoMarcaObj,
                self.listamarcas,
                self.sin_marca,
                self.COLORES,
                self.PALABRAS_INUTILES,
                self.ENVASES,
                self.SUJIFOS_NOMBRE,
                self.TALLAS,
                self.UMEDIDAS,
                self.PACKS, 
                self.UNIDADES,
                self.ean_13_site_ids,
                site,
                self.articulos_existentes,
                self.articulos_creados,
                Posicion,
                createRule
            )
       

        try:
            print(f'{site.siteName} registros= {registros} creados = {self.articulos_creados} existentes= {self.articulos_existentes}  vacios={self.articulos_nombre_vacio}  Tasa={(self.articulos_existentes/self.articulos_creados)  * 100}')
        except:
            pass


        print("Fin CreateProds")


