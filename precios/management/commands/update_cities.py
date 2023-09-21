from django.core.management.base import BaseCommand

from precios.models import (Cities)
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="devop-pi")
import time

class Command(BaseCommand):
    help = "Start the simulation"

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        cities = Cities.objects.filter(latitude=0).order_by('-region__id')

        for city in cities:
            
            nombre = city.name + ', '+  str(city.region.name) + ', ' + str(city.country.name)
            print(nombre)
            location = geolocator.geocode(nombre, timeout=5)
            if location is not None:
                # print(location.address)
                print((location.latitude, location.longitude))
                city.latitude = location.latitude
                city.longitude = location.longitude
                city.save()
            else:
                print("No se pudo obtener la información geográfica")
            
            time.sleep(5)
    