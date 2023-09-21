from precios.views_supermercado import (
    cotiza,
    ajax_robots,
    ajax_save_cotiza,
    ajax_plan,
    # ajax_url,
    # ajax_url_ld_json,
    # ajax_sitemap_url,
    # ajax_craw,
)

from precios.views_cedl import (
    ProductDetailView,
    MarcasListView,
    MarcasDetailView,
    CorporationListView,
    CorporationDetailView,
    ArticulosListView,
    ArticulosDetailView,
    SiteListView,
    SiteDetailView,
    SiteURLResultsListView,
    SiteURLResultsDetailView,
    PriceHistoryListView,
    PriceHistoryDetailView,
)
from precios.views import (
    # brandProducts,
    # index, 
    precios, 
    estado, 
    # detalle,
    rescan,
    supermercado,
    antiguedad_registros,

)
from precios.views_cart import (
    cart,
    add_product,
    get_cart,
    get_cart_simple,
    increase_product,
    decrementproduct,
    removeproduct,
    loadcart,
    deletecart,
    emptycart,
    save_cart,
    
)
from precios.views_sitemap import (
    marcas_y_articulos_sitemaps,
    sitemaps_marcas,
    sitemaps_articles,
    # sitemaps_URLResults,
)

from precios.views_acerca import (
    acerca,
    planes_buscan,
    planes_ofrecen,
    cobertura
)
from precios.views_compara import (
    siteUrlsinSite, 
    # brands_all,
    # brands_one,
    # brands_rule,
    CsvURLUploader
)
from . import api
from rest_framework import routers

from django.urls import include, path, re_path
from django.contrib import admin

admin.autodiscover()

app_name = 'precios_real'

router = routers.DefaultRouter()
router.register("Marcas",           api.MarcasViewSet)
router.register("Corporation",      api.CorporationViewSet)
router.register("Articulos",        api.ArticulosViewSet)
router.register("Site",             api.SiteViewSet)
router.register("SiteURLResults",   api.SiteURLResultsViewSet)
router.register("Vendedores",       api.VendedoresViewSet)
router.register("PriceHistory",     api.PriceHistoryViewSet)

urlpatterns = [
    path("api/v1/", include(router.urls)),
    path("precios/PriceHistory/",                       PriceHistoryListView.as_view(), name="PriceHistory_list"),
    path("precios/PriceHistory/detail/<int:pk>/",       PriceHistoryDetailView.as_view(), name="PriceHistory_detail"),
    path("precios/SiteURLResults/",                     SiteURLResultsListView.as_view(), name="SiteURLResults_list"),
    path("precios/SiteURLResults/detail/<int:pk>/",     SiteURLResultsDetailView.as_view(), name="SiteURLResults_detail"),
    path("precios/Site/",                               SiteListView.as_view(),         name="Site_list"),
    path("precios/Site/detail/<int:pk>/",               SiteDetailView.as_view(),       name="Site_detail"),
    
    path("precios/Corporation/",                        CorporationListView.as_view(),  name="Corporation_list"),
    path("precios/Corporation/detail/<int:pk>/",        CorporationDetailView.as_view(), name="Corporation_detail"),
    path("precios/Articulos/",                          ArticulosListView.as_view(),    name="Articulos_list"),
    path("precios/Articulos/detail/<slug>/",            ArticulosDetailView.as_view(),  name="Articulos_detail"),

    path('article/<slug>/',                             ProductDetailView.as_view() ,   name='detalle'),
    path('rescan/<slug>/',                              rescan,                         name='rescan'),
    path('precios/',                                    precios,                        name='home'),

    ## Supermercado
    path('estado/',                                     estado,                         name='estado'),
    path('cobertura/',                                  cobertura,                      name='cobertura'),
    path("supermercado/<int:pk>/",                      supermercado,                   name="supermercado"),
    path("antiguedad_registros",                        antiguedad_registros,           name="antiguedad_registros"),
    path("siteurlsinsite/",                             siteUrlsinSite,                 name="siteUrlsinSite"),
    ### Marcas
    # path("brandProducts/<brand>/",                      brandProducts,                  name="brandProducts"),
    path("brands/",                                     MarcasListView.as_view(),       name="brands"),
    path("brands/detail/<slug>/",                       MarcasDetailView.as_view(),     name="brands_detail"),
    
    # path("brands_rule",                                 brands_rule,                    name="brands_rule"),
    ### CART
    path("addproduct",                                  add_product,                    name="add_product"),
    path("decrementproduct",                            decrementproduct,               name="decrementproduct"),
    path("increase_product",                            increase_product,               name="increase_product"),
    path("get_cart",                                    get_cart,                       name="get_cart"),
    path("get_cart_simple",                             get_cart_simple,                name="get_cart_simple"),
    path("save_cart",                                   save_cart,                      name="save_cart"),
    path("removeproduct",                               removeproduct,                  name="removeproduct"),
    path("emptycart",                                   emptycart,                      name="emptycart"),
    path("deletecart/<id>",                             deletecart,                     name="deletecart"),
    path("loadcart/<id>",                               loadcart,                       name="loadcart"),
    path("cart",                                        cart,                           name="cart"),
    ## compara
    # path("brands_one/<brand>",                          brands_one,                     name="brands_one"),
    ## acerca
    path("acercadevop",                                 acerca,                         name="acerca"),
    ## planes
    path("planes_buscan",                               planes_buscan,                  name="planes_buscan"),
    path("planes_ofrecen",                              planes_ofrecen,                 name="planes_ofrecen"),
    ### Cotiza registro empresa, supermercado, distribuidor
    path("cotize",                                      cotiza,                         name="cotiza"),
    path('ajax_robots',                                 ajax_robots,                    name='ajax_robots'),
    path('ajax_plan',                                   ajax_plan,                      name='ajax_plan'),
    path('ajax_save_cotiza',                            ajax_save_cotiza,               name='ajax_save_cotiza'),
    ## Sitemaps
    re_path('sitemap.xml',                              marcas_y_articulos_sitemaps,    name='django.contrib.sitemaps.views.sitemap'),
    re_path(r'sitemaps/brands-(?P<pagina>\d+).xml',     sitemaps_marcas,                name='django.contrib.sitemaps.views.index'),
    re_path(r'sitemaps/articles-(?P<pagina>\d+).xml',   sitemaps_articles,              name='django.contrib.sitemaps.views.index'),
    # re_path(r'sitemaps/URLResults-(?P<pagina>\d+).xml',  sitemaps_URLResults,   name='django.contrib.sitemaps.views.index'),
    ## Mapas
    
    ### Update Precios
    path('csv-uploader/', CsvURLUploader.as_view(), name='csv-uploader'),

]


