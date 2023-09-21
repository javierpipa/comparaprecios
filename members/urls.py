from django.urls import path
from .views import (
    home,
    login_user, 
    logout_user, 
    register_user,
    update_member,
    load_regions,
    load_cities,
    load_countries,
    set_cobertura,
    get_cobertura,
    set_costo_despacho,
    get_costo_despacho,
)

app_name = 'members'
urlpatterns = [
    path('login_user', login_user, name='login'),
    path('logout_user', logout_user, name='logout'),
    path('register_user', register_user, name='register_user'),
    path('home', home, name='home'),
    path('update_member/', update_member, name='update_member'),
    path('ajax_paises', load_countries, name='ajax_paises'),
    path('ajax_regiones', load_regions, name='ajax_regiones'),
    path('ajax_comunas', load_cities, name='ajax_comunas'),
    path('ajax_set_cobertura', set_cobertura, name='ajax_set_cobertura'),
    path('ajax_get_cobertura', get_cobertura, name='ajax_get_cobertura'),
    path('ajax_set_costo_despacho', set_costo_despacho, name='ajax_set_costo_despacho'),
    path('ajax_get_costo_despacho', get_costo_despacho, name='ajax_get_costo_despacho'),
    
]