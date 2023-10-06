from django.contrib import admin
from django.utils.html import format_html


from django.urls import reverse
from django.utils.safestring import mark_safe

from django import forms

from django import forms
from precios.views import export_as_json
from precios.models import (
    Settings,
    Site, 
    Pages, 
    Campos,
    CamposEnSitio,
    SiteURLResults,
    SelectorCampo,
    PriceHistory,
    Marcas, 
    Articulos,
    Vendedores,
    MarcasSistema,
    Corporation,
    SiteMap,
    SelectorCampo,
    Countries,
    Regions,
    Cities,
    AreasDespacho,
    HorasDespacho,
    DiasSemana,
    MomentosDespacho,
    Unifica,
    Hello,
    ReemplazaPalabras,
    AllPalabras,
    Estadistica_Consulta,
    EstadisticasBlackList,
    Direccion,
    Horario_atencion,
    Breadcrumb,
    Breadcrumb_list

)
from django.contrib import admin
# from .models import   SiteURLResults

class TuModeloAdmin(admin.ModelAdmin):
    actions = [export_as_json]

# admin.site.register(SiteURLResults, TuModeloAdmin)


###  FORMS
class AreasDespachoForm(forms.ModelForm):
    class Meta:
        model = AreasDespacho
        fields = '__all__'

class MarcasAdminForm(forms.ModelForm):

    class Meta:
        model = Marcas
        fields = "__all__"

#### INLINE
class ConsultaInline(admin.TabularInline):
    model = Estadistica_Consulta
    extra = 0
    can_delete = False
    fields = ('clase_consultada', 'elemento_id', 'fecha', 'cantidad_vista', 'texto_busqueda')

class PagesEnSitioInline(admin.TabularInline):
    model = Pages
    extra = 0
    can_delete = False


class CamposEnSitioInline(admin.TabularInline):
    model = CamposEnSitio
    extra = 0
    can_delete = False

class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 0
    can_delete = True
    fields = ('OldDate','Oldprecio')
    readonly_fields = ('OldDate',)

class SelectorCampoInline(admin.TabularInline):
    model = SelectorCampo
    extra = 0
    can_delete = True

class VendedoresInline(admin.TabularInline):
    model = Vendedores
    fields = ('articulo', 'vendidoen', 'precio')
    readonly_fields=('articulo','vendidoen' , 'precio')

    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

class ArticulosxmarcaInline(admin.TabularInline):
    model = Articulos
    extra = 0
    can_delete = False
    fields = ('nombre', 'medida_um', 'medida_cant')
    readonly_fields=('nombre', 'medida_um', 'medida_cant')

class MomentosDespachoInline(admin.TabularInline):
    model = MomentosDespacho
    extra = 0
    can_delete = True

class DireccionInline(admin.TabularInline):
    model = Direccion
    extra = 0
    can_delete = True

class Horario_atencionInline(admin.TabularInline):
    model = Horario_atencion
    extra = 0
    can_delete = True

# #### FIN INLINE


class SiteAdmin(admin.ModelAdmin):
    list_display = (

        "siteName",
        "account",
        "siteURL",
        "siteSearch",
        "crawler",
        "productSearchEnabled",
        "last_scan",
        "urlCount",
        "es_ean13"
    )

    readonly_fields = ('last_scan',)
    fieldsets = [
 
        (
            "Header",
            {
                "fields": [
                    "account",
                    ("enable",
                    "use_his_image",),
                    (
                        "corporacion",
                        "siteName",
                        "siteURL",
                    ),
                    "siteSearch",
                    "sitemap_url",
                    "icon_image",
                    ("theparser",
                    "crawler",),
                    "last_scan",
                    "es_ean13",
                    "reclamos_url",
                    "notas"
                ]
            }
        ),
        (
            "Cobertura",{
                "fields": [
                    "cobertura_url",
                    "desp_monto_minimo",
                ]
            }
        ),
        (
            "Searching",
            {
                "fields": [
                    "product_url",
                    (
                    "siteSearchEnabled",
                    "productSearchEnabled",
                    "listNeedsPgDn",
                    ),
                    "url_suffix",
                    (
                    "product_category",
                    "product_product",
                    "product_palabras_evitar",
                    ),
                    
                ]
            }
        ),
        (
            "Pageing",
            {
                "fields": [
                    (
                        "page_parameter",
                        "page_suffix"),
                ]
            }
        ),
        (
            "Config",
            {
                "fields": [
                    (
                        "agregaSiteURL",
                        "allLinksInOnePage",
                        "listHasClick",
                    )
                ]
            }
        ),
        
    ]
    inlines = [DireccionInline,]
    list_filter = ('enable', 'corporacion','crawler', 'siteSearch', 'productSearchEnabled')

class PagesAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'last_scan',)
    list_display = (
        "site",
        "page",
        "enabled",
        "last_scan",
        "maxPagesFound",
        "lastPageIndexed",
        "got_404"
    )
    list_filter = ('site', 'enabled')

class CamposAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "donde",
        "campoQueGraba",
        "es_multiple",
        "es_click",
        "enabled",
        "guardar_historico"
    )
    list_filter = ('donde', )

class CamposEnSitioAdmin(admin.ModelAdmin):
    list_display = (
        "site",
        "campo",
        "enabled",
        "hijoDe",
        "my_order",
        "evita",
        "selectorErrorCount",
        "selectorCount",
        "printit",
    )
    fieldsets = [
 
        (
            "Header",
            {
                "fields": [
                    "site",
                    "campo",
                    "enabled",
                    "printit",
                    "evita",
                    "hijoDe",
                    "my_order",
                    
                ]
            }
        ),
        
        (
            "notes",
            {
                "fields": [
                    "notas",
                    
                ]
            }
        ),
    ]
    list_filter = ('enabled','site', 'campo__donde', 'campo' )
    inlines = [SelectorCampoInline]

class SiteURLResultsAdmin(admin.ModelAdmin):
    actions = [export_as_json]
    list_display = (
        "site",
        "nombre",
        "marca",
        "artRef",
        "stock",
        "updated",
        "unidades",
        "medida_um",
        "medida_cant",
        # "precio_cantidad",
        "precio",
        "HistoryCount",
        # "secondsToGet",
        "error404",
    )
    readonly_fields = ('created', 'updated','reglas',)
    list_filter = ('site','error404','updated')
    inlines = [PriceHistoryInline]
    search_fields= ["url"]

class ResultsAdmin(admin.ModelAdmin):
    list_display = (
        "URLResult",
        "campoEnSitio",
        "valor",
        "updated"
    )
    list_filter = ('URLResult__site', 'campoEnSitio__campo', 'es_error')
    search_fields = ["valor"]

    fieldsets = [
 
        (
            "Header",
            {
                "fields": [
                    "URLResult",
                    "campoEnSitio",
                    "valor",
                    "es_error"
                ]
            }
        ),
    ]

class PriceHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ('OldDate','FromResult')
    list_display = (
        "FromResult",
        "Oldprecio",
        "OldDate"
    )
    list_filter = ('FromResult__site','OldDate')

class ArticulosAdmin(admin.ModelAdmin):
    list_display = (
        "marca",
        "nombre",
        "resultsCount",
        "ean_13",
        'grados2',
        "medida_cant",
        "medida_um",
        'unidades',
        'envase',
        "get_price",
        'talla',
    )
    inlines = [VendedoresInline,]
    search_fields= ["nombre"]
    

class MarcasAdmin(admin.ModelAdmin):
    form = MarcasAdminForm

    list_display = (
        "id",
        "nombre",
        "slug",
        "rulesCount",
        "resultsCount",
        "es_marca"
    )
    search_fields= ["nombre"]
    list_filter = ('unificado','es_marca')
    inlines = [ArticulosxmarcaInline,]


