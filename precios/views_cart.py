
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.http import JsonResponse
from .models import (
    MomentosDespacho,
    AreasDespacho,
    Articulos,
    Vendedores,
)
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponseRedirect

from members.models import (
    Member,
    Lista, 
    DetalleLista,
    ContenidoPlan,
    Periodo,
    OBJETOS_EN_PLAN,
    MemberStats
)
from precios.pi_functions import getMomentos
from django.views.decorators.cache import (
    cache_page, 
    never_cache, 
)
from dj_shop_cart.cart import get_cart_class
from operator import itemgetter


Cart = get_cart_class()

def could_user_to(request, objeto, cantidad_hasta_ahora):
    # Revisa si el usuario puede solicitar mas de un objeto
    user            = request.user
    max_objeto     = ContenidoPlan.objects.filter(plan=user.member.account2.plan, objeto=objeto).values_list('cantidad',flat=True).get()
    
    print(max_objeto, cantidad_hasta_ahora)
    if max_objeto >= cantidad_hasta_ahora:
        return True
    else:
        return False
    
# @never_cache
def getLastCart(request):
    lista_arr = {}
    if request.user.is_authenticated:
        lista = Lista.objects.filter(member=request.user.member).order_by("updated").first()
        if lista:
            lista_arr = {'id': lista.pk, 'nombre': lista.nombre_lista}
        
    return lista_arr

@never_cache
def cart(request):
    ## Entrega lista del carrito ##
    
    context = {}
    cart = Cart.new(request)
    context['cart'] = cart
    momentos, supermercadoscount = getMomentos(request)
    
    if request.session.get('costo_despacho'):
        context['costo_despacho'] = request.session.get('costo_despacho')
    context['supermercados'] = momentos
        
    return render(request, 'precios/carrito.html', { 'context': context, })


@never_cache
@require_POST
def add_product(request):
    cart = Cart.new(request)
    if could_user_to(request, OBJETOS_EN_PLAN.PROD_EN_LISTA,  len(cart)):
        prrod = request.POST["product"]
        print(f'prrod={prrod}')

        
        product = get_object_or_404(Articulos.objects.all(), id=prrod)

        print(f'product={product}')
        quantity = int(request.POST.get("quantity", 0))
        cart.add(product, variant=1, quantity=quantity)

        table = createCart(request, cart)
        return JsonResponse(table, status=200, safe=False)
    else:
        return JsonResponse([], status=403, safe=False)
    
@never_cache
@require_POST
def get_cart(request):
    cart = Cart.new(request)

    table = createCart(request, cart)

    return JsonResponse(table, status=200, safe=False)

@never_cache
@require_POST
def get_cart_simple(request): 
    cart = Cart.new(request)

    table = createCartSimple(request, cart)
    

    return JsonResponse(table, status=200, safe=False)


def get_despachos(request, site_id, totcompra):
    # print('Solicita=',site_id)

    monto_minimo_compra = 0
    arr_areas = []

    areas_super     = AreasDespacho.objects.filter(site=site_id,comuna=request.user.member.comuna.id)
    
    for area in areas_super:
        momentos = MomentosDespacho.objects.filter(areaDespacho=area)
        monto_minimo_compra = area.monto_minimo_compra
        horario = []
        for momento in momentos:
            arrdia = ''
            for dia in momento.dia.all().values('nombre'):
                arrdia = arrdia + dia.get('nombre') + ', ' 
            arrhora = ''
            for dia in momento.horario.all().values('inicio', 'termino'):
                arrhora = arrhora + str(dia.get('inicio')) + ' - ' + str(dia.get('termino')) + ', ' 


            horario.append({'dias': arrdia, 'horas': arrhora})

        arr_areas.append({
            'areaDespacho_id': area.site.id,
            'areaDespacho_siteName': area.site.siteName,
            'areaDespacho_despachoid': area.id,
            'areaDespacho_area': area.area,
            'areaDespacho_monto_minimo_compra': area.monto_minimo_compra,
            'areaDespacho_valor_despacho': area.valor_despacho,
            'areaDespacho_dias_para_despacho': area.dias_para_despacho,
            'areaDespacho_dias_habiles': area.dias_habiles,
            'areaDespacho_dias': horario,
        })


    return arr_areas, monto_minimo_compra



