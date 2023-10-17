from itertools import combinations
from django.contrib import messages
from django.db.models import Avg, Max, Min, Sum, Subquery, OuterRef, Count, Q
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import (
    cache_page, 
    never_cache, 
)
import pytz
utc=pytz.UTC

from precios.views_cart import getLastCart
import json
from django.http import HttpResponse

import re
from django.core import serializers
import urllib.parse
from django.db.models import Avg, Q



from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta


from precios.forms import (
    NameForm,

)
from precios.models import (
    Settings,
    Site, 
    Pages, 
    CamposEnSitio,
    SiteURLResults,
    DONDESEUSA,
    PAGECRAWLER,
    Marcas,
    Articulos,
    Vendedores,
    SiteMap,
    AreasDespacho,
    MomentosDespacho,
    TaggedArticles,
)
from taggit.models import Tag
from precios.pi_stats import (
    save_consulta_count,
    may_consulta,
)

from precios.pi_functions import (
    getMomentos,
    getMessage,
    registrar_consulta,
    generate_articulos_dict,
    generate_filters,
)

from precios.pi_get import (
    url_get, 
    getSiteProperties, 
    set_browser,
    set_beautifulBrowser,
    create_prods,
    get_dics
)   

# @cache_page(60 * 5)   ## 5 minutos


