from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.cache import (
    cache_page, 
    never_cache, 
)
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import CharField, Value
from django.contrib import messages
from django.db.models.functions import Concat
from django.db.models import Avg, Max, Min, Sum, Subquery, OuterRef, Count, Q

import csv
import codecs
from django.http import HttpResponse
from django.views.generic import TemplateView
import pandas as pd
import json

from precios.views import getMomentos
from django.http import JsonResponse
from django.core import management

from .models import (
    Site, 
    SiteURLResults,
    Vendedores,
    Articulos,
    Marcas,
    Settings,
    Unifica,
    Cities,
    SiteMap,
    DiasSemana,
    HorasDespacho,
    PAGECRAWLER,
    THEPARSER,
    PAGECRAWLER,
    )
from members.models import (
    Plan, 
    TIPO_PLAN,
    ContenidoPlan,
    OBJETOS_EN_PLAN,
    Contrato,
    
)
from precios.pi_supermercado import (
    get_url_robots,
    get_content_from_column,
    get_sitemap_from_url,
    get_data_robots,
    get_url_content,
    find_product_details_in_ld_json_beautiful,
    find_product_details_in_ld_json_selenium,
    my_craw
)
from precios.forms import CotizaForm
from precios.tasks import getBeautiful
from precios.pi_functions import urlSave


# AJAX
def ajax_craw(request):
    siteURL         = request.GET.get('siteURL')
    pagecount       = 255
    craw            = my_craw(siteURL, pagecount)
    craw_content    = []
    registros       = 0
    for cuenta, row in craw.iterrows():
        registros = registros  + 1

        # if registros < 20:
        craw_content.append({
                'loc': row['url'], 
            })
    
    print(f'craw_content={craw_content}')

    context = {
        'craw_content'  : craw_content,
        'registros'     : registros,
    }
    
    return JsonResponse(context, status=200, safe=False)

def ajax_url_ld_json(UrltoGet):

    is_ld_json      = False
    ld_json         = ''
    crawler         = PAGECRAWLER.NINGUNO
    for theurl in UrltoGet:
        if theurl !='':
            ld_json     = find_product_details_in_ld_json_beautiful(theurl) 
            if ld_json:
                is_ld_json  = True
                crawler = PAGECRAWLER.BEAUTIFULSOUP
                break
            else:
                ld_json = find_product_details_in_ld_json_selenium(theurl)
                if ld_json:
                    crawler = PAGECRAWLER.SELENIUM
                    is_ld_json  = True
                    break

    return is_ld_json, ld_json, crawler



    
def ajax_sitemap(SiteMapList):
    SiteMapArr  = SiteMapList.split(',')
    registros   = 0
    heading     = []

    for thesite in SiteMapArr:
        if thesite != '':
            sitemap_content = get_sitemap_from_url(thesite, True)
            
            for cuenta, row in sitemap_content.iterrows():
                registros = registros  + 1
                try:
                    heading.append({
                            'loc': row['loc'], 
                            'sitemap': row['sitemap'],
                            'sitemap_size_mb': row['sitemap_size_mb'],
                            'download_date': row['download_date'],
                        })
                except Exception as e:
                    print(f"Error en ajax_sitemap con  {thesite} {e}")

    return heading, registros
    