class VendedoresAdmin(admin.ModelAdmin):
    list_display = (
        "articulo",
        "vendidoen"
    )
    readonly_fields = ('articulo', 'vendidoen')

class SiteMapAdmin(admin.ModelAdmin):
    list_display = (
        "site",
        "loc",
        "sitemap_type",
        "get_url",
        "lastmod"
    )
    readonly_fields = ('created', )
    list_filter = ('site', 'sitemap_type','get_url')

class MarcasSistemaAdmin(admin.ModelAdmin):
    search_fields= ["nombre"]

class SelectorCampoAdmin(admin.ModelAdmin):
    list_display = (
        "campo",
        "selector",
        "my_order",
        "error_count",
        "que_busca",
        "que_obtiene",

    )
    search_fields= ["nombre"]


class CitiesAdmin(admin.ModelAdmin):
    list_display = (
        "country",
        "region",
        "name",
        "cut",
        "superficie",
        "poblacion",
        "latitude",
        "longitude",

    )
    search_fields= ["name"]

class AreasDespachoAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "Header",
            {
                "fields": [
                    "site",
                    "area",
                    "datos_confiables",
                    ("monto_minimo_compra",
                    "valor_despacho",),
                    ("dias_para_despacho",
                    "dias_habiles",),
                ]
            }
        ),
        # (
        #     "No es depacho",
        #     {
        #         "fields": [
        #             "no_es_despacho",
        #             "direccion",
        #         ]
        #     }
        # ),
        
        (
            "Comunas",
            {
                "fields": [
                    "comuna",
                ]
            }
        ),
    ]
    
    filter_horizontal = ('comuna',)
    list_display = (
        "site",
        "area",
        "datos_confiables",
        "monto_minimo_compra",
        "valor_despacho",
        "dias_para_despacho",
        "dias_habiles",
        "comunasCount",
        # "no_es_despacho",
        # "direccion",
        
    )
    inlines = [MomentosDespachoInline]
    list_filter = ('site', 'dias_habiles')
   
    form = AreasDespachoForm
    list_filter = ['site']

    

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj=obj, **kwargs)

    #     if obj and not obj.no_es_despacho:
    #         form.base_fields['direccion'].widget.attrs['style'] = 'display:none;'
    #         self.inlines = []  # Oculta las inlines cuando no_es_despacho es True
    #     else:
    #         self.inlines = [MomentosDespachoInline]  # Vuelve a mostrar las inlines si no_es_despacho es False

    #     return form

    # def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
    #     context['adminform'].form.fields['direccion'].widget.attrs['class'] = 'direccion-field'
    #     context['add_url'] = reverse('admin:%s_%s_add' % (
    #         self.model._meta.app_label, self.model._meta.model_name))
    #     return super().render_change_form(request, context, add, change, form_url, obj)


class MomentosDespachoAdmin(admin.ModelAdmin):
    list_display = (
        "get_dias",
        "get_horas"

    )
    search_fields= ["dia"]
    # inlines = ('AreasDespachsInline',)

class RegionsAdmin(admin.ModelAdmin):
    list_display = (
        "country",
        "name",
        "code"
    )
class AllPalabrasAdmin(admin.ModelAdmin):
    list_display = (
        "palabra",
        "tipo",
        "contador",
    )
    search_fields= ["palabra"]
    list_filter = ('tipo',)

