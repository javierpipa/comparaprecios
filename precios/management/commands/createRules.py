from django.core.management.base import BaseCommand
from precios.models import SiteURLResults, Articulos, Unifica, Marcas, Vendedores, MarcasSistema, Site, Settings, AllPalabras, ReemplazaPalabras
from django.core import management


from precios.pi_functions import (
    setMessage, 
)   
from precios.pi_rules import (
    intenta_marca,
    createRule, 
)
from precios.pi_get import reemplaza_palabras        
from precios.tasks import (
    CreateProdsAll,
    
)



class Command(BaseCommand):
    help = "Start the simulation"

    def __init__(self):
        super().__init__()
    
    # def CreateMarcasRules(self):
    #     result = RulesMarcasAll.apply_async()
    #     result.get()

    def create_articles(self, marcaid):
        if marcaid:
            sites = Site.objects.filter(enable=True)
            posicion = 0
            for site in sites:
                posicion = posicion + 1
                management.call_command('createProds', site.id, posicion, f'--marcaid={marcaid}')

        else:
            # Articulos.objects.all().delete()
            # CreateProdsAll()
            result = CreateProdsAll.apply_async()
            result.get()
            # sites = Site.objects.filter(enable=True)
            # sites = sorted(sites, key=lambda a: a.urlCount, reverse=True)
            # posicion = 0
            # for site in sites:
            #     posicion = posicion + 1
            #     print(site.siteName)
            #     print('===========================================')
            #     management.call_command('createProds', site.id, posicion)

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
            intenta_marca(marca, False, None)
        

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
            if art.cuanntosvenden() == 0:
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

    