@never_cache
@require_GET
def ajax_plan(request):
    plan_id = request.GET.get('plan_id')

    plan_exist = False
    contenidoplan       = []
    # contenido_dias      = []
    # contenido_horario   = []
    contenido_comuna    = []

    # dia     = DiasSemana.objects.order_by('my_order').all()
    # horario = HorasDespacho.objects.all()
    comuna  = Cities.objects.all()

    if ContenidoPlan.objects.filter(plan=plan_id).exists():
        plan_exist = True
        contenidoplan_list = ContenidoPlan.objects.filter(plan=plan_id)
        for con in contenidoplan_list:
            contenidoplan.append({
                'id': con.pk,
                'objeto': con.objeto,
                'cantidad': con.cantidad,
                'todos': con.todos,
            })
        # for con in dia:
        #     contenido_dias.append({
        #         'id'        : con.pk,
        #         'nombre'    : con.nombre,
        #         }
        #     )
        # for con in horario:
        #     contenido_horario.append({
        #         'id'        : con.pk,
        #         'nombre'    : str(con.inicio) + ' - ' + str(con.termino)
        #         }
        #     )
        for con in comuna:
            contenido_comuna.append({
                'id'        : con.pk,
                'nombre'    : con.region.name + ': ' + con.name
                }
            )
    context =  {
        'plan_exist'    : plan_exist,
        'contenidoplan' : contenidoplan,
        # 'dia'           : contenido_dias,
        # 'horario'       : contenido_horario,
        'comuna'        : contenido_comuna,
    }
    return JsonResponse(context, status=200, safe=False)


@never_cache
@require_GET
def ajax_robots(request):
    siteURL = request.GET.get('siteURL')
    
    column          = 'directive'
    text_to_search  = 'Sitemap'
    sitemap_url     = ''
    sitemap_url_exist = False
    
    heading         = []
    sitemap_data    = []
    registros       = 0
    site            = None

    robots_data     = []
    robots_url      = ''
    site_exist      = False
    agentes         = []
    arr_url_ld_json = []
    max_ld_json     = 2

    
    if Site.objects.filter(siteURL=siteURL).exists():
        site_exist = True
        site = Site.objects.filter(siteURL=siteURL).get()
    

    robots_url = get_url_robots(siteURL)
    
    url_robots, existe_robots = get_data_robots(robots_url)

    if existe_robots:
        if not url_robots.empty:
            sitemap = get_content_from_column(url_robots, column, text_to_search)
            if sitemap.empty:
                sitemap_url = siteURL + 'sitemap.xml'
            elif not sitemap.empty:
                # sitemap_url_exist = True
                sitemap = url_robots.loc[url_robots[column] == text_to_search].values[0]
                sitemap_url = sitemap[1]
            sitemap_content = get_sitemap_from_url(sitemap_url, False)
            if not sitemap_content.empty:
                url_ld_json = 0
                for i, row in sitemap_content.iterrows():
                    this_sitemap_exist = False
                    if site:
                        if SiteMap.objects.filter(site=site, loc=row['loc']).exists():
                            this_sitemap_exist = True

                    url = str(row['loc'])
                    if '.xml' in url:
                        sitemap_url_exist = True
                        sitemap_data.append({
                            'loc': row['loc'], 
                            'sitemap': row['sitemap'],
                            'exist': this_sitemap_exist,
                        })

                        ## Get siteMap Content
                        heading_q, registros_q = ajax_sitemap(row['loc'])

                        registros = registros + registros_q
                        url_ld_json = 0
                        for rec in heading_q:
                            url_ld_json = url_ld_json + 1
                            if url_ld_json < max_ld_json:
                                arr_url_ld_json.append(rec['loc'])

                            heading.append({
                                'loc': rec['loc'], 
                                'sitemap': rec['sitemap'],
                            })    
                    else:
                        url_ld_json = url_ld_json + 1
                        if url_ld_json < max_ld_json:
                            arr_url_ld_json.append(row['loc'])
                        
                        registros = registros  + 1
                        sitemap_url_exist = True
                        heading.append({
                            'loc': row['loc'], 
                            'sitemap': row['sitemap'],
                        })
        try:
            agentes = (url_robots
                [url_robots['directive']=='User-agent']
                ['content'].drop_duplicates()
                .tolist())
        except Exception as e:
            print(f"Error agentes  {e}")
            agentes = None


        print(arr_url_ld_json)

        is_ld_json, ld_json, crawler = ajax_url_ld_json(arr_url_ld_json)

        try:
            for i, row in url_robots.iterrows():
                robots_data.append({
                    'directive': row['directive'], 
                    'content': row['content'],
                    'robotstxt_url': row['robotstxt_url'],
                    'download_date': row['download_date'],
                })
        except Exception as e:
            for i, row in url_robots.iterrows():
                robots_data.append({
                    'errors': row['errors'],
                    'robotstxt_url': row['robotstxt_url'],
                    'download_date': row['download_date'],
                })
            print(f"Error robots_data  {e}")
            agentes = None

    context = {
        'site_exist'        : site_exist,
        'existe_robots'     : existe_robots,
        'robots_data'       : robots_data,
        'robots_url'        : robots_url,
        'agentes'           : agentes,
        'sitemap_url'       : sitemap_url,
        'sitemap_url_exist' : sitemap_url_exist,
        'sitemap_data'      : sitemap_data,
        'heading'           : heading,
        'registros'         : registros,
        'is_ld_json'        : is_ld_json,
        'ld_json'           : ld_json,
        'crawler'           : crawler,
    }

    return JsonResponse(context, status=200, safe=False)