class UnificaAdmin(admin.ModelAdmin):
    # def cont(self,object) -> str:
    #     return format_html('<span style="color:green;">{}</span>', object.contador)
    
    # def cont(self,object) -> str:
    #     result =  (object.free + object.locked) * object.usd_price 
    #     return format_html('{percent:,.2f}'.format(percent=result))

    list_display = (
        "contador",
        'tipo',
        'auto',
        'si_mrc_lst',
        'si_nombre',
        "si_grd",
        "si_mdd",
        "si_udd",
        "si_env",
        "si_talla",
        "etc_mrc_lst",
        "entonces_nombre",
        "etc_grd",
        "etc_mdd",
        "etc_udd",
        "etc_env",
        "etc_talla",
    )
    list_display_links = ["si_nombre"]
    list_filter = ('automatico' , 'tipo' ,'si_marca','entonces_marca')
    search_fields= ["si_nombre", "entonces_nombre"]
    fieldsets = [
        (
            "Si - Entonces",
            {
                "fields": [
                    ("si_marca", "entonces_marca", ),
                    ("si_nombre", "entonces_nombre",),
                    ("si_grados2", "entonces_grados2", ),
                    ("si_medida_cant", "entonces_medida_cant",),
                    ("si_unidades", "entonces_unidades",),
                    ("si_envase", "entonces_envase",),
                ]
            }
        ),
        (
            "Estadisticas",
            {
                "fields": [
                    "contador",
                    "automatico",
                    "tipo",
                ]
            }
        )
    ]

class ReemplazaPalabrasAdmin(admin.ModelAdmin):
    list_display = (
        "palabra",
        'reemplazo',
        'contador',
    )
    search_fields= ["palabra", "reemplazo"]
class EstadisticasBlackListAdmin(admin.ModelAdmin):
    list_display = ('agente', 'no_contabilizar', 'mostrar_consultas')

    def mostrar_consultas(self, obj):
        consultas = Estadistica_Consulta.objects.filter(clase_consultada=obj.agente)
        return ', '.join(str(consulta) for consulta in consultas)

    mostrar_consultas.short_description = 'Consultas asociadas'

     

class Estadistica_ConsultaAdmin(admin.ModelAdmin):
    list_display = (
        "clase_consultada",
        'elemento_id',
        'fecha',
        'cantidad_vista'
    )
    list_filter = ('clase_consultada' ,)

class DireccionAdmin(admin.ModelAdmin):
    list_display    = ('site', 'direccion', 'comuna' )
    list_filter     = ('site' , )
    inlines = [Horario_atencionInline]
    


admin.site.register(Settings)
admin.site.register(Site, SiteAdmin)
admin.site.register(Pages, PagesAdmin)
admin.site.register(Campos, CamposAdmin)
admin.site.register(CamposEnSitio, CamposEnSitioAdmin)
admin.site.register(SiteURLResults, SiteURLResultsAdmin)
admin.site.register(PriceHistory,PriceHistoryAdmin)


admin.site.register(Marcas,MarcasAdmin)
admin.site.register(Articulos,ArticulosAdmin)
admin.site.register(Vendedores,VendedoresAdmin)

admin.site.register(MarcasSistema,MarcasSistemaAdmin)
admin.site.register(Corporation)
admin.site.register(SiteMap,SiteMapAdmin)
admin.site.register(SelectorCampo, SelectorCampoAdmin)

admin.site.register(Countries)
admin.site.register(Regions,RegionsAdmin)
admin.site.register(Cities,CitiesAdmin)

admin.site.register(AreasDespacho,AreasDespachoAdmin)


admin.site.register(HorasDespacho)
admin.site.register(DiasSemana)
admin.site.register(MomentosDespacho,MomentosDespachoAdmin)
admin.site.register(Unifica, UnificaAdmin)
admin.site.register(ReemplazaPalabras,ReemplazaPalabrasAdmin)
admin.site.register(AllPalabras, AllPalabrasAdmin)

admin.site.register(Estadistica_Consulta, Estadistica_ConsultaAdmin)
admin.site.register(EstadisticasBlackList, EstadisticasBlackListAdmin)

admin.site.register(Direccion, DireccionAdmin)
admin.site.register(Horario_atencion)

admin.site.register(Breadcrumb)
admin.site.register(Breadcrumb_list)

admin.site.register(Hello)