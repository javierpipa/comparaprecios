from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django_json_ld.views import JsonLdDetailView
from django.db.models import Avg, Max, Min, Sum, Subquery, OuterRef, Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from precios.models import (
    Corporation,
    Site, 
    SiteURLResults,
    Marcas,
    Articulos,
    Vendedores,
    PriceHistory,
    Settings,
    Unifica,
)
from precios.forms import (
    MarcasForm,
    CorporationForm,
    ArticulosForm,
    SiteForm,
    SiteURLResultsForm,
    VendedoresForm,
    PriceHistoryForm,
)
from precios.pi_functions import (
    getMomentos,
    getMessage,
    registrar_consulta,
    generate_articulos_dict,
    generate_filters,
)
from precios.pi_stats import (
    get_product_price_history,

)

class VendedoresListView(generic.ListView):
    model = Vendedores
    form_class = VendedoresForm

class PriceHistoryListView(generic.ListView):
    model = PriceHistory
    form_class = PriceHistoryForm

class PriceHistoryDetailView(generic.DetailView):
    model = PriceHistory
    form_class = PriceHistoryForm

class SiteURLResultsListView(generic.ListView):
    model = SiteURLResults
    paginate_by = 100
    form_class = SiteURLResultsForm



class ProductDetailView(JsonLdDetailView):
    template_name   = 'precios/articulos/detalle2.html'
    model           = Articulos

    
    def get_context_data(self, *args, **kwargs):
        context  = {}
        ExternalUrlPostUrl           = Settings.objects.get(key='ExternalUrlPostUrl').value
        momentos, supermercadoscount = getMomentos(self.request)

        messages.warning(self.request,  str(getMessage()))
        
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        context['resumen'] = {
            'articulos_count':'articulos_count', 
            'ofertas_count': 'ofertas_count',  
            'supermercadoscount': supermercadoscount,
            'ExternalUrlPostUrl': ExternalUrlPostUrl ,
            'meta': 'meta',
        }
        table, head = get_product_price_history(context['articulos'].id, momentos)
        
        articulos = Articulos.objects.filter(pk=context['articulos'].id)
        marca = articulos.get().marca
        articulos_dict  = []
        articulos_count = 0
        for particulo in articulos:
            detalle = Vendedores.objects.\
                filter(articulo__id=context['articulos'].id).\
                filter(vendidoen__site__in=momentos).\
                exclude(vendidoen__precio__exact=0).\
                order_by('vendidoen__precio')
            
            if (len(detalle)) > 0 :
                articulos_count +=1
                ofertas = detalle.count()
                articulos_dict.append({'articulo': particulo,'detalle': detalle, 'ofertas': ofertas})

        context['articulos_dict'] = articulos_dict 
    
        context["table"] = table
        context["head"] = head
        titulo = context['articulos'].titulo
        
        context["title"] =  titulo
        context["cache"] =  "0 Min."
        context["beardcrums"] =  [
            {"Nombre": 'Marcas', 'url': '/precios/brands/'},
            {"Nombre": str(context['articulos'].marca) , 'url': marca.get_absolute_url},
        ]

        return context


class SiteURLResultsDetailView(generic.DetailView):
    model = SiteURLResults
    form_class = SiteURLResultsForm

    def get_context_data(self, **kwargs):
        context = super(SiteURLResultsDetailView, self).get_context_data(**kwargs)

        url = self.get_object()
        reglas = url.reglas.all()
        precios = PriceHistory.objects.filter( FromResult=url.pk)
        if Vendedores.objects.filter(vendidoen=url.pk).exists():
            vendedores = Vendedores.objects.filter(vendidoen=url.pk).first()
        else:
            vendedores = None
        context.update({
            'reglas': reglas,
            'precios': precios,
            'vendidoen': vendedores
        })
        try:
            context["title"] =  vendedores.vendidoen.site.siteName + ": "  + vendedores.articulo.marca.nombre + ', ' + vendedores.vendidoen.nombre 
            context["cache"] =  "0 Min."
            context["beardcrums"] =  [
                {"Nombre": 'Marcas', 'url': '/precios/brands/'},
                {"Nombre": vendedores.articulo.marca.nombre , 'url': vendedores.articulo.marca.get_absolute_url},
                {"Nombre": vendedores.articulo.nombre , 'url': vendedores.articulo.get_absolute_url},
            ]
        except Exception as e:
            print('Error', str(e))

        return context

class SiteListView(generic.ListView):
    model = Site
    paginate_by = 10
    form_class = SiteForm


class SiteDetailView(generic.DetailView):
    model = Site
    form_class = SiteForm
    def get_context_data(self, **kwargs):
        context = super(SiteDetailView, self).get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)

        return context

class ArticulosListView(generic.ListView):
    model = Articulos
    form_class = ArticulosForm


class ArticulosDetailView(generic.DetailView):
    model = Articulos
    form_class = ArticulosForm
    
    def get_context_data(self, **kwargs):
        context = super(ArticulosDetailView, self).get_context_data(**kwargs)

        url = self.get_object()
        vendedores = Vendedores.objects.filter( articulo=url.pk)
        context.update({
            'vendedores': vendedores,
        })

        return context


class CorporationListView(generic.ListView):
    model = Corporation
    form_class = CorporationForm

class CorporationDetailView(generic.DetailView):
    model = Corporation
    form_class = CorporationForm