def alternativas_prod2(respecto_del_producto, item, item_subtotal_entregado, misuper):
    ### busca articulos con la misma:
    # nombre
    # marca
    # medida_cant
    # grados
    ### Que despachen a las comunas del usuario
    try:
        valor_x_un = item_subtotal_entregado / ( respecto_del_producto.medida_cant * item.quantity )
    except ZeroDivisionError:
        valor_x_un = item_subtotal_entregado
    
    # print(f'valor_x_un = {valor_x_un}')

    cambio_unidad_medida = False
    sugiere = []
    
    propuesta_total = 0
        
    ret_cant    = item.quantity
    cambio      = False
    lineas      = []
    item_subtotal = 0
    # print('sugiere final = ', len(sugiere) )
    
    if len(sugiere) == 0:
        ## obtener precio de ese supermercado
        art = Vendedores.objects.filter(
            vendidoen__site__id     = misuper,
            articulo__pk            = respecto_del_producto.pk).first()
        
        item_subtotal = item.quantity * art.precio
        # print("aca 1")
        linea = {
            'item_id': item.id,
            'item_quantity': item.quantity,
            'item_product_pk': item.product_pk,
            'item_product_slug': respecto_del_producto.slug,
            'item_product': item.product.nombre,
            'item_price': art.precio,
            'item_subtotal': item_subtotal,
            'item_id_super': misuper,
            'nombre_original': respecto_del_producto.nombre_original,
            'nombre': respecto_del_producto.nombre,
            'marca': respecto_del_producto.marca.nombre,
            'medida_um': respecto_del_producto.medida_um,
            'medida_cant': respecto_del_producto.medida_cant,
            'unidades': respecto_del_producto.unidades,
            'dimension': respecto_del_producto.dimension,
            'color': respecto_del_producto.color,
            'envase': respecto_del_producto.envase,
            'grados': respecto_del_producto.grados2,
            'ean_13': respecto_del_producto.ean_13,
            'id': respecto_del_producto.id,
            'cambio': cambio
        }
        lineas.append(linea)
        retorna_subtotal = item_subtotal
        # print('en len = 0')
        
    # for p in sugiere:
        
    #     item_subtotal = item.quantity * item.price
    #     print("Ciclo sugerencias: item_subtotal_entregado", item_subtotal_entregado, p.vendidoen.precio, item_subtotal, item.quantity , p.articulo.unidades)
    #     if propuesta_total < item_subtotal_entregado :
    #         ## and item.quantity >= p.articulo.unidades:
    #         # print("Entra a sugerencias IF ")
    #         if cambio_unidad_medida:
    #             # respecto_del_producto.medida_cant * item.quantity
    #             ret_cant        = int((respecto_del_producto.medida_cant * item.quantity) / p.articulo.medida_cant)
    #             saldo_items     = 0
    #             if int((respecto_del_producto.medida_cant * item.quantity) / p.articulo.medida_cant) != (respecto_del_producto.medida_cant * item.quantity) / p.articulo.medida_cant :
    #                 saldo_items     = 1
    #             medida_cant     = p.articulo.medida_cant
    #         else:
    #             ret_cant        = int(item.quantity / p.articulo.unidades)
    #             saldo_items     = item.quantity - (ret_cant * p.articulo.unidades)
    #             medida_cant     = p.articulo.medida_cant
    #         cambio          = True
    #         linea = {
    #             'item_id': item.id,
    #             'item_quantity': ret_cant,
    #             'item_product_pk': p.articulo.id,
    #             'item_product_slug': p.articulo.slug,
    #             'item_product': item.product.nombre,
    #             'item_price': p.vendidoen.precio,
    #             'item_subtotal': p.vendidoen.precio * ret_cant,
    #             'item_id_super': misuper,
    #             'nombre_original': respecto_del_producto.nombre_original,
    #             'nombre': respecto_del_producto.nombre,
    #             'marca': respecto_del_producto.marca.nombre,
    #             'medida_um': p.articulo.medida_um,
    #             'medida_cant': medida_cant,
    #             'unidades': p.articulo.unidades,
    #             'dimension': respecto_del_producto.dimension,
    #             'color': respecto_del_producto.color,
    #             'envase': respecto_del_producto.envase,
    #             'grados': respecto_del_producto.grados2,
    #             'ean_13': respecto_del_producto.ean_13,
    #             'id': respecto_del_producto.id,
    #             'cambio': cambio
    #         }
    #         retorna_subtotal = p.vendidoen.precio * ret_cant
    #         lineas.append(linea)
    #         if saldo_items > 0 :
    #             print("agregar otra linea")
    #             linea = {
    #                 'item_id': item.id,
    #                 'item_quantity': saldo_items,
    #                 'item_product_pk': item.product_pk,
    #                 'item_product_slug': respecto_del_producto.slug,
    #                 'item_product': item.product.nombre,
    #                 'item_price': item.price,
    #                 'item_subtotal': item.price * saldo_items,
    #                 'item_id_super': misuper,
    #                 'nombre_original': respecto_del_producto.nombre_original,
    #                 'nombre': respecto_del_producto.nombre,
    #                 'marca': respecto_del_producto.marca.nombre,
    #                 'medida_um': respecto_del_producto.medida_um,
    #                 'medida_cant': respecto_del_producto.medida_cant,
    #                 'unidades': respecto_del_producto.unidades,
    #                 'dimension': respecto_del_producto.dimension,
    #                 'color': respecto_del_producto.color,
    #                 'envase': respecto_del_producto.envase,
    #                 'grados': respecto_del_producto.grados2,
    #                 'ean_13': respecto_del_producto.ean_13,
    #                 'id': respecto_del_producto.id,
    #                 'cambio': False
    #             }
    #             lineas.append(linea)
    #             retorna_subtotal = retorna_subtotal + (item.price * saldo_items)
    #             # item_subtotal = item_subtotal + (item.price * saldo_items)
    #     else:
    #         print("Entra a sugerencias ELSE ")
    #         art = Vendedores.objects.filter(id = p.id).get()
    #         # print(art.precio)
    #         item_subtotal = item.quantity * art.precio
    #         linea = {
    #             'item_id': item.id,
    #             'item_quantity': item.quantity,
    #             'item_product_pk': item.product_pk,
    #             'item_product_slug': respecto_del_producto.slug,
    #             'item_product': item.product.nombre,
    #             'item_price': art.precio,
    #             'item_subtotal': item_subtotal,
    #             'item_id_super': misuper,
    #             'nombre_original': respecto_del_producto.nombre_original,
    #             'nombre': respecto_del_producto.nombre,
    #             'marca': respecto_del_producto.marca.nombre,
    #             'medida_um': respecto_del_producto.medida_um,
    #             'medida_cant': respecto_del_producto.medida_cant,
    #             'unidades': respecto_del_producto.unidades,
    #             'dimension': respecto_del_producto.dimension,
    #             'color': respecto_del_producto.color,
    #             'envase': respecto_del_producto.envase,
    #             'grados': respecto_del_producto.grados2,
    #             'ean_13': respecto_del_producto.ean_13,
    #             'id': respecto_del_producto.id,
    #             'cambio': cambio
    #         }
    #         lineas.append(linea)
    #         # item_subtotal = item_subtotal_entregado
    #         retorna_subtotal = item_subtotal

    # if  item_subtotal_entregado < retorna_subtotal:
    #     print("No  corresponde hacer cambio")
    #     # lineas = []
    
    return lineas, retorna_subtotal 

