from django.db import models
from django.utils import timezone
from django.urls import reverse

from decimal import Decimal


from django_extensions.db.fields import AutoSlugField
from django.utils.translation import gettext_lazy as _
from django.db.models import CharField
from django.utils.http import urlencode

from django.core.validators import MinLengthValidator

from typing import List
from django.utils.html import format_html


from cms.models.pluginmodel import CMSPlugin
from django.contrib import admin
import unidecode
from meta.models import ModelMeta
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

class Hello(CMSPlugin):
    guest_name = models.CharField(max_length=50, default='Guest')


class DIAS_SEMANA(models.TextChoices):
    LUNES        = "Lunes"
    MARTES       = "Martes"
    MIERCOLES    = "Miercoles"
    JUEVES       = "Jueves"
    VIERNES      = "Viernes"
    SABADO       = "Sabado"
    DOMINGO      = "Domingo"

class META_FIELDS(models.TextChoices):
    NONE        = "None"
    CHARSET     = "charset"
    NAME        = "name"
    PROPERTY    = "property"

class DONDESEUSA(models.TextChoices):
    EN_LISTADO          = "En listado"              # En listado de productos
    EN_PRODUCTO         = "En producto"             # En pagina del producto
    DETALLE_EN_LISTADO  = "Detalle en listado"      # Innfo del producto en listado de productos

class SELECTOR(models.TextChoices):
    XPATH        = "xpath"
    CSS_SELECTOR = "css selector"
    META         = "meta"
    NINGUNO      = 'ninguno'
    VALORFIJO    = 'valorfijo'

class THEPARSER(models.TextChoices):
    HTML_PARSER  = "html.parser"
    LXML         = "lxml"
    HTM5LIB      = "html5lib"

class PAGECRAWLER(models.TextChoices):
    BEAUTIFULSOUP  = "BeautifulSoup"
    SELENIUM       = "Selennium"
    NINGUNO        = "Ninguno"

class TIPOPALABRA(models.TextChoices):
    # NADA           = ""
    INUTIL         = "Inútiles"
    UMEDIDA        = "Unidades de medida"
    SUJIFO_NOMBRE  = "Sufijos de nombre"
    UNIDAD         = "Unidades"
    PACKS          = "Packs"
    TALLA          = "Tallas"
    COLOR          = "Colores"
    ENVASE         = "Envases"
    
    
class Estadistica_Consulta(models.Model):
    clase_consultada    = models.CharField(max_length=100)
    elemento_id         = models.PositiveIntegerField()
    fecha               = models.DateField()
    cantidad_vista      = models.PositiveIntegerField(default=0)
    texto_busqueda      = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Estadistica Consultas'
        verbose_name_plural = 'Estadisticas de Consultas'
        ordering = ("clase_consultada","fecha")
        indexes = [
            models.Index(fields=['clase_consultada', 'elemento_id']),
            models.Index(fields=['fecha']),
        ]
    
    def __str__(self):
        return "{0}: {1}".format(self.clase_consultada, self.elemento_id)
        
class EstadisticasBlackList(models.Model):
    agente = models.CharField(max_length=250, unique=True)
    no_contabilizar = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Estadisticas Black List'
        verbose_name_plural = 'Estadisticas Black List'

    def __str__(self):
        return self.agente
    
class Settings(models.Model):
    """
    Defined Settings
    """

    key         = models.CharField('Key', max_length=50, null=False, blank=False, unique=True)
    value       = models.CharField('Value', max_length=80)
    valor_data  = models.TextField(default='')
    description = models.TextField('Description', null=True, blank=True)

    __unicode__ = lambda self: u'%s = %s' % (self.key, self.value)

    def __str__(self):
        return "{0}: {1}".format(self.pk, self.key)

    class Meta:
        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'
        app_label = 'precios'


