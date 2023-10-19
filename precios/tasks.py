
from __future__ import absolute_import
from celery import shared_task

from datetime import datetime, timedelta, date
import time
from django.core import management

import pytz
utc=pytz.UTC

from precios.models import (
    Settings,
    Site, 
    SiteURLResults,
    PAGECRAWLER,
    Marcas,
    Vendedores,
    Unifica,
    Articulos,
    AllPalabras,
    ReemplazaPalabras,
)
from precios.pi_get import reemplaza_palabras        
from precios.pi_rules import (
    intenta_marca,
    createRule, 
)
# from precios.pi_emails import send_email_account_daily
# , send_email_account_daily
from members.models import (
    Periodo,
)
from precios.pi_functions import (
    setMessage, 
)   
#### Jupiter
# DJANGO_PROJECT="myproject" jupyter notebook
# python3 -m  celery  --app=myproject beat &
# python3 -m  celery  --app=myproject flower &
# python3 -m  celery --app=myproject worker -Q core_calc  -n worker1.%h &
# python3 -m  celery --app=myproject worker -Q core_front -n worker2.%h & 
# python3 -m  celery --app=myproject worker -Q core_selenium -n worker3.%h &
# python3 -m  celery --app=myproject worker -Q core_selenium2 -n worker4.%h -E

@shared_task(queue='core_calc')
def elimina_relacion_reglas(self):
    setMessage('Eliminando relacion con reglas')
    urls = SiteURLResults.objects.all()

    for url in urls:
        url.reglas.clear()


@shared_task(queue='core_calc')
def limpiar_y_borrar_inicial():
    setMessage('Generando articulos especial')

    ## Pongo en 0 num_rules_created
    rule = Settings.objects.get(key='num_rules_created')
    rule.value = 0
    rule.save()
    
    ## Elimina todas la reglas automaticas
    Unifica.objects.filter(automatico=True).delete() 

    ## Elimina vendedores y articulos
    setMessage('Elimina vendedores y articulos')
    Vendedores.objects.all().delete()
    Articulos.objects.all().delete()


@shared_task(queue='core_calc')
def rules_marcas( marcaid):
    ### Articulos debe estar lleno !!!
        
    ### de todas las reglas no automaticas
    ### que tengan si_nombre y entonces_nombre en blanco
    ### Se generan reglas automaticas

    queryRules = Unifica.objects.filter(automatico=False, si_nombre=None, entonces_nombre=None).all()
    if marcaid:
        marcaObj = Marcas.objects.filter(id=marcaid).get()
        queryRules = Unifica.objects.filter(automatico=False, si_marca=marcaObj).all()

    print(f'reglas de cambio de marca = {len(queryRules)}')
    num_articulos_cambio_marca = 0
    for rule in queryRules:
        print(f'si marca={rule.si_marca}')
        si_marca        = rule.si_marca
        entonces_marca  = rule.entonces_marca

        filtrado_por_marca = Articulos.objects.filter(marca=si_marca)

        num_articulos_cambio_marca = num_articulos_cambio_marca + len(filtrado_por_marca)
        print(f'num_articulos_cambio_marca = {num_articulos_cambio_marca}')
        for rowarticulo in filtrado_por_marca:         ## Por cada marca
            if rowarticulo.envase == '' :
                pon_envase = None
            else:
                pon_envase = rowarticulo.envase
            if rowarticulo.nombre == '' :
                pon_nombre = None
            else:
                pon_nombre = rowarticulo.nombre
                
            pon_nombre = reemplaza_palabras(pon_nombre)
            createRule(
                    si_marca, 
                    pon_nombre, 
                    rowarticulo.grados2, 
                    rowarticulo.medida_cant, 
                    rowarticulo.unidades, 
                    pon_envase, 
                    rowarticulo.talla, 

                    entonces_marca, 
                    pon_nombre, 
                    rowarticulo.grados2, 
                    rowarticulo.medida_cant, 
                    rowarticulo.unidades,
                    pon_envase,
                    rowarticulo.talla, 
                    'cambio de marca'
                )
            
        si_marca_obj        = rule.si_marca
        entonces_marca_obj  = rule.entonces_marca

        si_marca_obj.es_marca = False
        si_marca_obj.save()

        entonces_marca_obj.es_marca = True
        entonces_marca_obj.save()

    print(f'TOTAL num_articulos_cambio_marca = {num_articulos_cambio_marca}')

@shared_task(queue='core_calc')
def generar_una_regla(self,marca_id):
    intenta_marca(marca_id, False, None)



@shared_task(queue='core_calc')
def limpiar_y_borrar_normal(self,marcaid):
    setMessage('Eliminando articulos')
    ######################################### INICIO      ###################
    if marcaid:
        marcaObj = Marcas.objects.filter(id=marcaid).get()
        Articulos.objects.filter(marca=marcaObj).delete()
        Unifica.objects.filter(si_marca=marcaObj).update(contador=0)
    else:
        Unifica.objects.all().update(contador=0)
        AllPalabras.objects.all().update(contador=0)
        ReemplazaPalabras.objects.all().update(contador=0)

        setMessage('Eliminando vendedores')
        Vendedores.objects.all().delete()
    
    ######################################### FIN INICIO  ###################