def cotiza(request):
    template_name = 'precios/supermercado/cotiza-2.html'
    islogged =  request.user.is_authenticated

    planes = Plan.objects.filter(tipo=TIPO_PLAN.OFRECEN, publico=True).order_by('my_order')
    objetos = OBJETOS_EN_PLAN
    if request.method == "POST":
        print('POST')
        # , instance=request.user.member
        cotiza_form = CotizaForm(request.POST)
        if  cotiza_form.is_valid():
            print('POST 2')
            for key, value in request.POST.items():
                print(f'Campo: {key}, Valor: {value}')
            pass
        else:
            print('error ')
            print(cotiza_form.errors)

    else:
        print('OTHER')
        cotiza_form = CotizaForm(request.GET)

    context = {
        'planes': planes,
        'objetos': objetos,
    }
    context['resumen'] = {  'logged': islogged,}
    return render(request, template_name, {'form':cotiza_form,'context': context })

@never_cache
# @require_POST 
def ajax_save_cotiza(request):
    siteURL     = request.GET["siteURL"]
    plan_id     = request.GET["plan_id"]
    sitemap_url = request.GET["sitemap_url"]
    print(f'siteURL={siteURL}, plan_id={plan_id} request.user.member={request.user.member.id}')

    plan = Plan.objects.get(id=plan_id)

    save_site(siteURL, sitemap_url, plan, request.user.member)

    data = {'hola':'hola'}
    return JsonResponse(data, status=200, safe=False)
    

def save_site(siteURL, sitemap_url, plan, member):
    site = Site.objects.create(
        siteURL             = siteURL,
        siteName            = siteURL,
        agregaSiteURL       = False,
        allLinksInOnePage   = False,
        siteSearchEnabled   = False,
        siteSearch          = 'sitemap',
        productSearchEnabled= False,
        listHasClick        = False,
        listNeedsPgDn       = False,
        theparser           = THEPARSER.HTML_PARSER,
        crawler             = PAGECRAWLER.BEAUTIFULSOUP,
        url_suffix          = None,
        page_parameter      = None,
        page_suffix         = None,
        sitemap_url         = sitemap_url, 
        enable              = True,
        # icon_image          = "",
        cobertura_url       = None,
        es_ean13            = False,
        reclamos_url        = None,
        product_url         = siteURL,
    )
    site.save()
    
    contrato = Contrato.objects.create(
        site        =   site,
        plan        =   plan,
        member      =   member
    )
    contrato.save()


    sitemap_content = get_sitemap_from_url(sitemap_url, False)
    if not sitemap_content.empty:
        url_ld_json = 0
        for i, row in sitemap_content.iterrows():
            this_sitemap_exist = False
            if site:
                if SiteMap.objects.filter(site=site, loc=row['loc']).exists():
                    this_sitemap_exist = True

            url = str(row['loc'])
            if '.xml' in url:
                if not this_sitemap_exist:
                    sitemap = SiteMap.objects.create(
                        site            = site,
                        loc             = row['loc'], 
                        get_url         = True,
                        sitemap_type    = 'xml_sitemap_index',
                    )
                    sitemap.save()
            else:
                urlObj, created = urlSave(site, row['loc'])
                
                
    management.call_command('getURLFromSiteMap', site.id)
    
    getBeautiful(site.id)
    
    return site.id