class Corporation(models.Model):
    nombre              = models.CharField(max_length=250, null=False, blank=False, unique=True)
    notas               = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Corporarcion'
        verbose_name_plural = 'Corporarciones'
        app_label = 'precios'

    def get_absolute_url(self):
        return reverse("precios:Corporation_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("precios:Corporation_update", args=(self.pk,))


class Site(ModelMeta,models.Model):
    """
    web Site
    """
    class SITESEARCHBY(models.TextChoices):
        NONE = "none"
        CRAWLER = "crawler"
        SITEMAP = "sitemap"

    account             = models.ForeignKey(to="members.Account", on_delete=models.PROTECT, blank=True, null=True, default=5)
    corporacion         = models.ForeignKey(Corporation, on_delete=models.SET_DEFAULT, default=6,help_text='Grupo de empresas')
    siteName            = models.CharField(max_length=250, blank=False, null=False, help_text='Nombre del sitio')
    siteURL             = models.CharField(max_length=250, help_text='URL del sitio')
    agregaSiteURL       = models.BooleanField(default=True, help_text='Agrega SiteURL a las URL de cada producto.')
    allLinksInOnePage   = models.BooleanField(default=True, help_text='Todos los productos en una pagina. No tiene Next Page.')
    siteSearchEnabled   = models.BooleanField(default=True)
    siteSearch          = models.CharField(
        max_length=20, choices=SITESEARCHBY.choices, default=SITESEARCHBY.NONE, help_text='Obtiene URL de productos usando...'
    )
    productSearchEnabled= models.BooleanField(default=True)
    last_scan           = models.DateTimeField(auto_now=True,auto_now_add=False)
    listHasClick        = models.BooleanField(default=True)
    listNeedsPgDn       = models.BooleanField(default=False, help_text='El listado de prroductos necesita descender de a poco')
    theparser           = models.CharField(
        max_length=20, choices=THEPARSER.choices, default=THEPARSER.HTML_PARSER, help_text='Este campo es utilizado en ?'
    )
    crawler           = models.CharField(
        max_length=20, choices=PAGECRAWLER.choices, help_text='Scan pages with'
    )
    url_suffix          = models.CharField(max_length=250, blank=True, null=True)
    page_parameter      = models.CharField(max_length=50, blank=True, null=True, default="?page=")
    page_suffix         = models.CharField(max_length=50, blank=True, null=True, default="")
    notas               = models.TextField(default='', blank=True, null=True)
    sitemap_url         = models.URLField(default='', blank=True, null=True , help_text='URL del sitemap')
    enable              = models.BooleanField(default=True)
    actualizando        = models.CharField(max_length=50, blank=True, null=True, default="")
    icon_image          = models.ImageField('Menu Icon Image',
                                      upload_to = 'site_icons/',
                                      blank=True,null=True)
    cobertura_url       = models.URLField(max_length=600,default='', blank=True, null=True , help_text='URL de coberturas')
    es_ean13            = models.BooleanField(default=False, help_text="Sitio utiliza ID como EAN13")
    reclamos_url        = models.URLField(max_length=600,default='', blank=True, null=True , help_text='URL de reclamos')
    product_url         = models.URLField(max_length=400,default='', blank=True, null=True , help_text='URL de producto debe comenzar con')
    
    product_category    = models.CharField(max_length=250, blank=True, null=True, help_text="Parte de URL que identifica categoria")
    product_product     = models.CharField(max_length=250, blank=True, null=True, help_text="Parte de URL que identifica un producto")
    product_palabras_evitar = models.CharField(max_length=250, blank=True, null=True, help_text="Parte de URL para no escanear como map= _q= separar por coma")
    use_his_image       = models.BooleanField(default=True, help_text="Muestra imagen de la URL del sitio, si no, el articulo usa imagen de otro sitio")
    precios_con_iva     = models.BooleanField(default=True, help_text="Hay pocos sitios que entregan sus precios SIN IVA, default = True")
    obtiene_categorias  = models.BooleanField(default=False, help_text="Las categorias de los articulos de estos sitios. En principio usar jumbo solamente.")

    ### Area despacho
    desp_monto_minimo  = models.IntegerField(default=0, help_text="El mínimo para realizar una compra con despacho a domicilio es de")

    ## Planes
    # plan               = models.ForeignKey(Plan, on_delete=models.PROTECT, blank=True, null=True, default=1)
    _metadata = {
        'title': 'siteName',
        'description': 'notas',
        'image': 'get_meta_image',
    }
    def get_meta_image(self):
        if self.icon_image:
            return self.icon_image.url


    def __str__(self):
        return self.siteName

    def get_absolute_url(self):
        return reverse("precios:supermercado", args=(self.pk,))

    def get_update_url(self):
        return reverse("precios:Site_update", args=(self.pk,))


    @property
    def urlCount(self) -> int:
        return SiteURLResults.objects.filter(site=self).count()

    @property
    def pageCount(self) -> int:
        return Pages.objects.filter(site=self).count()

    @property
    def camposEnnSitioCount(self) -> int:
        return CamposEnSitio.objects.filter(site=self, enabled=True).count()

    class Meta:
        verbose_name = 'Site'
        verbose_name_plural = 'Sites'
        app_label = 'precios'



######### Areas geograficas

class Countries(models.Model):
    name            = models.CharField(max_length=50, blank=False, null=False, default="", unique=True)

    class Meta:
        """Meta definition for Countries."""

        verbose_name = "Pais"
        verbose_name_plural = "Paises"

    def __str__(self):
        """Unicode representation of Person."""
        return "%s" % self.name

class Regions(models.Model):
    country         = models.ForeignKey(Countries, on_delete=models.CASCADE, default=1)
    name            = models.CharField(max_length=50, blank=False, null=False, default="")
    code            = models.CharField(max_length=5, blank=True, null=True, default="")

    class Meta:
        """Meta definition for Regions."""

        verbose_name = "Region"
        verbose_name_plural = "Regiones"
        unique_together = [['country', 'name']]

    def __str__(self):
        """Unicode representation of Regions."""
        return "{0}: {1} ".format( self.country, self.name)

class Cities(models.Model):
    country         = models.ForeignKey(Countries, on_delete=models.CASCADE, default=1)
    region          = models.ForeignKey(Regions, on_delete=models.CASCADE, default=1)
    name            = models.CharField(max_length=50, blank=False, null=False, default="")
    cut             = models.IntegerField(default=0,null=True , help_text="Código Único Territorial")
    superficie      = models.IntegerField(default=0,null=True , help_text="Superficie (km²)")
    poblacion       = models.IntegerField(default=0,null=True , help_text="Población 2020")
    latitude        = models.FloatField(default=0)
    longitude       = models.FloatField(default=0)
    
    @property
    def supermercado_count(self):
        return AreasDespacho.objects.filter(comuna=self, site__enable=True).count()
    
    @property
    def supermercados(self):
        areas_despacho = AreasDespacho.objects.filter(comuna=self)
        nombres_supermercados = []
        for area in areas_despacho:
            if area.site.enable:
                url_supermercado = f"/precios/supermercado/{area.site.pk}/"
                nombres_supermercados.append(f'<a href="{url_supermercado}">{area.site.siteName}</a>')
        return nombres_supermercados
  
    class Meta:
        """Meta definition for Cities."""

        verbose_name = "Comuna"
        verbose_name_plural = "Comunas"
        unique_together = [['country', 'region','name']]
        ordering = ("region","name")

    def __str__(self):
        """Unicode representation of Cities."""
        return "{0}: {1} {2}".format(  self.name, self.region, self.country)
        
######### FIN Areas geograficas ########

######### Areas de despacho y su costo
class HorasDespacho(models.Model):
    inicio                  = models.TimeField(auto_now=False, auto_now_add=False)
    termino                 = models.TimeField(auto_now=False, auto_now_add=False)

    class Meta:
        verbose_name = 'Hora de despacho'
        verbose_name_plural = 'Horas de despacho'
        unique_together = [['inicio', 'termino']]
        ordering = ("inicio", "termino")

    def __str__(self):
        """Unicode representation of Areas de despacho."""
        return "{0} - {1} ".format(  self.inicio, self.termino)

class DiasSemana(models.Model):
    nombre              = models.CharField(max_length=250, unique=True)
    my_order            = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )
    class Meta:
        verbose_name = 'Dia de la semana'
        verbose_name_plural = 'Dias de la semana'
        ordering = ("my_order",)

    def __str__(self):
        """Unicode representation of Dias de la Semana."""
        return "{0}".format(  self.nombre)

