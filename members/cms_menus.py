from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from cms.menu_bases import CMSAttachMenu



class UserMenu(CMSAttachMenu):

    name = _("User menu")

    def get_nodes(self, request):
            return [
                # NavigationNode(_("Profile"), reverse(profile), 30, attr={'visible_for_anonymous': False}),
                NavigationNode(_("Log in"), "/members/login_user", 31, attr={'visible_for_authenticated': False}),
                NavigationNode(_("Preferencias"), "/members/home", 31, attr={'visible_for_anonymous': False}),
                NavigationNode(_("Direccion"), "/members/update_member", 31, attr={'visible_for_anonymous': False}),
                NavigationNode(_("Registrarse"), "/members/register_user", 32, attr={'visible_for_authenticated': False}),
                NavigationNode(_("Log out"), "/members/logout_user", 32, attr={'visible_for_anonymous': False}),
            ]

# class MembersMenu(CMSAttachMenu):

#     name = _("Members menu")

#     def get_nodes(self, request):
#         nodes = []
#         n = NavigationNode(_('Preferencias'), "/members/home", 7)
#         n2 = NavigationNode(_('Direccion'), "/members/update_member", 8)
#         n3 = NavigationNode(_('Logout'), "/members/logout_user", 9)
#         nodes.append(n)
#         nodes.append(n2)
#         nodes.append(n3)
#         return nodes


menu_pool.register_menu(UserMenu)
# menu_pool.register_menu(MembersMenu)