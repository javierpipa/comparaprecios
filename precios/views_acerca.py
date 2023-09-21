from django.shortcuts import get_object_or_404, redirect, render
from precios.models import (
    Site, 
    SiteURLResults,
    Vendedores,
    DiasSemana,
    MomentosDespacho,
    AreasDespacho,
    Countries,
    Regions,
    Cities
)
from members.models import (
    Member, 
    Lista, 
    Plan,
    ContenidoPlan,
    TIPO_PLAN,
    # Account

)
from precios.pi_functions import get_sessions
from django.views.decorators.cache import (
    cache_page, 
    never_cache, 
)

# @cache_page(60 * 5)   ## 5 minutos
@never_cache
def cobertura(request):
    islogged =  request.user.is_authenticated
    country_id, region_id, comuna_id = get_sessions(request)
    comunas = Cities.objects.all()
    if country_id:
        comunas = comunas.filter(country_id=country_id)
    if region_id:
        comunas = comunas.filter(region_id=region_id)
    if comuna_id:
        comunas = comunas.filter(id=comuna_id)
        
    data = [
        {
            "nombre": comuna.name,
            "latitud": comuna.latitude,
            "longitud": comuna.longitude,
            "cantidad_supermercados": comuna.supermercado_count,
            "nombres_supermercados": "<br>".join(comuna.supermercados),
            "color": "green" if comuna.supermercado_count > 0 else "red"
        }
        for comuna in comunas
    ]
    if comunas:
        min_lat = min(comuna.latitude for comuna in comunas)
        max_lat = max(comuna.latitude for comuna in comunas)
        min_lng = min(comuna.longitude for comuna in comunas)
        max_lng = max(comuna.longitude for comuna in comunas)
    else:
        min_lat, max_lat, min_lng, max_lng = -56, -17, -75, -66  # Coordenadas por defecto para Chile

    
    paises = Countries.objects.all()
    if country_id:
        paises = paises.filter(id=country_id)

    datos = []
    num_regiones =  0
    for pais in paises:
        regiones = Regions.objects.filter(country=pais)
        if region_id:
            regiones = regiones.filter(id=region_id)

        datos_regiones =  []
        for region in regiones:
            num_regiones = num_regiones + 1
            ciudades = Cities.objects.filter(country=pais,  region=region )
            if comuna_id:
                ciudades = ciudades.filter(id=comuna_id)

            datos_ciudades = []
            for ciudad in ciudades:
                
                areas =  AreasDespacho.objects.filter(comuna=ciudad, site__enable=True)
                datos_area = []
                num_areas = 0
                for area in areas:
                    num_areas = num_areas + 1
                    momentos = MomentosDespacho.objects.filter(areaDespacho=area)
                    

                    dat_area = {'site': area.site, 'area': area.area, 'monto_minimo_compra': area.monto_minimo_compra, 'valor_despacho': area.valor_despacho, 'momentos': momentos}
                    datos_area.append(dat_area)

                dat_ciudad  =  {'id': ciudad.pk,  'nombre': ciudad.name, 'cut':  ciudad.cut, 'superficie': ciudad.superficie, 'poblacion': ciudad.poblacion, 'num_areas': num_areas, 'areas': datos_area}
                datos_ciudades.append(dat_ciudad)


            dat_region = {'id': region.pk, 'nombre': region.name, 'code': region.code, 'ciudades': datos_ciudades}
            datos_regiones.append(dat_region)

        dat_pais  =  {'id': pais.pk, 'nombre': pais.name, 'regiones': datos_regiones, 'num_regiones': num_regiones}
        datos.append(dat_pais)


    context = {}
    context['bounds'] = {
        'min_lat': min_lat,
        'max_lat': max_lat,
        'min_lng': min_lng,
        'max_lng': max_lng,
    }
    context['datos'] = datos
    context['resumen'] = {  'logged': islogged }
    return render(request, 'acerca/cobertura.html', { 'context': context, 'data': data })


@never_cache
def acerca(request):
    islogged =  request.user.is_authenticated
    if not islogged:
        comuna = None
    else:
        comuna = request.user.member.comuna

    context = {}
    context['resumen'] = {  'logged': islogged, 'comuna': comuna }

    return render(request, 'acerca/sobre_devop.html', { 'context': context })


# @cache_page(60 * 5)   ## 5 minutos
@never_cache
def planes_buscan(request):
    planes          = Plan.objects.filter(publico=True, tipo=TIPO_PLAN.PERSONAS).order_by('my_order')
    arr_planes      = []
    for plan in planes:
        contenidoPlan   = ContenidoPlan.objects.filter(plan=plan).order_by('my_order')
        contenido     = {
            'plan': plan,
            'incorpora' : contenidoPlan
        }
        arr_planes.append(contenido)
    return render(request, 'acerca/planes_buscan.html', { 'context': 'context','planes':arr_planes })

# @cache_page(60 * 5)   ## 5 minutos
@never_cache
def planes_ofrecen(request):
    planes          = Plan.objects.filter(publico=True, tipo=TIPO_PLAN.OFRECEN).order_by('my_order')
    arr_planes      = []
    for plan in planes:
        contenidoPlan   = ContenidoPlan.objects.filter(plan=plan).order_by('my_order')
        contenido     = {
            'plan': plan,
            'incorpora' : contenidoPlan
        }
        arr_planes.append(contenido)
    return render(request, 'acerca/planes_ofrecen.html', { 'context': 'context','planes':arr_planes })
    

# ?utm_medium=referral&utm_source=soicos