class Direccion(models.Model):
    site                    = models.ForeignKey(Site, on_delete=models.CASCADE, default=1)
    direccion               = models.CharField(max_length=300, blank=True, null=True, help_text="Dirección")
    comuna                  = models.ForeignKey(Cities, on_delete=models.CASCADE, default=1)

    class Meta:
        verbose_name = 'Direccion'
        verbose_name_plural = 'Direcciones'
    
class Horario_atencion(models.Model):
    direccion     = models.ForeignKey(Direccion, on_delete=models.CASCADE, default=1)
    dia           = models.ManyToManyField(DiasSemana)
    horario       = models.ManyToManyField(HorasDespacho)

    class Meta:
        verbose_name = 'Horario atencion'
        verbose_name_plural = 'Horarios de atencion'

    def __str__(self):
        """Unicode representation of Momentos de despacho."""
        return "{0} - {1}".format(  self.dia, self.horario)

    def get_dias(self):
        return "\n".join([d.nombre for d in self.dia.all()])

    def get_horas(self):
        return "\n".join([str(h.inicio)+'-'+str(h.termino) for h in self.horario.all()])
    

class AreasDespacho(models.Model):
    site                    = models.ForeignKey(Site, on_delete=models.CASCADE, default=1)
    area                    = models.CharField(max_length=50, blank=False, null=False, default="")
    comuna                  = models.ManyToManyField(Cities)
    monto_minimo_compra     = models.IntegerField(default=0,null=True , help_text="Monto desde el cual se cobra el siguiente valor del despacho")
    valor_despacho          = models.IntegerField(default=0,null=True , help_text="Costo del despacho")
    dias_para_despacho      = models.IntegerField(default=0,null=True , help_text="Dias que demora despacho")
    dias_habiles            = models.BooleanField(default=True, help_text="Dias Habiles = True")
    datos_confiables        = models.BooleanField(default=True, help_text="")
    
    def __str__(self):
        """Unicode representation of Dias de la Semana."""
        return "{0}".format(  self.site)

    @property
    def comunasCount(self) -> int:
        return self.comuna.count()

    class Meta:
        verbose_name = 'Area de despacho'
        verbose_name_plural = 'Areas de despacho'


class MomentosDespacho(models.Model):
    areaDespacho  = models.ForeignKey(AreasDespacho, on_delete=models.CASCADE, default=1)
    dia           = models.ManyToManyField(DiasSemana)
    horario       = models.ManyToManyField(HorasDespacho)

    class Meta:
        verbose_name = 'Momento del despacho'
        verbose_name_plural = 'Momentos de despacho'

    def __str__(self):
        """Unicode representation of Momentos de despacho."""
        return "{0} - {1}".format(  self.dia, self.horario)

    def get_dias(self):
        return "\n".join([d.nombre for d in self.dia.all()])

    def get_horas(self):
        return "\n".join([str(h.inicio)+'-'+str(h.termino) for h in self.horario.all()])

######### FIN Areas de despacho y su costo

class SiteMap(models.Model):
    site            = models.ForeignKey(Site, on_delete=models.CASCADE, default=1)
    loc             = models.URLField(max_length=600,default='', blank=True, null=True , help_text='URL del sitemap')
    sitemap_type    = models.CharField(max_length=20, blank=True, null=True, default="")
    get_url         = models.BooleanField(default=False)
    created         = models.DateTimeField(auto_now_add=True)
    lastmod         = models.DateField(auto_now=True,auto_now_add=False)

    def __str__(self):
        return "{0}: {1} ".format( self.site, self.loc)

    class Meta:
        verbose_name = 'SiteMap'
        verbose_name_plural = 'SiteMaps'
        index_together = [
            ("site", "loc"),
        ]
        unique_together = [['site', 'loc']]

class Pages(models.Model):
    """
    web Site Pages to search products
    """
    site            = models.ForeignKey(Site, on_delete=models.CASCADE, default=1)
    page            = models.CharField(max_length=250)
    enabled         = models.BooleanField(default=True)
    got_404         = models.BooleanField(default=False)
    lastPageIndexed = models.IntegerField(default=0)
    maxPagesFound   = models.IntegerField(default=0)
    created         = models.DateTimeField(auto_now_add=True)
    last_scan       = models.DateTimeField(auto_now=True,auto_now_add=False)

    def __str__(self):
        # return self.page
        return "{0}: {1} ".format( self.site, self.page)

    # @property
    def FaltaBuscar(self) -> bool:
        if self.maxPagesFound == 0 or self.maxPagesFound > self.lastPageIndexed:
            return True
        else:
            return False

    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'
        index_together = [
            ("site", "page"),
        ]
        unique_together = [['site', 'page']]


class Campos(models.Model):
    """
    Campos que se buscaran en los sitios.
    Se utiliza BeautifulSoup
    """
    nombre              = models.CharField(max_length=250)
    donde = models.CharField(
        max_length=20, choices=DONDESEUSA.choices, default=DONDESEUSA.EN_LISTADO, help_text='Este campo es utilizado en ?'
    )
    campoQueGraba       = models.CharField(max_length=20, default='')
    es_multiple         = models.BooleanField(default=True)
    es_click            = models.BooleanField(default=True)
    enabled             = models.BooleanField(default=True)
    guardar_historico   = models.BooleanField(default=False)
    
    def __str__(self):
        # return "{0}: {1} ".format( self.nombre, self.donde)
        return "{0}".format( self.nombre)

    class Meta:
        verbose_name = 'Campo'
        verbose_name_plural = 'Campos'

