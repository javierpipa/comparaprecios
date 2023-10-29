from precios.models import (
    Marcas,
    Articulos,
    Settings,
)
from django.db.models import  Count
from django.contrib.sites.models import Site as siteSite
from django.shortcuts import render
from datetime import datetime
import math

def get_domain():
    current_site = siteSite.objects.get_current()
    domain = 'https://' + current_site.domain

    return domain

def customhandler404(request, exception, template_name='errors/404.html'):
    response = render(request, template_name)
    response.status_code = 404
    return response


def sitemaps_articles(request, pagina):
    pagina = int(pagina)
    suffix = get_domain()

    records     = Articulos.objects.all()
    num_paginas = int(Articulos.objects.all().count() / 10000) + 1

    if pagina < 1 or pagina > num_paginas:
        return customhandler404(request, exception=404)
    
    desde   = (( pagina - 1 ) * 10000 ) + 0
    hasta   = (( pagina     ) * 10000 ) - 1

    priority = '0.5'
    changefreq = "weekly"
    
    records =  records[desde:hasta]

    urlset = []
    for rec in records:
        urlset.append({'location': suffix + rec.get_absolute_url(), 'lastmod': rec.created.strftime('%Y-%m-%d'), 'priority': priority, 'changefreq': changefreq})

    return render(request, 'sitemaps/custom_sitemap.html', { 'context': urlset }, content_type='content_type="application/xml; charset=utf-8')

def sitemaps_marcas(request, pagina):
    pagina = int(pagina)
    suffix = get_domain()
    MinSuperCompara         = int(Settings.objects.get(key='MinSuperCompara').value)

    lastmod = datetime.today().strftime('%Y-%m-%d')

    subquery    = Articulos.objects.values('marca__nombre').annotate(cantidad=Count('id')).filter(cantidad__gte=MinSuperCompara).values_list('marca__id', flat=True)
    records     = Marcas.objects.filter(id__in=subquery).filter(es_marca=True)
    num_paginas = int(Marcas.objects.filter(id__in=subquery).count() / 1000) + 1

    print(num_paginas)

    if pagina < 1 or pagina > num_paginas:
        return customhandler404(request, exception=404)
        
    desde   = (( pagina - 1 ) * 10000 ) + 0
    hasta   = (( pagina     ) * 10000 ) - 1

    priority = '0.5'
    changefreq = "weekly"
    
    records =  records[desde:hasta]

    urlset = []
    for rec in records:
        urlset.append({'location': suffix + rec.get_absolute_url(), 'lastmod': lastmod, 'priority': priority, 'changefreq': changefreq})

    return render(request, 'sitemaps/custom_sitemap.html', { 'context': urlset }, content_type='content_type="application/xml; charset=utf-8')


def marcas_y_articulos_sitemaps(request, file_size=1000):
    
    domain = get_domain()
    suffix = domain + '/precios/sitemaps/'
    lastmod = datetime.today().strftime('%Y-%m-%d')
    paths = []

    ####### Marcas
    subquery = Articulos.objects.values('marca__nombre').annotate(cantidad=Count('id')).filter(cantidad__gt=0).values_list('marca__id', flat=True)
    num_records = Marcas.objects.filter(id__in=subquery).count()
    try:
        paginas = math.ceil(num_records / 10000)
        
    except:
        paginas = 1
    
    for x in range(1, paginas + 1):
        filename = f'{suffix}brands-{x}.xml'
        paths.append({'url': filename, 'lastmod': lastmod})

    ####### Articulos
    num_records = Articulos.objects.all().count()
    try:
        # paginas = int(round(num_records / 10000,0))
        paginas = math.ceil(num_records / 10000)
    except:
        paginas = 1

    
    for x in range(1, paginas + 1):
        filename = f'{suffix}articles-{x}.xml'
        paths.append({'url': filename, 'lastmod': lastmod})


    # ####### SiteURLResults
    # num_records = SiteURLResults.objects.filter(site__enable=True).all().count()
    # try:
    #     # paginas = int(round(num_records / 10000,0))
    #     paginas = math.ceil(num_records / 10000)
    # except:
    #     paginas = 1

    
    # for x in range(1, paginas + 1):
    #     filename = f'{suffix}URLResults-{x}.xml'
    #     paths.append({'url': filename, 'lastmod': lastmod})


    
    return render(request, 'sitemaps/sitemap_index.html', { 'context': paths }, content_type='content_type="application/xml; charset=utf-8')

# def sitemaps_URLResults(request, pagina):
#     pagina = int(pagina)
#     suffix = get_domain()
#     lastmod = datetime.today().strftime('%Y-%m-%d')

    
#     records     = SiteURLResults.objects.filter(site__enable=True).all()
#     num_paginas = int(SiteURLResults.objects.filter(site__enable=True).all().count() / 10000) + 1

#     if pagina < 1 or pagina > num_paginas:
#         return customhandler404(request, exception=404)
    
#     desde   = (( pagina - 1 ) * 10000 ) + 0
#     hasta   = (( pagina     ) * 10000 ) - 1

#     priority = '0.5'
#     changefreq = "weekly"
    
#     records =  records[desde:hasta]

#     urlset = []
#     for rec in records:
#         urlset.append({'location': suffix + rec.get_absolute_url(), 'lastmod': rec.updated.strftime('%Y-%m-%d'), 'priority': priority, 'changefreq': changefreq})

#     return render(request, 'sitemaps/custom_sitemap.html', { 'context': urlset }, content_type='content_type="application/xml; charset=utf-8')