def export_as_json(modeladmin, request, queryset):
    response = HttpResponse(content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename={}.json'.format(modeladmin.model.__name__)
    serializers.serialize("json", queryset, stream=response)
    return response

def busca_marca(nombre):
    palabras = nombre.split()

    # Buscamos todas las combinaciones posibles de palabras
    combinaciones_palabras = []
    for i in range(1, len(palabras) + 1):
        combinaciones_palabras.extend(list(combinations(palabras, i)))

    # Buscamos si alguna combinación de palabras es una marca
    marca = None
    for combinacion in combinaciones_palabras:
        nombre_marca = " ".join(combinacion)
        if Marcas.objects.filter(nombre__icontains=nombre_marca, es_marca=True).exists():
            marcas = Marcas.objects.filter(nombre__icontains=nombre_marca)
            for mm_marca in marcas:
                if mm_marca.nombre in nombre:
                    marca = mm_marca
                    break

    return marca, palabras

@never_cache
def supermercado(request, pk):
    template = 'precios/supermercado/supermercado.html'

    superobj    = get_object_or_404(Site.objects.all(), id=pk)
    superobj2    = Site.objects.get(id=pk)
    pages       = Pages.objects.filter(site=superobj)
    sitemaps    = SiteMap.objects.filter(site=superobj)
    urls        = SiteURLResults.objects.filter(site=superobj)
    urlsCount   = urls.count()
    urls404     = SiteURLResults.objects.filter(site=superobj, error404=True).count()
    sin404      = urlsCount - urls404
    ReSeconds = SiteURLResults.objects.filter(site=superobj, error404=False).aggregate(average_time=Avg('secondsToGet'))
    urls_data = []
    urls_data.append({
        'urlsCount': urlsCount, 
        'urls404': urls404,
        'sin404': sin404,
        'ReSeconds': ReSeconds
    })

    meta = superobj2.as_meta()
    momentos = MomentosDespacho.objects.filter(areaDespacho__site=pk).all()
    context = {
        "supermercado": superobj,
        "momentos": momentos,
        "sitemaps": sitemaps,
        "pages": pages,
        "urls": urls_data,
        "meta": meta,
    }
    
    return render(request, template, {'context': context, 'meta': meta })

@never_cache
def index(request):
    
    return render(request, 'precios/index.html' )

# @cache_page(60 * 5)   ## 5 minutos
def antiguedad_registros(request):
    dias_viejo                          = int(Settings.objects.get(key='diasActualizado').value)
    sitios = Site.objects.filter(enable=True).order_by('crawler','siteName')
    # vdia4 = datetime.today() - timedelta(days=3)
    vdia1 = utc.localize(datetime.today()) - timedelta(days=0)
    vdia2 = utc.localize(datetime.today()) - timedelta(days=1)
    vdia3 = utc.localize(datetime.today()) - timedelta(days=2)
    vdia4 = utc.localize(datetime.today()) - timedelta(days=3)
    vdia5 = utc.localize(datetime.today()) - timedelta(days=4)
    vdia6 = utc.localize(datetime.today()) - timedelta(days=5)
    vdia7 = utc.localize(datetime.today()) - timedelta(days=6)
    vdia8 = utc.localize(datetime.today()) - timedelta(days=7)
    vdia9 = utc.localize(datetime.today()) - timedelta(days=8)
    vdia10 = utc.localize(datetime.today()) - timedelta(days=10)
    vdia15 = utc.localize(datetime.today()) - timedelta(days=15)
    
    suma_url    = 0
    
    tdia1       = 0
    tdia2       = 0 
    tdia3       = 0
    tdia4       = 0 
    tdia5       = 0
    tdia6       = 0
    tdia7       = 0  
    tdia8       = 0
    tdia9       = 0 
    tdia10      = 0 
    tdia15      = 0

    table   = []
    resumen = []
    for sitio in sitios:
        urls                 = SiteURLResults.objects.filter(site=sitio.id).exclude(error404=True).count()
        nombres              = SiteURLResults.objects.filter(site=sitio.id).exclude(error404=True).count()
    
        dia1                 = SiteURLResults.objects.filter(site=sitio.id, updated__range=(vdia2, vdia1)).exclude( error404=True).exclude(precio__exact=0).count()
        dia2                 = SiteURLResults.objects.filter(site=sitio.id, updated__range=(vdia3, vdia2)).exclude( error404=True).exclude(precio__exact=0).count()
        dia3                 = SiteURLResults.objects.filter(site=sitio.id, updated__range=(vdia4, vdia3)).exclude( error404=True).exclude(precio__exact=0).count()
        dia4                 = SiteURLResults.objects.filter(site=sitio.id, updated__range=(vdia5, vdia4)).exclude( error404=True).exclude(precio__exact=0).count()
        dia5                 = SiteURLResults.objects.filter(site=sitio.id, updated__range=(vdia6, vdia5)).exclude( error404=True).exclude(precio__exact=0).count()
        dia6                 = SiteURLResults.objects.filter(site=sitio.id, updated__range=(vdia7, vdia6)).exclude( error404=True).exclude(precio__exact=0).count()
        dia7                 = SiteURLResults.objects.filter(site=sitio.id, updated__range=(vdia8, vdia7)).exclude( error404=True).exclude(precio__exact=0).count()
        dia8                 = SiteURLResults.objects.filter(site=sitio.id, updated__range=(vdia9, vdia8)).exclude( error404=True).exclude(precio__exact=0).count()
        dia9                 = SiteURLResults.objects.filter(site=sitio.id, updated__range=(vdia10,vdia9)).exclude( error404=True).exclude(precio__exact=0).count()
        dia10                = SiteURLResults.objects.filter(site=sitio.id, updated__range=(vdia15,vdia10)).exclude( error404=True).exclude(precio__exact=0).count()
        dia15                = SiteURLResults.objects.filter(site=sitio.id, updated__lte=vdia15).exclude( error404=True).exclude(precio__exact=0).count()

        suma_url    += urls
        
        tdia1       += dia1
        tdia2       += dia2
        tdia3       += dia3
        tdia4       += dia4
        tdia5       += dia5
        tdia6       += dia6
        tdia7       += dia7
        tdia8       += dia8
        tdia9       += dia9
        tdia10      += dia10
        tdia15      += dia15
        table.append({
            'id': sitio.pk, 
            'corporacion': sitio.corporacion,
            'name': sitio.siteName,
            'crawler' : sitio.crawler,
            'URLS': urls, 
            'nombres':nombres,
            
            'dia1': dia1,
            'dia2': dia2,
            'dia3': dia3,
            'dia4': dia4,
            'dia5': dia5,
            'dia6': dia6,
            'dia7': dia7,
            'dia8': dia8,
            'dia9': dia9,
            'dia10': dia10,
            'dia15': dia15,
        })

    resumen.append({
        'suma_url':suma_url,
        
        'tdia1' : tdia1,
        'tdia2' : tdia2,
        'tdia3' : tdia3,
        'tdia4' : tdia4,
        'tdia5' : tdia5,
        'tdia6' : tdia6,
        'tdia7' : tdia7,
        'tdia8' : tdia8,
        'tdia9' : tdia9,
        'tdia10': tdia10,
        'tdia15': tdia15,
    })

    return render(request, 'precios/supermercado/super_inf_viejos.html', {'context': table, 'resumen':resumen, 'max_dias': dias_viejo })


# @cache_page(60 * 5)   ## 5 minutos
@never_cache
def estado(request):
    dias_viejo                          = int(Settings.objects.get(key='diasActualizado').value)
    horasregistrositio                  = int(Settings.objects.get(key='horasregistrositio').value)
    horasregistrocampolistado           = float(Settings.objects.get(key='horasregistrocampolistado').value)
    horasregistrocampoproducto          = float(Settings.objects.get(key='horasregistrocampoproducto').value)
    horasregistrocampoProdictolistado   = float(Settings.objects.get(key='horasregistrocampoProdictolistado').value)
    valorHoraConfigSitioPesos           = int(Settings.objects.get(key='valorHoraConfigSitioPesos').value)
    horasregistroAreaDespacho           = float(Settings.objects.get(key='horasregistroAreaDespacho').value)
    costoCoresMensualUsd                = float(Settings.objects.get(key='costoCoresMensualUsd').value)
    sitios = Site.objects.filter(enable=True).order_by('crawler','siteName')
    table = []
    resumen = []

    suma_url = 0
    suma_url404 = 0
    suma_nombres = 0
    suma_marca = 0
    suma_precio = 0
    suma_vendedores = 0
    suma_prercioNotUpdt = 0
    suma_sin404 = 0
    suma_solo_sitio = 0
    suma_campos_listado = 0
    suma_campos_producto = 0
    suma_campos_productolistado = 0
    suma_valor_recolecta = 0
    suma_valor_despacho = 0
    suma_valor_total = 0
    today = utc.localize(datetime.today()) - timedelta(days=dias_viejo)
    suma_articulos     = Articulos.objects.all().count()

    for sitio in sitios:
        urls        = SiteURLResults.objects.filter(site=sitio.id)
        urlsCount   = urls.count()
        urls404     = SiteURLResults.objects.filter(site=sitio.id, error404=True).count()
        sin404      = urlsCount - urls404
        
        
        areas           = AreasDespacho.objects.filter(site=sitio.id)
        comunas         = len(areas.values_list('comuna',flat=True))
        

        areasDespacho   = areas.count()
        momentos        = MomentosDespacho.objects.filter(areaDespacho__in=areas).count()

        siteMaps        = SiteMap.objects.filter(site=sitio.id).count()
        siteMapsGetUrl  = SiteMap.objects.filter(site=sitio.id,get_url=True).count()
        pages           = Pages.objects.filter(site=sitio.id).count()
        pagesEnabled    = Pages.objects.filter(site=sitio.id,enabled=True).count()
        pages404        = Pages.objects.filter(site=sitio.id,got_404=True).count()


        campos          = CamposEnSitio.objects.filter(site=sitio.id, enabled=True)
        camposlistado   = campos.filter(campo__donde=DONDESEUSA.EN_LISTADO).count()
        camposproducto  = campos.filter(campo__donde=DONDESEUSA.EN_PRODUCTO).count()
        camposd_listado = campos.filter(campo__donde=DONDESEUSA.DETALLE_EN_LISTADO).count()
        
        camposHa        = campos.filter(site=sitio.id, enabled=True).count()
        camposDe        = campos.filter(site=sitio.id, enabled=False).count()
        camposTot       = campos.filter(site=sitio.id).count()

        # alternativas = SelectorCampo.objects.filter(campo__in=campos).count()

        ReCampoNombre = SiteURLResults.objects.filter(site=sitio.id).exclude(error404=True).exclude(nombre__exact='').count()
        if ReCampoNombre == 0:
            ReCampoNombre = 1
        
        ReCampoMarca = SiteURLResults.objects.filter(site=sitio.id).exclude(error404=True).exclude(marca__exact='').count()
        ReCampoMarcaPrc = (ReCampoMarca / ReCampoNombre) * 100
        ReCampoImagen = SiteURLResults.objects.filter(site=sitio.id).exclude(error404=True).exclude(image__exact='').count()
        ReCampoImagenPrc = (ReCampoImagen / ReCampoNombre) * 100
        ReCampoPrecio = SiteURLResults.objects.filter(site=sitio.id).exclude( error404=True).exclude(precio__exact=0).count()
        ReCampoPrecioPrc = (ReCampoPrecio / ReCampoNombre) * 100
        ReCampoPrecioNotUpdt = SiteURLResults.objects.filter(site=sitio.id, updated__lte=today).exclude( error404=True).exclude(precio__exact=0).count()
        
        if (urlsCount - urls404) > 0:
            ReCampoNombrePercent = (ReCampoNombre / (urlsCount - urls404)) * 100
        else:
            ReCampoNombrePercent = 0
            
        ReSeconds = SiteURLResults.objects.filter(site=sitio, error404=False).aggregate(average_time=Avg('secondsToGet'))
        # .exclude(secondsToGet=0)
        

        vendedores = Vendedores.objects.filter(vendidoen__in=urls).count()
        vendedoresPercent = (vendedores / ReCampoNombre) * 100

        solo_sitio = (horasregistrositio * valorHoraConfigSitioPesos)
        valor_recolecta = (horasregistrocampolistado * camposlistado * valorHoraConfigSitioPesos) + \
                (horasregistrocampoproducto * camposproducto * valorHoraConfigSitioPesos) + \
                (horasregistrocampoProdictolistado * camposd_listado * valorHoraConfigSitioPesos)
        valor_despacho = (areasDespacho * horasregistroAreaDespacho * valorHoraConfigSitioPesos)
        total_puestaen_marcha = solo_sitio + valor_recolecta + valor_despacho

        suma_url += urlsCount
        suma_url404 += urls404
        suma_sin404 += sin404
        suma_nombres += ReCampoNombre
        suma_marca += ReCampoMarca
        suma_precio += ReCampoPrecio
        suma_vendedores += vendedores
        suma_prercioNotUpdt += ReCampoPrecioNotUpdt
        suma_solo_sitio += (horasregistrositio * valorHoraConfigSitioPesos)
        suma_campos_listado += (horasregistrocampolistado * camposlistado * valorHoraConfigSitioPesos)
        suma_campos_producto += (horasregistrocampoproducto * camposproducto * valorHoraConfigSitioPesos)
        suma_campos_productolistado += (horasregistrocampoProdictolistado * camposd_listado * valorHoraConfigSitioPesos)
        suma_valor_recolecta += valor_recolecta
        suma_valor_despacho += valor_despacho
        suma_valor_total += total_puestaen_marcha
        table.append({
            'id': sitio.pk, 
            'corporacion': sitio.corporacion,
            'name': sitio.siteName,
            'crawler' : sitio.crawler,
            'URLS': urlsCount, 
            'urls404': urls404,
            'sin404': sin404,
            'areasDespacho': areasDespacho,
            'comunas': comunas,
            'momentos': momentos,
            'ReCampoPrecioNotUpdt': ReCampoPrecioNotUpdt,
            'siteMaps': siteMaps,
            'siteMapsGetUrl': siteMapsGetUrl,
            'pages': pages,
            'pagesEnabled': pagesEnabled,
            'pages404': pages404,
            'camposlistado': camposlistado,
            'camposproducto': camposproducto,
            'camposd_listado': camposd_listado,
            'valor_recolecta': valor_recolecta,
            'valor_despacho': valor_despacho,
            'total_puestaen_marcha': total_puestaen_marcha,
            'camposha': camposHa, 
            'camposde': camposDe, 
            'campostot': camposTot, 
            'ReCampoNombre': ReCampoNombre,
            'ReSeconds': ReSeconds,
            'ReCampoPrecio': ReCampoPrecio,
            'ReCampoPrecioPrc': ReCampoPrecioPrc,
            'ReCampoMarca':ReCampoMarca,
            'ReCampoMarcaPrc': ReCampoMarcaPrc,
            'ReCampoImagen': ReCampoImagen,
            'ReCampoImagenPrc': ReCampoImagenPrc,
            'ReCampoNombrePercent': ReCampoNombrePercent,
            'vendedores':vendedores,
            'vendedoresPercent':vendedoresPercent,
            'suma_url':suma_url
            })


    sumaNombrePercent = (suma_nombres / suma_url) * 100
    suma_vendedoresPercent = (suma_vendedores / suma_nombres) * 100
    resumen.append({'suma_url':suma_url,
        'suma_url404': suma_url404,
        'suma_sin404': suma_sin404,
        'suma_nombres': suma_nombres,
        'sumaNombrePercent': sumaNombrePercent,
        'suma_marca': suma_marca,
        'suma_precio': suma_precio,
        'suma_prercioNotUpdt': suma_prercioNotUpdt,
        'suma_vendedores': suma_vendedores,
        'suma_vendedoresPercent': suma_vendedoresPercent,
        'suma_solo_sitio': suma_solo_sitio,
        'suma_campos_listado':suma_campos_listado,
        'suma_campos_producto': suma_campos_producto,
        'suma_campos_productolistado': suma_campos_productolistado,
        'suma_valor_recolecta': suma_valor_recolecta,
        'suma_valor_despacho': suma_valor_despacho,
        'suma_valor_total': suma_valor_total,
        'dias_viejo': dias_viejo,
        'valorHoraConfigSitioPesos':valorHoraConfigSitioPesos,
        'horasregistrositio': horasregistrositio,
        'horasregistrocampolistado': horasregistrocampolistado,
        'horasregistrocampoproducto': horasregistrocampoproducto,
        'horasregistrocampoProdictolistado': horasregistrocampoProdictolistado,
        'horasregistroAreaDespacho': horasregistroAreaDespacho,
        'costoCoresMensualUsd': costoCoresMensualUsd,
        'suma_articulos': suma_articulos
    })
    return render(request, 'precios/supermercado/estado.html', {'context': table, 'resumen':resumen })
    

def mobile(request):


    """Return True if the request comes from a mobile device."""

    MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False

debug = False
def get_time_took(evento, startTime, endTime):
    dif = endTime - startTime
    
    startTime = endTime

    if debug:
        print(f'{evento} toma {dif}')
    return startTime


# @never_cache
def getArticulos(momentos, articulos, MinSuperCompara):
    startTime = datetime.now()
    startTime = get_time_took('articulos.distinct etc  ', startTime, datetime.now())

    articulos_dict  = []
    articulos_count = 0
    ofertas_count   = 0
    for particulo in articulos:
        # print(particulo.mejorprecio)
        etalle = Vendedores.objects.select_related('vendidoen').values(
            'vendidoen__precio',
            'vendidoen__url',
            'vendidoen__updated',
            'vendidoen__site__siteName',
            'vendidoen__stock',
            'vendidoen__tipo',
            'vendidoen__categoria',
            'vendidoen__idproducto',
        ).all()
        etalle = etalle.filter(articulo=particulo.id)
        
        if momentos:
            etalle = etalle.filter(vendidoen__site__in=momentos)

        etalle = etalle.exclude(vendidoen__precio__exact=0)
        etalle = etalle.order_by('vendidoen__precio')
        etalle = etalle.distinct()
        etalle = etalle.all()
        
        if (len(etalle)) >= MinSuperCompara :
            articulos_count +=1
            ofertas = etalle.count()
            ofertas_count += ofertas
            
            articulos_dict.append({'articulo': particulo, 'mejorprecio': particulo.mejorprecio, 'detalle': etalle})

    startTime = get_time_took('FIN particulo  ', startTime, datetime.now())
    

    return ofertas_count, articulos_count, articulos_dict

# @never_cache
def rescan(request, slug):
    articulos_creados = 0
    articulos_existentes = 0
    articulos_nombre_vacio = 0
    articulos_marca_vacio = 0
    debug = False
    
    articulos = Vendedores.objects.select_related('articulo', 'vendidoen').all()
    query= Q(articulo__slug=slug)
    articulos = articulos.filter(query)
    urlCount = 0
    for art in articulos:
        print(f'articulo={art}, art.vendidoen.site={art.vendidoen.site}, art.vendidoen.url={art.vendidoen.url}')
        urlCount = urlCount + 1
        
        siteclicks, \
                arr_campo404, \
                listaDeCampos, \
                campoEnSitioObject, \
                arr_linksSelector, \
                ItemsEnListado,\
                arr_nextPage, \
                arr_maxPages = getSiteProperties(art.vendidoen.site)

        url = urllib.parse.unquote(art.vendidoen.url)
        laurl1 = SiteURLResults.objects.get(id=art.vendidoen.id)

        
        if art.vendidoen.site.crawler != PAGECRAWLER.SELENIUM:            
            
            browser = set_beautifulBrowser(url, laurl1)
            if not browser:
                print("Error browser")
                continue
        else:
            browser = set_browser()

        #### URL Get
        url_get(
            browser, 
            url, 
            laurl1, 
            arr_campo404, 
            siteclicks, 
            campoEnSitioObject, 
            art.vendidoen.site, 
            urlCount, 
            len(articulos), 
            0,
           
        )

        ### Create prods
        laurl2 = SiteURLResults.objects.filter(id=art.vendidoen.id, error404=False)
        
        PALABRAS_INUTILES, \
            SUJIFOS_NOMBRE, \
            ean_13_site_ids, \
            UMEDIDAS, \
            UNIDADES, \
            PACKS, \
            TALLAS, \
            COLORES, \
            ENVASES, \
            marcas, \
            listamarcas,\
            marcasistema,\
            sin_marca, \
            listamarcas, \
            campoMarcaObj = get_dics()

        registros = 0
        create_prods(
            laurl2, 
            registros, 
            articulos_nombre_vacio, 
            debug, 
            campoMarcaObj,
            listamarcas,
            sin_marca,
            COLORES,
            PALABRAS_INUTILES,
            ENVASES,
            SUJIFOS_NOMBRE,
            TALLAS,
            UMEDIDAS,
            PACKS, 
            UNIDADES,
            ean_13_site_ids,
            art.vendidoen.site,
            articulos_existentes,
            articulos_creados,
             2,
            False
        )
        # art.delete()

    # return detalle(request, slug)





def categorias_anidadas(request):
    etiquetas_jerarquicas  = Tag.objects.all()
    
    return render(request, 'precios/categorias.html', {'etiquetas_jerarquicas': etiquetas_jerarquicas})

    
# @never_cache
def precios(request):
    MinSuperCompara             = int(Settings.objects.get(key='MinSuperCompara').value)
    PaginatorItemsPerPage       = int(Settings.objects.get(key='PaginatorItemsPerPage').value)
    ExternalUrlPostUrl          = Settings.objects.get(key='ExternalUrlPostUrl').value
    messages.warning(request,  str(getMessage()))
    
    context = {}
    
    islogged =  request.user.is_authenticated
    if not islogged:
        comuna = None
        puede_connsultar = True
    else:
        comuna = request.user.member.comuna
        save_consulta_count(request)
        puede_connsultar = may_consulta(request)

    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            nombre          = form.cleaned_data['nombre']
            rmarca          = request.POST.getlist('marca')
            rgrados         = request.POST.getlist('grados')
            renvase         = request.POST.getlist('envase')
            rcolor          = request.POST.getlist('color')
            rmedida_cant    = request.POST.getlist('medida_cant')
            rtalla          = request.POST.getlist('talla')
            runidades       = request.POST.getlist('unidades')
            rsupermercados  = request.POST.getlist('supermercados')
            orden           = request.POST.get('order', 'precio_por_unidad')
            page_number     = request.POST.get('page_number',1)
            rtags           = request.POST.get('tags')
        # page_number = 1
    else:
        page_number = request.GET.get("page", 1)
        form = NameForm(request.GET)
        if form.is_valid():
            nombre          = form.cleaned_data['nombre']
            rmedida_cant    = request.GET.getlist('medida_cant')
            rmarca          = request.GET.getlist('marca')
            rgrados         = request.GET.getlist('grados')
            renvase         = request.GET.getlist('envase')
            rcolor          = request.GET.getlist('color')
            rtalla          = request.GET.getlist('talla')
            runidades       = request.GET.getlist('unidades')
            rsupermercados  = request.GET.getlist('supermercados')
            orden           = request.GET.get("order", 'precio_por_unidad')
            rtags           = request.GET.get('tags')
        else:
            orden           =  'precio_por_unidad'
            nombre          = ''
            rtags           = None

    if type(orden) == 'list':
        if len(orden) == 0:
            orden   = 'precio_por_unidad'

    nombre = nombre.rstrip().lower()

    registrar_consulta(request, clase_consultada="cslta_", elemento_id=1, texto_busqueda=nombre)
    
    params = request.GET.copy()
    if 'page' in params:
        del params['page']
        
    context['clean_params'] = params.urlencode()
    print(f'params.urlencode()={params.urlencode()}')
   
    
    if  puede_connsultar and (rtags or rmarca or nombre !=''):
        momentos, supermercadoscount = getMomentos(request)
        articulos = Articulos.objects.select_related('marca').all()
        
        if nombre !='':
            if Articulos.objects.filter(ean_13__exact=nombre).exists():
                articulos = Articulos.objects.filter(ean_13__exact=nombre)
            else:
                
                marca, palabras = busca_marca(nombre)  
                # else:
                #     palabras = ''

                # Si encontramos una marca, la utilizamos para filtrar los artículos
                if marca:
                    articulos = Articulos.objects.filter(marca=marca)
                    palabras_buscar = []
                    for palabra in palabras:
                        if palabra not in marca.nombre.lower():
                            palabras_buscar.append(palabra)

                # Si no encontramos una marca, buscamos en todos los artículos
                else:
                    articulos = Articulos.objects.all()
                    palabras_buscar = nombre.split()
                    
                # Buscamos en campo nombre del artículo utilizando las palabras restantes
                cuenta = 0 
                for palabra in palabras_buscar:
                    cuenta = cuenta + 1
                    if cuenta == 1:
                        articulos = articulos.filter(Q(nombre__istartswith=palabra))
                    else:
                        articulos = articulos.filter(Q(nombre__icontains=palabra))
                articulos = articulos.distinct()

        # MinSuperCompara
        ofertas_count  = 0
        

        if rtags:
            articulos = articulos.filter(tags__slug=rtags)
            # print(rtags, articulos, articulos.query)

        if rmarca:
            articulos = articulos.filter(marca__in=rmarca)

        if rgrados:
            articulos = articulos.filter(grados2__in=rgrados)

        if renvase:
            articulos = articulos.filter(envase__in=renvase)

        if rcolor:
            articulos = articulos.filter(color__in=rcolor)

        if rmedida_cant:
            articulos = articulos.filter(medida_cant__in=rmedida_cant)

        if rtalla:
            articulos = articulos.filter(talla__in=rtalla)

        if runidades:
            articulos = articulos.filter(unidades__in=runidades)

        # print('rsupermercados=',rsupermercados)
        if not rsupermercados:
            articulos = articulos.annotate(num_vendedores=Count('vendedores__vendidoen', filter=Q(vendedores__vendidoen__site__in=momentos, vendedores__vendidoen__precio__gt=0), distinct=True))
        else:
            articulos = articulos.annotate(num_vendedores=Count('vendedores__vendidoen', filter=Q(vendedores__vendidoen__site__in=rsupermercados, vendedores__vendidoen__precio__gt=0), distinct=True))


        articulos_dict, articulos_count, ofertas_count = generate_articulos_dict(articulos, momentos, MinSuperCompara, orden)
        filtro = generate_filters(articulos)
        
        
        context['resumen'] = {
            'articulos_count':articulos_count, 
            'ofertas_count': ofertas_count, 
            'supermercadoscount': supermercadoscount, 
            'nombre': nombre, 
            'orden': orden,
            'logged': islogged, 
            'comuna': comuna , 
            'mensaje': 'No hay resultados.',
            'ExternalUrlPostUrl': ExternalUrlPostUrl
        }
        paginator = Paginator(articulos_dict, per_page=PaginatorItemsPerPage)
        
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = None

    else:
        islogged =  request.user.is_authenticated
        mensaje = ""
        if not islogged:
            comuna = None
        else:
            comuna = request.user.member.comuna

            ### vemos si tiene listas
            lista = getLastCart(request)

            if not  may_consulta(request):
                mensaje = "Maximo de consultas por mes excedido."

        momentos, supermercadoscount = getMomentos(request)
        page_obj = []
        context = {}
        filtro = {}
        context['mobile'] = True
        context['resumen'] = { 
            'supermercadoscount': supermercadoscount,  
            'nombre': nombre, 
            'orden': orden,
            'logged': islogged, 
            'comuna': comuna , 
            'mensaje': mensaje,
            'ExternalUrlPostUrl': ExternalUrlPostUrl
        }
        articulos_dict  = {}
        articulos = {}
        form = NameForm()

        
    return render(request, 'precios/precios-3.html', {'form': form, 'filtro': filtro, 'context': context, 'articulos': articulos,  'articulos_dict': page_obj})



def getObjectOrNone(site, campo):
    try:
        return CamposEnSitio.objects.filter(site=site,campo=campo).get()
    except:
        return None


