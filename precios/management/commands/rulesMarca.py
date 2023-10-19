from django.core.management.base import BaseCommand
from precios.models import Marcas

from precios.pi_functions import (
    setMessage, 
)   
from precios.pi_rules import (
    intenta_marca,
)
  
class Command(BaseCommand):
    help = "Start the simulation"

    def __init__(self):
        super().__init__()

    def add_arguments(self, parser):
        parser.add_argument('marcaid', type=int, help='Marca id')
        

    def handle(self, *args, **options):
        marcaid     = options["marcaid"]
        # marca       = Marcas.objects.filter(id=marcaid).first()
        
        setMessage(f'Generando REGLAS {marca}')
        intenta_marca(marcaid, False)

        setMessage('')
    
        ######## FIN  Programa #########

    