# @never_cache
def createCartSimple(request, cart):
    itemsInCart = 0 
    for item in cart:
        itemsInCart += 1

    pass
    costo_despacho = None
    if request.session.get('costo_despacho'):
        costo_despacho = request.session.get('costo_despacho')

    superdetail = {
        'itemsInCart': itemsInCart,
        'costo_despacho': costo_despacho
    }
    table = { 'superdetail': superdetail}
    return table


def createCart(request, cart):

    
    lista = getLastCart(request)
    
    tableProd   = []
    superset    = []
    totsuper    = []
    super_req   = []

    costo_despacho = None
    if request.session.get('costo_despacho'):
        costo_despacho = request.session.get('costo_despacho')


    ## Que super me despachan
    momentos, supermercadoscount = getMomentos(request)

    lossuperlist = momentos.values_list('areaDespacho__site__pk',flat=True).distinct()
    supermercadoscount = len(lossuperlist)
    supersinproductos = 0

    #### Lista de productos en la lista #####
    itemsInCart = 0 
    grantotalunidades = 0
    for item in cart:
        itemsInCart += 1
        producto = Articulos.objects.get(id=item.product_pk)
        
        ### obtengo id super que venden este producto y que me pueden despachar
        idsuper = Vendedores.objects.filter(articulo=producto)
        idsuper = idsuper.filter(vendidoen__site__pk__in=lossuperlist)
        idsuper = idsuper.values_list('vendidoen__site__pk',flat=True)
        superset.extend(list(idsuper))
        
        ## Obtengo mejor precio de esta lista de super
        bestpriceA = Vendedores.objects.filter(articulo=producto)
        bestpriceA = bestpriceA.filter(vendidoen__site__pk__in=lossuperlist)

        dequien    = bestpriceA.values_list('vendidoen__site__siteName',flat=True).order_by('vendidoen__precio').first()

        grantotalunidades =  grantotalunidades  +  ( item.quantity *  producto.unidades)

        tableProd.append({
            'item_id': item.id,
            'item_quantity': item.quantity,
            'item_product_pk': item.product_pk,
            'item_product_slug': producto.slug,
            'item_product': item.product.nombre,
            # 'item_price': bestprice,
            # 'item_price': item.price,
            # 'item_subtotal': item.subtotal,
            'item_id_super': list(idsuper),
            'nombre_original': producto.nombre_original,
            'nombre': producto.nombre,
            'marca': producto.marca.nombre,
            'imagen': producto.image1,
            'medida_um': producto.medida_um,
            'medida_cant': producto.medida_cant,
            'unidades': producto.unidades,
            'dimension': producto.dimension,
            'color': producto.color,
            'envase': producto.envase,
            'grados': producto.grados2,
            'ean_13': producto.ean_13,
            'dequien': dequien,
            'id': producto.id,
        })
        if len(list(idsuper)) == 1:
            super_req.extend(list(idsuper))

    ##### Lista de productos en cada supermercado ###
    requerido = False

    for misuper in lossuperlist:
        totcompra   = 0
        tableProd2  = []
        num_lineas  = 0
        supertotalunidades = 0
        for item in cart:
            num_lineas  = num_lineas + 1

            producto = Articulos.objects.get(id=item.product_pk)
            
            ## Obtengo mejor precio de esta lista de super
            bestpriceA = Vendedores.objects.filter(articulo=producto)
            bestpriceA = bestpriceA.values_list('vendidoen__precio',flat=True)
            bestpriceB = bestpriceA.filter(vendidoen__site__pk=misuper).first()
            
            if bestpriceB:
                item_subtotal = item.quantity * bestpriceB
                lineas, item_subtotal1 = alternativas_prod2(producto, item, item_subtotal, misuper)
                
                for linea in lineas:
                    tableProd2.append(linea)
                    supertotalunidades = supertotalunidades + ( linea['item_quantity'] * linea['unidades'])

                totcompra = totcompra + (item_subtotal)
        
        if len(tableProd2)>0:
            tablemomentos, monto_minimo_compra = get_despachos(request, misuper, totcompra)
            

            for despacho in tablemomentos:
                if misuper in super_req:
                    requerido = True

                if supertotalunidades ==  grantotalunidades:
                    seleccionado = 1
                else:
                    seleccionado = 2
                    
                if  totcompra  >= despacho['areaDespacho_monto_minimo_compra']:
                    pre_seleccionado = 0
                else:
                    pre_seleccionado = 1
                    

                totsuper.append({
                    'id': misuper,
                    'pre_seleccionado': pre_seleccionado,
                    'seleccionado': seleccionado,
                    'totcompra': totcompra,
                    # 'monto_minimo_compra':monto_minimo_compra,
                    'monto_minimo_compra':despacho['areaDespacho_monto_minimo_compra'],
                    'tableProd2': tableProd2,
                    # 'supermercados': tablemomentos,
                    'supermercados': despacho,
                    'costo_despacho': tablemomentos[0]['areaDespacho_valor_despacho'],
                    'total_super':  totcompra + tablemomentos[0]['areaDespacho_valor_despacho'],
                    'requerido': requerido,
                    'supertotalunidades': supertotalunidades,
                    'costo_despacho':costo_despacho,
                })
            
        else:
            supersinproductos = supersinproductos + 1
      
    ### Orden

    totsuper = sorted(totsuper, key=itemgetter('seleccionado','pre_seleccionado','total_super'))

    ## Si

    superdetail = {
        'supermercadoscount': supermercadoscount,
        'supersinproductos': supersinproductos,
        'itemsInCart': itemsInCart,
        'grantotalunidades': grantotalunidades,
        'lista': lista,
    }
    table = {'prods':tableProd, 'totsuper': totsuper, 'superdetail': superdetail}
    return table

