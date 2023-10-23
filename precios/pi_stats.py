
from django.shortcuts import get_object_or_404
from members.models import (
    Member,
    Lista, 
    DetalleLista,
    Plan,
    ContenidoPlan,
    Periodo,
    MemberStats,
    OBJETOS_EN_PLAN,

)
from precios.models import (
    PriceHistory,
    Articulos,
    Vendedores,
    SiteURLResults
)
from django.db import connection,  connections

id_objeto_consulta          = OBJETOS_EN_PLAN.BUSQUEDAS
id_objeto_consulta_marca    = OBJETOS_EN_PLAN.BUSQ_MARCAS
the_period                  = Periodo.objects.filter(active=True).order_by('start_date').first()

def get_product_price_history(id_prod, site_list):
    site_list = ','.join(str(v) for v in site_list)
  
    query_resume    = "select \
                        precios_siteurlresults.id, \
                        precios_pricehistory.OldDate, \
                        precios_pricehistory.Oldprecio, \
                        precios_vendedores.articulo_id, \
                        precios_siteurlresults.site_id , \
                        precios_site.siteName,  \
                        precios_siteurlresults.site_id \
                    from precios_vendedores \
                    inner join precios_siteurlresults  on precios_vendedores.vendidoen_id = precios_siteurlresults.id \
                    inner join precios_site on precios_siteurlresults.site_id = precios_site.id \
                    inner join precios_articulos on precios_vendedores.articulo_id = precios_articulos.id \
                    inner join precios_pricehistory  on precios_siteurlresults.id = precios_pricehistory.FromResult_id \
                    where articulo_id= " + str(id_prod) + " \
                    and precios_site.id in (" + site_list + ") \
                    and precios_siteurlresults.error404 = False \
                    order by precios_pricehistory.OldDate "

    # cursor = connections['precios'].cursor()
    cursor = connection.cursor()
    cursor.execute(query_resume)
    records = cursor.fetchall()
    
    sitios = set()
    last_valor  = {}
    for rec in records:
        sitios.add(rec[5])
        last_valor[rec[4]] = {}
        last_valor[rec[4]].update({'id': str(rec[4]), 'name': rec[5],  'valor':rec[2]}) 
    
    lineas  = []
    linea = {}
    
    for rec in records:
        linea = {}
        valores = []
        for sitio in last_valor:
            if last_valor[sitio].get('name') == rec[5]:
                valores.append({'id':last_valor[sitio].get('id'), 'name':last_valor[sitio].get('name'),'valor':rec[2] })
                last_valor[rec[4]].update({'id': str(rec[4]), 'name': rec[5],  'valor':rec[2]}) 
            else:
                valores.append({'id':last_valor[sitio].get('id'), 'name':last_valor[sitio].get('name'),'valor':last_valor[sitio].get('valor') })
            linea.update({'fecha':rec[1],'valores':valores})

        
        lineas.append(linea)

    return lineas, sitios

    
#### Busquedas de marcas
def may_marca(request):
    ### Puede el cliente hacerlo ?
    cliente_cuantos     = get_object_or_404(MemberStats.objects.all(), 
                member = request.user.member,
                objeto = id_objeto_consulta_marca,
                period = the_period)
    
    plan_maximo = get_object_or_404(ContenidoPlan.objects.all(),
                plan = request.user.member.account2.plan,
                objeto = id_objeto_consulta_marca)
    
    if plan_maximo.cantidad > cliente_cuantos.cuantity or plan_maximo.todos:
        return True
    else:
        return False

def save_consulta_marca_count(request):
    
    periodstat, created = MemberStats.objects.get_or_create(
        member=request.user.member,
        objeto = id_objeto_consulta_marca,
        period = the_period
        )
    if created:
        periodstat.cuantity = 1
    else:
        periodstat.cuantity = periodstat.cuantity + 1
    periodstat.save()

#### Busquedas de precios
def may_consulta(request):
    ### Puede el cliente hacerlo ?
    cliente_cuantos     = get_object_or_404(MemberStats.objects.all(), 
                member = request.user.member,
                objeto = id_objeto_consulta,
                period = the_period)
    
    plan_maximo = get_object_or_404(ContenidoPlan.objects.all(),
                plan = request.user.member.account2.plan,
                objeto = id_objeto_consulta)
    
    if plan_maximo.cantidad > cliente_cuantos.cuantity or plan_maximo.todos:
        return True
    else:
        return False

def save_consulta_count(request):
    
    periodstat, created = MemberStats.objects.get_or_create(
        member=request.user.member,
        objeto = id_objeto_consulta,
        period = the_period
        )
    if created:
        periodstat.cuantity = 1
    else:
        periodstat.cuantity = periodstat.cuantity + 1
    periodstat.save()