@shared_task(queue='core_calc')
def limpiar_final(self, marcaid):
    setMessage('Elimina reglas automaticas sin uso')
    Unifica.objects.filter(automatico=True, contador=0).delete()  ### Borra reglas sin uso

    setMessage('Elimina productos sin vendedores')
    arts = Articulos.objects.all()
    cuenta = 0
    nocuenta = 0
    for art in arts:
        if art.cuanntosvenden() == 0:
            try:
                art.delete()
                cuenta = cuenta + 1
            except Exception as e:
                print(e)
        else:
            nocuenta = nocuenta + 1

    print(f'Se eliminan {cuenta} no se eliminan={nocuenta}')
    
    if not marcaid:
        setMessage('Actualizando numero de veces que reglas han sido creadas')
        rules = Settings.objects.get(key='num_rules_created')
        rules.value = str(int(rules.value) + 1)
        rules.save()

    setMessage('')

from .pi_functions import (
    checkIfProcessRunning,
    
)

# @shared_task(queue='users_mail',bind=True)
# def send_daily_account_emails(request):
#     accounts = Account.objects.filter(enabled=True)
#     mydate = date.today()
    
#     for account in accounts:
#         send_email_account_daily(request,account.id,mydate,False)


@shared_task(queue='core_calc',bind=True)
def check_periods(request):
    import calendar
    ## Does this date have a period ??
    today = datetime.today()
    this_month = today.month
    this_year = today.year
    try:
        period = Periodo.objects.get(start_date__year=this_year, start_date__month = this_month)
    except Periodo.DoesNotExist:
        ## Create this new period
        firs_day, last_day = calendar.monthrange(this_year,this_month)
        p = Periodo(
            start_date = date(this_year, this_month, 1),
            end_date   = date(this_year, this_month, last_day),
            active     = True
            )
        p.save()

        ## Are other periods active ?
        periods = Periodo.objects.filter(active=True)
        for period in periods:
            start_date = str(period.start_date)
            end_date = str(period.end_date)
            max_prev = date.today() - timedelta(days=0)
            if max_prev > period.end_date :
                print('Closing period: ', period)
                period.active = False
                period.save()            


@shared_task(queue='core_calc',bind=True)
def CreateRules(request):
    management.call_command('createRules')


######### createProds ################
@shared_task(queue='core_calc')
def CreateProds(request, site_id):
    management.call_command('createProds', site_id, 2)

######### FIN createProds ################


########## Cities ###########
@shared_task(queue='core_calc',bind=True)
def updateCities(request):
    management.call_command('update_cities')


########## GetAllSiteMap ###########
@shared_task(queue='core_calc',bind=True)
def getSiteMaps(request):
    sites = Site.objects.filter(siteSearch='sitemap', enable=True).all()
    for site in sites:
        management.call_command('getSiteMap', site.id)


@shared_task(queue='core_calc',bind=True)
def getURLFromMaps(request):
    sites = Site.objects.filter(siteSearch='sitemap', enable=True).all()
    for site in sites:
        management.call_command('getURLFromSiteMap', site.id)
    


########## getSiteURLS ###########
@shared_task(queue='core_calc',bind=True)
def getURLS(self, siteid):

    management.call_command('getSiteURL', siteid)

@shared_task(queue='core_calc',bind=True)
def getSiteURLS(request):
    funncionnando = checkIfProcessRunning("geckodriver", True)

    sites = Site.objects.filter(siteSearch='crawler', enable=True).order_by('last_scan')
    
    for site in sites:
        getURLS.apply_async(args=(site.id,), expires=1600)
########## FIN getSiteURLS ###########


########## Del404URLS ###########
@shared_task(queue='core_calc',bind=True)
def Del404URLS(request):
    
    sites = Site.objects.filter(enable=True)
    
    for site in sites:
        sitio = Site.objects.get(pk=site.id)
        urls = SiteURLResults.objects.filter(site=sitio, error404=True)
        urls.delete()


###### BEAUTIFUL #############################

@shared_task(queue='core_front',bind=True)
def getBeautiful(self, siteid):
    management.call_command('getProducts-beautiful', siteid)

@shared_task(queue='core_front',bind=True)
def getProductsBeautiful(request):

    sites = Site.objects.filter(productSearchEnabled=True,crawler=PAGECRAWLER.BEAUTIFULSOUP, enable=True)
    for site in sites:
        print(f'Site={site.siteName}')
        getBeautiful.apply_async(args=(site.id,), expires=1600)
        
###### FIN BEAUTIFUL #############################



########## SELENNIUM #######