@never_cache
@require_POST
def increase_product(request):
    prrod = request.POST["product"]
    cart = Cart.new(request)
    quantity = int(request.POST.get("quantity", 0))
    cart.increase(prrod, quantity=quantity)

    table = createCart(request, cart)

    return JsonResponse(table, status=200, safe=False)

@never_cache
@require_POST
def decrementproduct(request):
    prrod = request.POST["product"]
    
    cart = Cart.new(request)
    quantity = int(request.POST.get("quantity", 0))
    cart.remove(prrod, quantity=quantity)

    table = createCart(request, cart)

    return JsonResponse(table, status=200, safe=False)

@never_cache
@require_POST
def removeproduct(request):
    cart = Cart.new(request)
    prrod = request.POST["product"]
    cart.remove(prrod)
    
    table = createCart(request, cart)

    return JsonResponse(table, status=200, safe=False)

@never_cache
def loadcart(request, id, *args, **kwargs):
    cart = Cart.new(request)
    lista = get_object_or_404(Lista.objects.all(), id=id)
    itemslista = DetalleLista.objects.filter(lista = lista)
    for item in itemslista:
        cart.add(item.articulo, quantity=item.cantidad)
            
    return render(request, 'precios/carrito.html', { 'context': '', })
    
@never_cache
def deletecart(request, id, *args, **kwargs):
    try:
        Lista.objects.filter(id=id).delete()
    except ObjectDoesNotExist:
        pass

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
@never_cache
@require_POST
def emptycart(request):
    cart = Cart.new(request)
    cart.empty()
    table = createCart(request, cart)

    return JsonResponse(table, status=200, safe=False)
    
@never_cache
@require_POST
def save_cart(request):
    cart = Cart.new(request)
    nombre_lista=request.POST["nombre_lista"]

    user            = request.user
    member          = Member.objects.get(user=user)
    num_listas = Lista.objects.filter(member=member).count()
    if could_user_to(request, OBJETOS_EN_PLAN.LISTAS,  num_listas):
        lista, created = Lista.objects.update_or_create(
            member=member,
            nombre_lista=nombre_lista,
            )
        DetalleLista.objects.filter(lista = lista).delete()
        for item in cart:
            articulo = Articulos.objects.get(pk=item.product_pk)
            DetalleLista.objects.update_or_create(
                lista = lista,
                articulo = articulo,
                cantidad = item.quantity
            )

        data = {'hola':'hola'}
        return JsonResponse(data)
    else:
        return JsonResponse([], status=403, safe=False)

    