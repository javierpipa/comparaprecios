# sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from precios.models import Marcas, Articulos 
from django.db.models import Count


class MarcasSitemap(Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return Marcas.objects.all()[0:100]

    # def location(self, item):
    #     return reverse(item)

class ArticulosSitemap1(Sitemap):

    
    pagina = 1
    desde   = (( pagina - 1 ) * 1000 ) + 1
    hasta   = (( pagina     ) * 1000 ) - 1

    priority = 0.5
    changefreq = "daily"

    def items(self):
        return Articulos.objects.all()[self.desde:self.hasta]



