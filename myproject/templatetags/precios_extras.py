from django import template
# from django.conf import settings
from typing import List, Optional
from precios.models import (
    Vendedores,
)
register = template.Library()


def cuanntosvenden(art_id, vendedores:List[int]=None):
    mp = Vendedores.objects.filter(articulo__id=art_id)
    if vendedores:
        mp = mp.filter(vendidoen__site__in=vendedores)
        print('con filtro')
    else:
        print('SIN filtro')
    mp = mp.count()
    return mp



register.filter('cuanntosvenden', cuanntosvenden)