class CamposEnSitio(models.Model):
    """
    Campos que se buscaran en los sitios.
    Se utiliza BeautifulSoup
    """
    site                = models.ForeignKey(Site, on_delete=models.CASCADE, default=1)
    campo               = models.ForeignKey(Campos, on_delete=models.CASCADE, default=1)
    
    evita               = models.CharField(max_length=650, blank=True, null=True,  help_text='Que clase evita en listados')
    printit             = models.BooleanField(default=False)
   
    enabled             = models.BooleanField(default=True)

    notas               = models.TextField(default='', blank=True, null=True)
    hijoDe              = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)
    my_order            = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )


    @property
    def selectorCount(self) -> int:
        return SelectorCampo.objects.filter( campo=self).count()

    @property
    def selectorErrorCount(self) -> int:
        selectores = SelectorCampo.objects.filter( campo=self)
        errores = 0
        for selector in selectores:
            errores = errores + selector.error_count

        return errores

    def __str__(self):
        return "{1} - {0}".format(self.campo, self.site)

    class Meta:
        verbose_name = 'Campo en sitio'
        verbose_name_plural = 'Campos en sitio'
        ordering = ("site","campo","my_order")


class LowerField(models.CharField):

    def get_prep_value(self, value):
        return str(value).lower()

class FixTerm(models.Model):
    """
    Campos que se buscaran en los sitios.
    Se utiliza BeautifulSoup
    """
    campo               = models.ForeignKey(CamposEnSitio, on_delete=models.CASCADE, default=1)
    que_busca           = LowerField(max_length=100, help_text='artesanos de cochiguaz')
    reemplazacon        = LowerField(max_length=100, help_text='Artesanos del Cochiguaz',default='', blank=True, null=False)

    def __str__(self):
        return "{0}: {1} ".format( self.campo, self.que_busca)


    class Meta:
        verbose_name = 'FixTerm'
        verbose_name_plural = 'FixTerms'
        index_together = [
            ( "campo", "que_busca"),
        ]
        unique_together = [['campo', 'que_busca']]


class SelectorCampo(models.Model):
    """
    Selectores de un campo de un sitio
    
    """
    campo               = models.ForeignKey(CamposEnSitio, on_delete=models.SET_DEFAULT,  default=1)
    
    selector            = models.CharField(
        max_length=20, 
        choices=SELECTOR.choices, 
        default=SELECTOR.XPATH, 
        help_text='como selecciona ?'
    )

    my_order            = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    meta_opcion          = models.CharField(
        max_length=20, 
        choices=META_FIELDS.choices, 
        default=META_FIELDS.NONE, 
        help_text='Meta que ?'
    )
    
    que_busca           = models.CharField(max_length=650, blank=True, help_text='c-block.c-product.js-product-single o product:retailer_item_id. Si es FIJO, introduzca valor a guardar')
    
    printit             = models.BooleanField(default=False)
    removeChars         = models.CharField(max_length=650, blank=True, null=True)
    que_obtiene         = models.CharField(
        max_length=650, 
        blank=True, 
        null=True,
        default="text"
    )

    split_return_by     = models.CharField(max_length=6, blank=True, null=True)
    split_get_element   = models.IntegerField(default=0)

    error_count         = models.IntegerField(default=0)
    error_description   = models.CharField(max_length=650, blank=True, null=True)

    def __str__(self):
        return "{0}: {1} ".format( self.campo, self.selector)
        # return "{0}".format( self.nombre)


    class Meta:
        verbose_name = 'Selector de campo'
        verbose_name_plural = 'Selectores de campo'
        index_together = [
            ("campo", "my_order"),
        ]
        unique_together = [['campo', 'selector', 'my_order']]


def my_slugify_function(content):
    retorna = content.replace('_', '-').lower()
    retorna = retorna.replace(' ', '-')
    retorna = retorna.replace('/', '-')
    retorna = unidecode.unidecode(retorna)
    return retorna

class MarcasSistema(models.Model):
    nombre              = models.CharField(max_length=250, unique=True)
    
    def __str__(self):
        return "{0}".format( self.nombre)
    class Meta:
        verbose_name = 'Marca sistema'
        verbose_name_plural = 'Marcas sistema'
        ordering = ("nombre",)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()
        return super(MarcasSistema, self).save(*args, **kwargs)



class Marcas(models.Model):
    nombre              = models.CharField(max_length=250, validators=[MinLengthValidator(2)], unique=True, db_index=True, blank=False, null=False)
    slug                = AutoSlugField(populate_from='nombre', editable=True, unique=True, db_index=True, slugify_function=my_slugify_function)
    unificado           = models.BooleanField(default=False)
    es_marca            = models.BooleanField(default=True)
    created             = models.DateTimeField(editable=False,default=timezone.now)
    grados              = models.BooleanField(default=False)
    talla               = models.BooleanField(default=False)
    numero              = models.BooleanField(default=False)

    @property
    def rulesCount(self) -> int:
        return Unifica.objects.filter(si_marca=self).count() + Unifica.objects.filter(entonces_marca=self).count() 
      
    # @property
    def resultsCount(self) -> int:
        return Articulos.objects.filter(marca=self).count()

    @property
    def vendedoresList(self) -> list:
        arr_vendedores = []
        if Articulos.objects.filter(marca=self).exists():
            for art in Articulos.objects.filter(marca=self):
                sitios = Vendedores.objects.filter(articulo=art).values_list('vendidoen__site', flat=True)
                for sitio in sitios:
                    arr_vendedores.append(sitio)
        
        return set(arr_vendedores)


    def __str__(self):
        return "{0}".format( self.nombre)
    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ("nombre",)

    def get_absolute_url(self):
        base_url = reverse('precios:home')
        query_string =  urlencode({'marca': self.id})
        return f"{base_url}?{query_string}"
        # return reverse("precios:brands_detail", args=(self.slug,))

    def get_update_url(self):
        return reverse("precios:Marcas_update", args=(self.pk,))

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.lower()