class MarcasListView(generic.ListView):
    model                   = Marcas
    form_class              = MarcasForm
    paginate_by             = 90
    

    def get_queryset(self):
        articles_from_all = Vendedores.objects.select_related('articulo')
        articles_from_all = articles_from_all.exclude(vendidoen__precio=0)
        articles_from_all = articles_from_all.exclude(vendidoen__error404=True)
        articles_from_all = articles_from_all.exclude(articulo__marca__es_marca=False)
        articles_from_all = articles_from_all.values('articulo__marca__pk').distinct().all()
        records  = Marcas.objects.filter(id__in=articles_from_all).filter(es_marca=True)
        return records
        # return Marcas.objects.filter(es_marca=True)
    
    def get_context_data(self, **kwargs):
        MinSuperCompara         = int(Settings.objects.get(key='MinSuperCompara').value)
        context                 = super().get_context_data(**kwargs)
        # marcas                  = Marcas.objects.filter(es_marca=True)
        marcas                  = self.get_queryset()

        params = self.request.GET.copy()
        if 'page' in params:
            del params['page']
            
        context['clean_params'] = params.urlencode()
        
        paginator = Paginator(marcas, self.paginate_by)
        page_number = self.request.GET.get('page')
        
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = None

        context['resumen'] = {
            'class': 'precios:brands',
            'MinSuperCompara': MinSuperCompara,
        }
        context["paginator"] =  paginator
        context["page_obj"] =  page_obj

        context["title"] =  "Marcas"
        context["cache"] =  "0 Min."
        context["beardcrums"] =  [
            {"Nombre": 'Marcas'},
        ]
        return context
   


class MarcasDetailView(generic.DetailView):
    model                   = Marcas
    form_class              = MarcasForm
    paginate_by             = int(Settings.objects.get(key='marcaPaginatorItemsPerPage').value)

    
    def get_queryset(self):
        return Marcas.objects.filter(es_marca=True)
       
    def get_context_data(self, **kwargs):
        momentos, supermercadoscount    = getMomentos(self.request)
        ExternalUrlPostUrl              = Settings.objects.get(key='ExternalUrlPostUrl').value
        messages.warning(self.request,  str(getMessage()))
        context                         = super().get_context_data(**kwargs)

        brand = self.kwargs['slug']
        marca = get_object_or_404(Marcas.objects.all(), slug=brand)
        if not marca.es_marca:
            reglas = Unifica.objects.filter(si_marca=marca, si_nombre=None, si_grados2=float(0))
            for regla in reglas:
                return redirect('precios:Marcas_detail', slug=regla.entonces_marca.slug)
        else:
            registrar_consulta(self.request, 'Marcas', marca.pk)
        
        orden = self.request.GET.get('order', 'nombre')  # 'nombre' es el valor por defecto
        # Recuperar los parámetros del filtro de la solicitud GET
        marca_filter    = self.request.GET.get('marca', None)
        grados_filter   = self.request.GET.get('grados', None)
        envase_filter   = self.request.GET.get('envase', None)
        medida_cant_filter = self.request.GET.get('medida_cant', None)
        color_filter    = self.request.GET.get('color', None)
        unidades_filter    = self.request.GET.get('unidades', None)
        
        params = self.request.GET.copy()
        if 'page' in params:
            del params['page']
            
        context['clean_params'] = params.urlencode()

        articulos = Articulos.objects.select_related('marca').filter(marca=marca)
        articulos = articulos.annotate(num_vendedores=Count('vendedores__vendidoen', filter=Q(vendedores__vendidoen__site__in=momentos, vendedores__vendidoen__precio__gt=0), distinct=True))
        if marca_filter:
            articulos = articulos.filter(marca_id=marca_filter)
        if grados_filter:
            articulos = articulos.filter(grados2=grados_filter)
        if envase_filter:
            articulos = articulos.filter(envase=envase_filter)
        if medida_cant_filter:
            articulos = articulos.filter(medida_cant__in=medida_cant_filter)
        if color_filter:
            articulos = articulos.filter(color__in=color_filter)
        if unidades_filter:
            articulos = articulos.filter(unidades__in=unidades_filter)


        articulos_dict, articulos_count, ofertas_count = generate_articulos_dict(articulos, momentos, 0, orden)

        filtro = generate_filters(articulos, '')

        # Utiliza Paginator si es necesario
        paginator = Paginator(articulos_dict, self.paginate_by)
        page_number = self.request.GET.get('page')
        
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = None

        context['resumen'] = {
            'articulos_count':articulos_count, 
            'ofertas_count': ofertas_count, 
            'supermercadoscount': supermercadoscount, 
            'brand': brand,
            'class': 'precios:brands_detail',
            'meta': '',
            'mensaje': '',
            'ExternalUrlPostUrl': ExternalUrlPostUrl
        }
        context["filtro"] =  filtro
        context["paginator"] =  paginator
        context["page_obj"] =  page_obj
        
        # context['articulos_dict'] = articulos_dict 
        context['articulos_dict'] = page_obj
        context['orden'] = orden 
        context["title"] =  marca.nombre
        context["cache"] =  "0 Min."
        context["beardcrums"] =  [
            {"Nombre": 'Marcas', 'url': '/precios/brands/'},
            {"Nombre": marca.nombre},
        ]
        return context

