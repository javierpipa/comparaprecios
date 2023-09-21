import django_filters
from precios.models import (
    Site, 
    Pages, 
    Campos,
    CamposEnSitio,
    SiteURLResults,
    Marcas,
    Articulos

)
class ArticulosFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Articulos
        fields = ['nombre', 'marca']