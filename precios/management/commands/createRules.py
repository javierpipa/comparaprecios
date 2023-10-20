from django.core.management.base import BaseCommand
from precios.models import  Marcas, Site
from django.core import management
from celery import chain, group

from precios.tasks import (limpiar_y_borrar_inicial, rules_marcas, 
                            limpiar_y_borrar_normal, CreateProds, limpiar_final,
                            elimina_relacion_reglas, generar_una_regla, hace_nada)

class Command(BaseCommand):
    help = "Start the simulation"

    def __init__(self):
        super().__init__()
    
    def add_arguments(self, parser):
        parser.add_argument('--marcaid', type=int, help='Marca id', default=None)
        parser.add_argument('--crear', type=bool, help='Solo crear articulos', default=False)


    def handle(self, *args, **options):
    
        marcaid     = options["marcaid"]
        print(marcaid)

        # sites = Site.objects.filter(enable=True).order_by('-id')[0:5]
        sites = Site.objects.filter(enable=True).order_by('-id')
        sites = sorted(sites, key=lambda a: a.urlCount, reverse=True)
        tasks_for_sites = [CreateProds.s(site.id) for site in sites]
        group_tasks_sites = group(tasks_for_sites)
        
        if marcaid:
            marcas = Marcas.objects.filter(id=marcaid)
        else:
            # marcas = Marcas.objects.filter(es_marca=True)[0:100]
            marcas = Marcas.objects.filter(es_marca=True)

        tasks_for_marcas = [generar_una_regla.s(marca.id) for marca in marcas]
        # print(tasks_for_marcas)
        group_tasks_marcas = group(tasks_for_marcas)

        if options["crear"]:
            pipeline = chain(
                limpiar_y_borrar_inicial.s(),
                elimina_relacion_reglas.s(),
                rules_marcas.s(marcaid),
                group_tasks_marcas,
                limpiar_y_borrar_normal.s(),
                group_tasks_sites,
                limpiar_final.s(marcaid),
                ## 2da parte 
                rules_marcas.s(marcaid),
                group_tasks_marcas,
                limpiar_y_borrar_normal.s(),
                group_tasks_sites,
                limpiar_final.s(marcaid),
            )
        else:
            pipeline = chain(
                hace_nada.s(),
                rules_marcas.s(marcaid),
                group_tasks_marcas,
                limpiar_y_borrar_normal.s(),
                group_tasks_sites,
                limpiar_final.s(marcaid),
            )

        result = pipeline.apply_async()
        print(result)
        ######## FIN  Programa #########

    
