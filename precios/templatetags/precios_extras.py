from django import template
from typing import List
from precios.models import (
    Vendedores,
)
register = template.Library()

@register.simple_tag
def precios_extras():
    return ''

@register.simple_tag
def cuanntosvenden(art_id, vendedores:List[int]=None):
    mp = Vendedores.objects.filter(articulo__id=art_id).filter(vendidoen__site__in=vendedores).exclude(vendidoen__precio__exact=0)
    
    mp = mp.count()
    return mp



@register.filter(name='replace_comma')
def replace_comma(value):
    return str(value).replace(',', '')