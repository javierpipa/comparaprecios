from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
# from django.db.models import Count, Sum, Q, Subquery, OuterRef
from django.db.models import Count

import csv
import codecs
from django.http import HttpResponse
from django.views.generic import TemplateView
import pandas as pd
import io


from .models import (
    Site, 
    SiteURLResults,
    Vendedores,
    Articulos,
    Marcas,
)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import (
    cache_page, 
    never_cache, 
)

from precios.pi_functions import (
    getMessage,
    registrar_consulta,
)

class CsvURLUploader(TemplateView):
    template_name = 'precios/csv_uploader.html'

    def post(self, request):
        context = {
            'messages':[]
        }
        updates = 0
        created = 0
        csv = request.FILES['csv']
        csv_data = pd.read_csv(
            io.StringIO(
                csv.read().decode("utf-8")
            )
        )

        for record in csv_data.to_dict(orient="records"):
            # print(record)
            d_siteid    = record['site']
            o_site      = Site.objects.get(pk=d_siteid)
            d_url       = record['url']
            try:
                if not SiteURLResults.objects.filter(site__id=d_siteid, url=d_url).exists():
                    print(f'Add url {d_url}')
                    created = created + 1
                    SiteURLResults.objects.create(
                        site        = o_site,
                        url         = d_url,
                        error404    = record['error404'],
                        precio      = record['precio'],
                        nombre      = record['nombre'],
                        idproducto  = record['idproducto'],
                        marca       = record['marca'],
                        image       = record['image']
                    )
                else:
                    print(f'Update url {d_url}')
                    updates = updates + 1
                    thisUrl = SiteURLResults.objects.filter(site__id=d_siteid, url=d_url).get()
                    thisUrl.updated(
                        error404    = record['error404'],
                        precio      = record['precio'],
                        nombre      = record['nombre'],
                        idproducto  = record['idproducto'],
                        marca       = record['marca'],
                        image       = record['image']
                    )
                    thisUrl.save()
            except Exception as e:
                context['exceptions_raised'] = e

        context = {
            'created': created,
            'updates': updates
        } 
        return render(request, self.template_name, context=context)



@never_cache
def siteUrlsinSite(request):
    id_super    = 4
    salida_csv = False
    orden       = 'precio'
    page_number = 1
    # if request.method == 'POST':
    #     print("Por post !")
    #     form = NameForm(request.POST)
    #     if form.is_valid():
    #         id_super    = request.POST.get("id_super", 3)
    #         page_number = request.POST.get("page", 1)
    #         orden       = request.POST.get("order", 'precio')
    #         salida_csv  = request.POST.get("salida_csv", False)
    # else:
    #     form = NameForm(request.GET)
    #     if form.is_valid():

    id_super    = request.GET.get("id_super", 3)
    page_number = request.GET.get("page", 1)
    orden       = request.GET.get("order", 'precio')
    salida_csv  = request.GET.get("salida_csv", False)
    registrar_consulta(request, 'Site', id_super)
        
    print(f'salida_csv={salida_csv}')
    supermercado    = get_object_or_404(Site.objects.all(), id=id_super)
    registrar_consulta(request, 'Site', id_super)

    urls            = SiteURLResults.objects.filter(site=supermercado)
    if salida_csv == 'on':
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="~/URLResults-{id_super}.csv"'

        response.write(codecs.BOM_UTF8)


        header = [
            "site",
            "url",
            "error404",
            "updated",
            "precio",
            "nombre",
            "idproducto",
            "marca",
            "image"
        ]

        writer = csv.DictWriter(response, fieldnames=header)
        writer.writeheader()

        for url in urls:
            writer.writerow(
                {
                    "site": url.site.pk,
                    "url": url.url,
                    "error404": url.error404,
                    "updated": url.updated,
                    "precio": url.precio,
                    "nombre": url.nombre,
                    "idproducto": url.idproducto,
                    "marca": url.marca,
                    "image": url.image
                }
            )
        return response
    
    else:
        urls            = urls.exclude(precio = 0)
        urls            = urls.order_by(orden)
        urls_count      = len(urls)
        context = {
            "supermercado": supermercado,
            "id_super": id_super,
            "orden": orden,
            "urls_count": urls_count
        }

        paginator = Paginator(urls, per_page=40)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            # if page is not an integer, deliver the first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # if the page is out of range, deliver the last page
            page_obj = paginator.page(paginator.num_pages)

        return render(request, 'precios/supermercado/siteUrlsinSite.html', {'context': context, 'articulos_dict': page_obj })


