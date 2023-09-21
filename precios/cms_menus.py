from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from cms.menu_bases import CMSAttachMenu

class AcercaMenu(CMSAttachMenu):

    name = _("Acerca menu")

    def get_nodes(self, request):
        nodes = []
        n = NavigationNode(_('Planes'), '/precios/acercadevop',1,None)
        n01 = NavigationNode(_('Planes para personas que buscan'), "/precios/planes_buscan", 1)
        n02 = NavigationNode(_('Planes para empresas que ofrecen'), "/precios/planes_ofrecen", 1)
        n2 = NavigationNode(_('Coberturas de despacho'), "/precios/cobertura", 4)
        n3 = NavigationNode(_('Estado indexacion'), "/precios/estado", 5)
        n4 = NavigationNode(_('Antiguedad registros'), "/precios/antiguedad_registros", 6)
        nodes.append(n)
        nodes.append(n01)
        nodes.append(n02)
        nodes.append(n2)
        nodes.append(n3)
        nodes.append(n4)
        return nodes


class PreciosMenu(CMSAttachMenu):

    name = _("Precios menu")

    def get_nodes(self, request):
        nodes = []
        n = NavigationNode(_('Buscar'), '/precios/precios',991,None)
        n1 = NavigationNode(_('Marcas'), '/precios/brands',991,None)
        nodes.append(n)
        nodes.append(n1)
        return nodes


menu_pool.register_menu(AcercaMenu)
menu_pool.register_menu(PreciosMenu)