# def ajax_sitemap_2(request):
#     SiteMapList = request.GET.get('SiteMapList')
#     SiteMapArr  = SiteMapList.split(',')
#     registros   = 0
#     heading     = []

#     for thesite in SiteMapArr:
#         if thesite != '':
#             sitemap_content = get_sitemap_from_url(thesite, True)
            
#             for cuenta, row in sitemap_content.iterrows():
#                 registros = registros  + 1
#                 heading.append({
#                         'loc': row['loc'], 
#                         'sitemap': row['sitemap'],
#                         'sitemap_size_mb': row['sitemap_size_mb'],
#                         'download_date': row['download_date'],
#                     })

#     responde = (f'{registros} Registros.')

#     context = {
#         'registros': responde,
#         'heading': heading,
#     }

#     # return render(request, 'precios/supermercado/includes/url_sitemap.html', {'context': context })
#     return JsonResponse(context, status=200, safe=False)

# def ajax_sitemap_url(request):
#     siteURL     = request.GET.get('siteURL')
    
#     # column = 'directive'
#     # text_to_search = 'Sitemap'

#     # sitemap_data = []
#     # sitemap_url = ''
#     sitemap_url_exist   =   False
#     # site            = None

#     # heading     = []
#     # registros   = 0
#     robots_url = get_url_robots(siteURL)

#     if Site.objects.filter(siteURL=siteURL).exists():
#         site_exist = True
#         site = Site.objects.filter(siteURL=siteURL).get()

    
#     url_robots, existe_robots = get_data_robots(robots_url)

#     # if existe_robots:
#         # if not url_robots.empty:
#         #     sitemap = get_content_from_column(url_robots, column, text_to_search)
#         #     if sitemap.empty:
#         #         sitemap_url = siteURL + 'sitemap.xml'
#         #     elif not sitemap.empty:
#         #         # sitemap_url_exist = True
#         #         sitemap = url_robots.loc[url_robots[column] == text_to_search].values[0]
#         #         sitemap_url = sitemap[1]

#             # sitemap_content = get_sitemap_from_url(sitemap_url, False)
#             # if not sitemap_content.empty:
#             #     for i, row in sitemap_content.iterrows():
#             #         this_sitemap_exist = False
#             #         if site:
#             #             if SiteMap.objects.filter(site=site, loc=row['loc']).exists():
#             #                 this_sitemap_exist = True

#             #         url = str(row['loc'])
#             #         if '.xml' in url:
#             #             sitemap_url_exist = True
#             #             sitemap_data.append({
#             #                 'loc': row['loc'], 
#             #                 'sitemap': row['sitemap'],
#             #                 'sitemap_size_mb': row['sitemap_size_mb'],
#             #                 'download_date': row['download_date'],
#             #                 'exist': this_sitemap_exist,
#             #             })
#             #         else:
#             #             registros = registros  + 1
#             #             sitemap_url_exist = False
#             #             heading.append({
#             #                 'loc': row['loc'], 
#             #                 'sitemap': row['sitemap'],
#             #                 'sitemap_size_mb': row['sitemap_size_mb'],
#             #                 'download_date': row['download_date'],
#             #             })

#     context = {
#         # 'sitemap_data'      : sitemap_data,
#         # 'sitemap_url'       : sitemap_url,
#         # 'sitemap_url_exist' : sitemap_url_exist,
#         # 'heading'           : heading,
#         # 'registros'         : registros
#     }

#     return JsonResponse(context, status=200, safe=False)

