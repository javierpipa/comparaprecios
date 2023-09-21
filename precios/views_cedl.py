from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django_json_ld.views import JsonLdDetailView
from django.db.models import Avg, Max, Min, Sum, Subquery, OuterRef, Count, Q

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
    registrar_consulta
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
    template_name = 'precios/articulos/detalle2.html'
    model           = Articulos
    queryset        = Articulos.objects.select_related('marca').all()

    # def get_queryset(self):
    #     return  get_object_or_404(Articulos, slug=self.kwargs["slug"])
    #     # return Articulos.objects.filter(id=self.articulo)

    # override context data
    def get_context_data(self, *args, **kwargs):
        context  = {}
        ExternalUrlPostUrl           = Settings.objects.get(key='ExternalUrlPostUrl').value
        momentos, supermercadoscount = getMomentos(self.request)
        print(momentos)

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
                articulos_dict.append({'articulo': particulo,'detalle': detalle})

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
    model = Marcas
    form_class = MarcasForm
    paginate_by = 50

    def get_queryset(self):
        return Marcas.objects.filter(es_marca=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        momentos, supermercadoscount  = getMomentos(self.request)
        ExternalUrlPostUrl      = Settings.objects.get(key='ExternalUrlPostUrl').value
        messages.warning(self.request,  str(getMessage()))
        context = super().get_context_data(**kwargs)

        brand = self.kwargs['slug']
        marca = get_object_or_404(Marcas.objects.all(), slug=brand)
        if not marca.es_marca:
            reglas = Unifica.objects.filter(si_marca=marca, si_nombre=None, si_grados2=float(0))
            for regla in reglas:
                return redirect('precios:Marcas_detail', slug=regla.entonces_marca.slug)
        else:
            registrar_consulta(self.request, 'Marcas', marca.pk)
        
        context['resumen'] = {
            'articulos_count':'articulos_count', 
            'ofertas_count': 'ofertas_count',  
            'supermercadoscount': supermercadoscount,
            'ExternalUrlPostUrl': ExternalUrlPostUrl ,
            'meta': 'meta',
        }
        articulos = Articulos.objects.select_related('marca').filter(marca=marca)
        articulos_dict  = []
        articulos_count = 0
        for particulo in articulos:
            detalle = Vendedores.objects\
            .filter(articulo=particulo.id).\
                filter(vendidoen__site__in=momentos).\
                exclude(vendidoen__precio__exact=0).\
                order_by('vendidoen__precio')\
                .distinct()
            if (len(detalle)) > 0 :
                articulos_count +=1
                ofertas = detalle.count()
                articulos_dict.append({'articulo': particulo,'detalle': detalle})

        context['articulos_dict'] = articulos_dict 

        
        context["title"] =  marca.nombre
        context["cache"] =  "0 Min."
        context["beardcrums"] =  [
            {"Nombre": 'Marcas', 'url': '/precios/brands/'},
            {"Nombre": marca.nombre},
        ]
        return context