@shared_task(queue='core_selenium2',bind=True)
def getSelenium2(self, siteid, startrecord=0 ):
    default_num_urls = int(Settings.objects.get(key='Get_Selenium_default_num_urls').value)
    management.call_command('getProducts-selenium', siteid, default_num_urls, startrecord)
        


@shared_task(queue='core_selenium',bind=True)
def getSelenium(self, siteid, startrecord=0 ):
    default_num_urls = int(Settings.objects.get(key='Get_Selenium_default_num_urls').value)
    management.call_command('getProducts-selenium', siteid, default_num_urls, startrecord)
        

@shared_task(queue='core_selenium',bind=True)
def getProductsSelenium(request):
    default_num_urls                = int(Settings.objects.get(key='Get_Selenium_default_num_urls').value)
    default_max_paralelle_workers   = int(Settings.objects.get(key='Get_Selenium_max_paralelle_workers').value)
    
    funncionnando = checkIfProcessRunning("geckodriver", True)
    sites = Site.objects.filter(productSearchEnabled=True,crawler=PAGECRAWLER.SELENIUM, enable=True)


    vdia1 = utc.localize(datetime.today()) - timedelta(days=0)
    vdia2 = utc.localize(datetime.today()) - timedelta(days=1)
    vdia3 = utc.localize(datetime.today()) - timedelta(days=2)
    vdia15 = utc.localize(datetime.today()) - timedelta(days=15)
    tot_dia1 = 0
    tot_dia2 = 0
    tot_dia3 = 0
    for site in sites:
        dia1   = SiteURLResults.objects.filter(site=site.id, updated__range=(vdia2, vdia1)).exclude( error404=True).count()
        dia2   = SiteURLResults.objects.filter(site=site.id, updated__range=(vdia3, vdia2)).exclude( error404=True).count()
        dia3   = SiteURLResults.objects.filter(site=site.id, updated__range=(vdia15, vdia3)).exclude( error404=True).count()
        tot_dia1 = tot_dia1 + dia1
        tot_dia2 = tot_dia2 + dia2
        tot_dia3 = tot_dia3 + dia3

    print(f'tot dia 1={tot_dia1};  tot dia 2={tot_dia2}; tot dia 3={tot_dia3}')
    for site in sites:
        dia1   = SiteURLResults.objects.filter(site=site.id, updated__range=(vdia2, vdia1)).exclude( error404=True).count()
        dia2   = SiteURLResults.objects.filter(site=site.id, updated__range=(vdia3, vdia2)).exclude( error404=True).count()
        if dia2 > 0:
            print(f'Site={site.siteName} urlCount={site.urlCount}  dia2={dia2}')
            getSelenium.apply_async(args=(site.id,0), expires=1600)
            time.sleep(0.5)

        suma_reg_viejos_del_sitio = dia2
        suma_reg_viejos_totales = tot_dia2 + 1
        workers = int(round((suma_reg_viejos_del_sitio / suma_reg_viejos_totales),2) * default_max_paralelle_workers)
        if workers > 0:
            print(f'Site={site.siteName}   dia1={dia1}')
            for ciclo in range(1,workers):
                startrecord = ciclo * default_num_urls
                print(f'Site={site.siteName} urlCount={site.urlCount}  suma_reg_viejos={suma_reg_viejos_del_sitio} startrecord={startrecord}')
                getSelenium.apply_async(args=(site.id,startrecord), expires=1600)
                time.sleep(0.5)

            

    for site in sites:
        dia1   = SiteURLResults.objects.filter(site=site.id, updated__range=(vdia2, vdia1)).exclude( error404=True).count()
        dia2   = SiteURLResults.objects.filter(site=site.id, updated__range=(vdia3, vdia2)).exclude( error404=True).count()
        dia3   = SiteURLResults.objects.filter(site=site.id, updated__range=(vdia15, vdia3)).exclude( error404=True).count()
        suma_reg_viejos_del_sitio =  dia3
        suma_reg_viejos_totales =  tot_dia3 + 1
        workers = int(round((suma_reg_viejos_del_sitio / suma_reg_viejos_totales),2) * default_max_paralelle_workers)
        if workers > 0:
            for ciclo in range(1,workers):
                startrecord = (ciclo * default_num_urls) + dia2
                print(f'Site={site.siteName} urlCount={site.urlCount}  suma_reg_viejos={suma_reg_viejos_del_sitio} startrecord={startrecord}')
                getSelenium2.apply_async(args=(site.id,startrecord), expires=1600)
                time.sleep(0.5)
              


########## FINN  SELENNIUM #######

# Borra URL con 404
# from precios.models import (Site, SiteURLResults)  
# sitio = Site.objects.get(pk=4)
# urls = SiteURLResults.objects.filter(site=sitio, error404=True)
# urls.count()
# urls.delete()
# urls = SiteURLResults.objects.filter(site=sitio, nombre__exact='')