class TaggedArticles(TaggedItemBase):
    content_object = models.ForeignKey('Articulos', on_delete=models.CASCADE)
    class Meta:
        indexes = [
            models.Index(fields=['tag_id'], name='tag_id_idx'),  # Define un índice en la columna tag_id
        ]


class TaggedUrls(TaggedItemBase):
    content_object = models.ForeignKey('SiteURLResults', on_delete=models.CASCADE)


class Articulos(ModelMeta, models.Model):
    """
    Articulos
    """
    nombre_original     = models.CharField(max_length=350, default='')
    nombre              = models.CharField(max_length=350)
    marca               = models.ForeignKey(Marcas, on_delete=models.CASCADE, default=1)
    medida_um           = models.CharField(max_length=20, default='')
    medida_cant         = models.FloatField(default=0)
    unidades            = models.IntegerField(default=0)
    dimension           = models.CharField(max_length=50, default='', null=True, blank=True)
    color               = models.CharField(max_length=50, default='', null=True, blank=True)
    envase              = models.CharField(max_length=50, default='', null=True, blank=True)
    grados              = models.CharField(max_length=10, default='', null=True, blank=True)
    grados2             = models.FloatField(default=0)
    ean_13              = models.CharField(max_length=50, default='', null=True, blank=True)
    tipo                = models.CharField(max_length=60, blank=True, null=True,default='')
    talla               = models.CharField(max_length=50, default='', null=True, blank=True)
    slug                = AutoSlugField(populate_from=[
        'marca__slug',
        'nombre',
        'medida_cant',
        'unidades',
        'envase',
        'grados2',
        'talla'], editable=False, unique=True, db_index=True)

    created             = models.DateTimeField("date created", editable=False,default=timezone.now)
    updated             = models.DateTimeField("last updated", auto_now=True,auto_now_add=False)
    tags                = TaggableManager(through=TaggedArticles)
    priceCurrency       = models.CharField(max_length=3, default="CLP")
    

    
    _metadata = {
        'title': 'nombre',
        'description': 'slug',
        'og:description': 'nombre',
    }
    @property
    def get_price(self)->Decimal:
        bestprice = Vendedores.objects.filter(articulo=self).exclude(vendidoen__precio=0).values_list('vendidoen__precio', flat=True).order_by('vendidoen__precio').first()

        return bestprice
    
    @property
    def titulo(self)->str:
        titulo = str(self.marca) + ': ' + self.nombre + ' (' 
        if self.unidades:
            titulo = titulo + str(self.unidades) + ' ' 
        
        if self.envase:
            titulo = titulo + self.envase 
        else:
            if self.unidades == 1:
                titulo = titulo + ' unidad '
            else:
                titulo = titulo + ' unidades '

        if self.medida_cant:
            titulo = titulo + ' de ' + str(self.medida_cant) 

        titulo = titulo + ' ' + self.medida_um  + ')'

        if self.grados2:
            titulo = titulo + ' ' + str(self.grados2) + '°'

        return titulo

    @property
    def sd(self):
        return {
            "@type": 'Product',
            "name": self.titulo,
            "description": self.titulo,
            "brand":{
                "@type":"Brand",
                "name": self.marca.nombre
            },
            "image": self.image1,
            "sku": self.ean_13,
            "offers": {
                "@type":"Offer",
                "price": self.get_price,
                "priceCurrency":"CLP",
                "itemCondition":"https://schema.org/NewCondition",
                "availability":"https://schema.org/InStock",
            }
        }
    
    #  "name":"Desodorante Crema Rexona Classic 48 g | Jumbo.cl",
    #  "image":"https://jumbo.vteximg.com.br/arquivos/ids/416212/Desodorante-en-crema-classic-48-g.jpg?v=637479990215800000",
    #  "description":"Desodorante Crema Rexona Classic 48 g | Jumbo.cl | Código de producto: 9760",
    #  "sku":"9760",
    #  "offers":{
    #       "@type":"Offer",
    #       "price":"6699",
    #       "priceCurrency":"CLP",
    #       "url":"https://cl-jumboweb-render-prod.ecomm.cencosud.com/www-jumbo-clrexona-desodorantebarra-clinical-softsolidclassic-48g/p",
    #       "itemCondition":"https://schema.org/NewCondition",
    #       "availability":"https://schema.org/InStock",
    #       "seller":{
    #           "@type":"Organization",
    #           "name":"Jumbo.cl"
    #       }
    #   }}

    @property
    def resultsCount(self) -> int:
        return Vendedores.objects.filter(articulo=self).exclude(vendidoen__precio__exact=0).count()
    

    def get_absolute_url(self):
        return reverse("precios:detalle", args=(self.slug,))

    def get_update_url(self):
        return reverse("precios:Articulos_update", args=(self.pk,))

    # @staticmethod
    # @property
    def quienesvenden(self) -> int:
        mp = list(Vendedores.objects.filter(articulo=self).values_list('vendidoen__site__id', flat=True).all())
        return mp
    
    # @property
    # @staticmethod
    def cuanntosvenden(self, vendedores:List[int]=None) -> int:
        mp = Vendedores.objects.filter(articulo=self)
        if vendedores:
            mp = mp.filter(vendidoen__site__in=vendedores)
        mp = mp.count()
        return mp
    
    @property
    def vendido_url(self, vendedores:List[int]=None):
        mp = Vendedores.objects.filter(articulo=self)
        if vendedores:
            mp = mp.filter(vendidoen__site__in=vendedores)
        mp = mp.order_by('vendidoen__precio').first()
        return mp.vendidoen.url

    @property
    def vendido(self, vendedores:List[int]=None) -> int:
        mp = Vendedores.objects.filter(articulo=self).values('vendidoen')
        if vendedores:
            mp = mp.filter(vendidoen__site__in=vendedores)
        mp = mp.order_by('vendidoen__precio').first()
        return mp

    @property
    def vendido_icon(self, vendedores:List[int]=None):
        mp = Vendedores.objects.filter(articulo=self)
        if vendedores:
            mp = mp.filter(vendidoen__site__in=vendedores)
        mp = mp.order_by('vendidoen__precio').first()

        return mp.vendidoen.site.icon_image

    @property
    def mejorprecio(self, vendedores:List[int]=None) -> int:
        mp = Vendedores.objects.filter(articulo=self).exclude(vendidoen__precio=0)
        if vendedores:
            mp = mp.filter(vendidoen__site__in=vendedores)
        mp = mp.order_by('vendidoen__precio').first()
        if mp:
            return mp.vendidoen.precio
        else:
            return None

    @property
    def vendidopor(self, vendedores:List[int]=None):
        mp = Vendedores.objects.filter(articulo=self)
        if vendedores:
            mp = mp.filter(vendidoen__site__in=vendedores)
        mp = mp.order_by('vendidoen__precio').first()

        return mp.vendidoen.site.siteName

    @property
    def medida(self) -> CharField:
        return self.medida_um + '-' + str(self.medida_cant)

    @property
    def image1(self) :
        
        imagen = Vendedores.objects.filter(articulo=self).exclude(vendidoen__image__isnull=True).exclude(vendidoen__site__use_his_image=False).first()
        if imagen:
            return imagen.vendidoen.image
        else:
            # print('aca')
            return "aca"
        
    def __str__(self):
        return self.titulo
        

    class Meta:
        verbose_name = 'Articulo'
        verbose_name_plural = 'Articulos'
        indexes = [
            models.Index(
                fields=['marca', 'nombre', 'medida_cant', 'grados2', 'unidades', 'envase', 'talla'],
                name='articulo_id1_idx',
            ),
        ]
        ordering        = ( "marca", "nombre", "medida_cant","grados2","unidades", "envase", "talla" )
        unique_together = [['marca', 'nombre', 'medida_cant','grados2','unidades', 'envase', 'talla']]
        index_together  = [['marca', 'nombre', 'medida_cant','grados2','unidades', 'envase', 'talla']]

        