# def brands_rule(request):
#     if request.method == 'POST':
#         form = Unifica_Rule(request.POST)
#         # check whether it's valid:
#         if form.is_valid():
#             si_fuera = form.cleaned_data['si_fuera']
#             entonces = form.cleaned_data['entonces']

#             print(si_fuera, entonces)
#             si_fuera_art = Articulos.objects.filter(pk=si_fuera)
#             entonces_art = Articulos.objects.filter(pk=entonces)
#             print(si_fuera_art, entonces_art)



#     context = {}
#     return render(request, 'precios/marca/marcas_all.html', {'context': context })
    

# @never_cache
# @cache_page(60 * 10)   ## 10 minutos
# def brands_one(request, brand):
    
#     marcas = Marcas.objects.filter(nombre__startswith=brand)
    
#     context = {
#         "marcas": marcas,
#         'cache': '10 Min.',
        
#     }
#     return render(request, 'precios/marcas/marcas_one.html', {'context': context })

def sitePosition(request, siteid):
    ## Debe indicar 
    ## solo en jumbo= 3000 productos
    ## mas barato   =  500 productos
    ## 2do lugar    =  300 productos
    ## 3er lugar    = 1600 productos
    from precios.models import (Articulos, Vendedores)
    vendidosporjumbo = Vendedores.objects.all()
    vendidosporjumbo = vendidosporjumbo.order_by('articulo','vendidoen__precio')
    vendidosporjumbo = vendidosporjumbo.exclude(vendidoen__precio=0)
    vendidosporjumbo = vendidosporjumbo[:100]
    primero = True
    id_actual = vendidosporjumbo.first().articulo.id
    lista = {}
    for f in vendidosporjumbo:
        if primero or f.articulo.id != id_actual:
            primero = False
            id_actual = f.articulo.id
            posicion = 0
        
        posicion = posicion + 1
        lista.update({
            f.vendidoen.site.id: f.vendidoen.site.id,
            'posicion': posicion
        })

    print(lista)    
        # -- print(f.articulo.id ,f.articulo, f.vendidoen.site, f.vendidoen.precio)



    lista = {
        'superm': 3,
        'posiciones':{
            'lugar1': 100,

        }
    }

# @never_cache
# # @cache_page(60 * 60 * 12)   ## 12 horas
# def brands_all(request, unificado=None):
#     messages.warning(request,  str(getMessage()))

#     # marcas = Marcas.objects.exclude(nombre='').order_by('nombre')
#     marcas = Vendedores.objects.filter(articulo__marca__es_marca=True).exclude(articulo__nombre='').values_list('articulo__marca__nombre', flat=True).order_by('articulo__marca__nombre')
#     index_letras = {}
#     for marca in marcas:
#         # primera_letra = marca.nombre[0].lower()
#         primera_letra = marca[0].lower()
#         if primera_letra not in index_letras:
#             index_letras[primera_letra] = []


#     letras = []
#     for letra in index_letras:
#         # cantidad = Marcas.objects.filter( nombre__startswith=letra).count()
#         # marcas = Marcas.objects.filter(nombre__startswith=letra)
#         marcas = Vendedores.objects.filter(articulo__marca__es_marca=True).filter(articulo__marca__nombre__startswith=letra).values('articulo__marca__nombre', 'articulo__marca__slug')
#         marcas = marcas.distinct()
#         marcas = marcas.annotate(acount=Count('articulo__id'))

        
#         letras.append({
#             'letra': letra,
#             # 'cantidad': cantidad,
#             'marcas': marcas,
#         })

#     context = {
#         "letras": letras,
#         'cache': '0 Min.',
        
#     }
#     return render(request, 'precios/marca/marcas_all.html', {'marcas':marcas, 'context': context })    