class Unifica(models.Model):
    """
    Campos que se buscaran en los sitios.
    Se utiliza BeautifulSoup
    """
    si_marca                = models.ForeignKey(Marcas, on_delete=models.PROTECT, default=1,related_name='si_marca')
    si_nombre               = models.CharField(max_length=250, null=True, blank=True)
    si_grados2              = models.FloatField(default=0)
    si_medida_cant          = models.FloatField(default=0)
    si_unidades             = models.IntegerField(default=1)
    si_envase               = models.CharField(max_length=50, null=True, blank=True)
    si_talla                = models.CharField(max_length=50, default='', null=True, blank=True)

    entonces_marca          = models.ForeignKey(Marcas, on_delete=models.PROTECT, default=1,related_name='entonces_marca')
    entonces_nombre         = models.CharField(max_length=250, null=True, blank=True)
    entonces_grados2        = models.FloatField(default=0)
    entonces_medida_cant    = models.FloatField(default=0)
    entonces_unidades       = models.IntegerField(default=1)
    entonces_envase         = models.CharField(max_length=50, null=True, blank=True)
    entonces_talla          = models.CharField(max_length=50, default='', null=True, blank=True)

    contador                = models.IntegerField(default=0)
    automatico              = models.BooleanField(default=False)
    tipo                    = models.CharField(max_length=250, null=True, blank=True)
    

    # created                 = models.DateTimeField(auto_now_add=True)
    # updated                 = models.DateTimeField(auto_now=True,auto_now_add=False)

    def __str__(self):
        return "{0}: {1} {2}° {3}   {4}u".format( self.si_marca, self.si_nombre, self.si_grados2, self.si_medida_cant, self.si_unidades)
    
    @admin.display(ordering='si_marca')
    def cont(self):
        return self.contador

    def auto(self):
        if self.automatico:
            test = '<img src="/static/admin/img/icon-yes.svg" alt="True">'
        else:
            test = '<img src="/static/admin/img/icon-no.svg" alt="False">'

        return format_html(test)
    
    def si_mrc_lst(self):
        return format_html(
            '<a target="_new" href="/precios/brands/detail/{}">{}</a>',
            self.si_marca.slug,
            self.si_marca.nombre,
        )
    
    def si_grd(self):
        return self.si_grados2
    
    def si_mdd(self):
        return self.si_medida_cant
    
    def si_udd(self):
        return self.si_unidades
    
    def si_env(self):
        return self.si_envase
    
    def etc_mrc_lst(self):
        return format_html(
            '<a target="_new" href="/precios/brands/detail/{}">{}</a>',
            self.entonces_marca.slug,
            self.entonces_marca.nombre,
        )
    def etc_grd(self):
        return self.entonces_grados2
    
    def etc_mdd(self):
        return self.entonces_medida_cant
    
    def etc_udd(self):
        return self.entonces_unidades
    
    def etc_env(self):
        return self.entonces_envase
    
    def etc_talla(self):
        return self.entonces_talla

    def save(self, *args, **kwargs):
        if self.si_nombre:
            self.si_nombre = self.si_nombre.lower()
        if self.entonces_nombre:
            self.entonces_nombre = self.entonces_nombre.lower()
        return super(Unifica, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Unifica'
        # index_together  = [('si_marca', 'si_nombre', 'si_medida_cant','si_grados2','si_unidades', 'si_envase'),]
        # unique_together = [['si_marca', 'si_nombre', 'si_medida_cant','si_grados2','si_unidades','si_envase']]
        # ordering = ("si_marca", "si_nombre", "si_medida_cant", "si_grados2", "si_unidades", "si_envase")
        constraints = [
            models.UniqueConstraint(
                fields=['si_marca', 'si_nombre', 'si_medida_cant', 'si_grados2', 'si_unidades', 'si_envase', 'si_talla' ],
                # condition=Q(deleted=False),
                name='unique_if_not_deleted')
        ]


### Almacen de resultados
class SiteURLResults(models.Model):
    """
    URL de paginas de un sitio.
    URLs encontradas en cada sitio
    """
    site            = models.ForeignKey(Site, on_delete=models.CASCADE, default=1)
    url             = models.URLField(blank=True, null=True)
    error404        = models.BooleanField(default=False)
    created         = models.DateTimeField(editable=False,default=timezone.now)
    updated         = models.DateTimeField(auto_now=True,auto_now_add=False)
    secondsToGet    = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    precio          = models.IntegerField(default=0)
    precio_cantidad = models.IntegerField(default=0, blank=True, null=True)
    nombre          = models.CharField(max_length=650, blank=True, null=True, default='')
    idproducto      = models.CharField(max_length=50, blank=True, null=True, default='')
    marca           = models.CharField(max_length=50, blank=True, null=True, default='')
    medida_um       = models.CharField(max_length=20, blank=True, null=True, default='')
    medida_cant     = models.FloatField(default=0)
    categoria       = models.CharField(max_length=50, blank=True, null=True, default='')
    descripcion     = models.TextField(default='', blank=True, null=True)
    tipo            = models.CharField(max_length=60, blank=True, null=True,default='')
    proveedor       = models.CharField(max_length=30, blank=True, null=True, default='')
    stock           = models.CharField(max_length=20, blank=True, null=True,default='')
    precioref       = models.IntegerField(default=0)
    unidades        = models.FloatField(default=1)
    image           = models.URLField(max_length=600, blank=True, null=True, default='')

    reglas          = models.ManyToManyField(Unifica, related_name="las_reglas", default=None, blank=True)
    tags            = TaggableManager(through=TaggedUrls)
    priceCurrency   = models.CharField(max_length=3, default="CLP")


        
    @property
    def HistoryCount(self) -> int:
        return PriceHistory.objects.filter( FromResult=self).count()

    @property
    def artRef(self) -> int:
        return Vendedores.objects.filter( vendidoen=self).count()
    
    @property
    def num_articulos(self) -> int:
        id_articulo = Vendedores.objects.filter(vendidoen=self).values_list('articulo', flat=True).get()
        num_articulos = Vendedores.objects.filter(articulo=id_articulo).count()
        return num_articulos
    
    @property
    def posicion(self) -> str:
        id_articulo = Vendedores.objects.filter(vendidoen=self).values_list('articulo', flat=True).get()
        articulos_list = Vendedores.objects.filter(articulo=id_articulo).order_by("vendidoen__precio")
        posicion = 0
        for art in articulos_list:
            posicion = posicion + 1
            if art.vendidoen.site == self.site:
                break
        return posicion
    @property
    def artid(self) -> object:
        return Vendedores.objects.get(vendidoen=self)

    def __str__(self):
        return "{0}: {1} ".format( self.site, self.url)

    def get_absolute_url(self):
        return reverse("precios:SiteURLResults_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("precios:SiteURLResults_update", args=(self.pk,))


    class Meta:
        verbose_name = 'URL encontrada en sitio'
        verbose_name_plural = 'URLs encontradas en sitio'
        index_together = [
            ("site", "url"),
        ]
        ordering = ("-updated",)
    
    def save(self, *args, **kwargs):
        existe_historico = False
        if self.id:
            ## Ya existe
            existe_historico = True
            this_valor    = self.precio
            this_date     = self.updated

            if this_valor !=0 :
                resultadoanterior = PriceHistory.objects.filter(FromResult=self.pk).order_by('-OldDate').first() 
                if resultadoanterior:
                    if resultadoanterior.Oldprecio != this_valor:
                        PriceHistory.objects.update_or_create(
                            FromResult=self,
                            Oldprecio=this_valor,
                            OldDate=this_date
                        )
                else:
                    PriceHistory.objects.update_or_create(
                            FromResult=self,
                            Oldprecio=this_valor,
                            OldDate=this_date
                    )

        ### Busco Marca
        if not self.marca and self.nombre != '' and not self.error404:
            nombre = self.nombre.strip()
            marca = ''
            ## Revisamos si la marca enviada existe
            if Marcas.objects.filter(nombre=marca).exists():
                ## Puede ser marca habilitada o no, veamos:
                if Marcas.objects.filter(es_marca=True, nombre=marca).exists():    
                    posible_marca = Marcas.objects.filter(es_marca=True, nombre=marca).values_list('nombre', flat=True).get()
                    self.nombre = nombre.replace(posible_marca, '').strip()
                    self.marca = marca
                else:
                    ## Marca no esta habilitada:
                    marca_obj = Marcas.objects.filter(es_marca=False, nombre=marca).get()
                    if Unifica.objects.filter(si_marca=marca_obj, si_nombre=None, si_grados2=float(0), si_medida_cant=float(0), si_unidades=1,  automatico=False ).exists():
                        unifica_obj = Unifica.objects.filter(si_marca=marca_obj, si_nombre=None, si_grados2=float(0), si_medida_cant=float(0), si_unidades=1, automatico=False).first()
                        if unifica_obj:
                            self.marca = unifica_obj.entonces_marca.nombre
                            self.nombre = nombre.replace(marca, '').strip()

            else:
                # Si la marca no existe, busco en todas las marcas habilitadas si estuviera en el nombre
                
                palabras = (nombre + ' ' + marca).split(' ')
                for palabra in palabras:
                    if Marcas.objects.filter(nombre=palabra, es_marca=True).values_list('nombre', flat=True).exists():
                        self.marca = palabra
                        self.nombre = nombre.replace(marca, '').strip()
                
                ## Finalmente la marca no existe, se crea
                if marca !='' and len(marca) >= 2:
                    print(f'Marca no existe =|{marca}| creando Marca')
                    marca_obj = Marcas(
                        nombre=marca,
                        es_marca=False,
                        grados=False,
                        talla=False
                    )
                    marca_obj.save()
                    self.marca = marca
                    self.nombre = nombre.replace(marca, '').strip()
                else:
                    self.marca = None
            
        #     temp = self.nombre.split()
        #     for palabra_busco in temp:
        #         for posible_marca in Marcas.objects.filter(nombre=palabra_busco, es_marca=True).values_list('nombre', flat=True).all():
        #             self.marca = posible_marca
        #             self.nombre = self.nombre.replace(posible_marca, '')
        #             print(f'1- reemplaza aca marca que llega= {self.marca}')
        #             break

        # if not self.marca and self.nombre != '' and not self.error404:
        #     for posible_marca in Marcas.objects.filter(es_marca=True).values_list('nombre', flat=True).all():
        #         if ( ' ' + posible_marca +' ' in self.nombre ) :
        #             self.marca = posible_marca
        #             self.nombre = self.nombre.replace(posible_marca, '')
        #             print(f'2- reemplaza aca marca que llega= {self.marca}')
        #             break

        # if not self.marca and self.nombre != '' and not self.error404:
        #     for posible_marca in Marcas.objects.filter(es_marca=True).values_list('nombre', flat=True).all():
        #         if (  posible_marca  in self.nombre ) :
        #             self.marca = posible_marca
        #             self.nombre = self.nombre.replace(posible_marca, '')
        #             print(f'3- reemplaza aca marca que llega= {self.marca}')
        #             break

        # if not Marcas.objects.filter(nombre__iexact=self.marca, es_marca=True).exists() and not self.marca and self.idproducto:
        #     if self.site.es_ean13 and Articulos.objects.filter(ean_13 = self.idproducto).exclude(marca__es_marca = False).exists():
        #         print(f'4- SiteURLResults: Utiliza la marca de un articulo con mismo ean_13 ean_13={self.idproducto} marca={self.marca}')
        #         art = Articulos.objects.filter(ean_13 = self.idproducto).exclude(marca__es_marca = False).values_list('marca__nombre', flat=True).first()
        #         self.marca = art
        #     else:
        #         print('SiteURLResults: limpia marca pues no existe')
        #         self.marca = ''

        super(SiteURLResults, self).save(*args, **kwargs)
        if not existe_historico:
            if self.precio !=0:
                PriceHistory.objects.update_or_create(
                        FromResult=self,
                        Oldprecio=self.precio,
                    )



class PriceHistory(models.Model):
    """
    URL de paginas de un sitio.
    URLs encontradas en cada sitio
    """
    FromResult          = models.ForeignKey(SiteURLResults, on_delete=models.CASCADE, default=1)
    Oldprecio           = models.IntegerField(default=0)
    OldDate             = models.DateTimeField(editable=False,default=timezone.now, db_index=True)

    def __str__(self):
        return "{0}: {1} ".format( self.FromResult, self.Oldprecio)

    def get_absolute_url(self):
        return reverse("precios:PriceHistory_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("precios:PriceHistory_update", args=(self.pk,))

        
    class Meta:
        verbose_name = 'Precio historico'
        verbose_name_plural = 'Precios historicos'
        index_together = [
            ("FromResult"),
        ]
        ordering = ("-OldDate",)


class Vendedores(models.Model):
    """
    Vendedores
    """
    articulo            = models.ForeignKey(Articulos, on_delete=models.CASCADE, default=1)
    vendidoen           = models.ForeignKey(SiteURLResults, on_delete=models.CASCADE, default=1)
    
    @property
    def sd(self):
        return {
            "@type": 'Product',
            "name": self.articulo.nombre,
            "brand":{
                "@type":"Brand",
                "name": self.articulo.marca},
        }
    
    @property
    def precio(self)-> int :
        return self.vendidoen.precio
        
    def __str__(self):
        return "{0}: {1}".format( self.articulo, self.vendidoen)


    class Meta:
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'
        unique_together = [['articulo', 'vendidoen']]
        index_together  = [['articulo', 'vendidoen']]
        indexes = [models.Index(fields=['articulo', ]),
                   models.Index(fields=['vendidoen', ])]
        


class ReemplazaPalabras(models.Model):
    palabra = models.CharField(max_length=100, db_index=True, unique=True)
    reemplazo = models.CharField(max_length=100, default='', blank=True, null=True)
    contador  = models.IntegerField(default=0)

    def __str__(self):
        return self.palabra
    
    def save(self, *args, **kwargs):
        self.palabra = self.palabra.lower()
        if self.reemplazo:
            self.reemplazo = self.reemplazo.lower()

        return super(ReemplazaPalabras, self).save(*args, **kwargs)


class AllPalabras(models.Model):
    # palabra     = models.CharField(max_length=100, db_index=True, unique=True)
    palabra     = models.CharField(max_length=100, db_index=True, unique=False)
    contador    = models.IntegerField(default=0)
    tipo        = models.CharField(
        max_length=20, 
        choices=TIPOPALABRA.choices, 
        help_text='Palabra es tipo',
        blank=True, 
        null=True
    )
    largo    = models.IntegerField(default=0, db_index=True)
    
    # unique_together = [['country', 'name']]
    class Meta:
        verbose_name = "AllPalabras"
        verbose_name_plural = "AllPalabras"
        unique_together = [['tipo', 'palabra']]
        ordering = ("palabra",)


    def __str__(self):
        return self.palabra
    
    def save(self, *args, **kwargs):
        self.palabra = self.palabra.lower().strip()
        self.largo   = len(self.palabra)
        return super(AllPalabras, self).save(*args, **kwargs)