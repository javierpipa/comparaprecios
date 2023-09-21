from django.utils.translation import gettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cms.utils.urlutils import admin_reverse
from precios.models import Settings


# class PreciosToolbar(CMSToolbar):
#     supported_apps = (
#         'precios',
#         'precios_integration',
#     )

#     watch_models = [Settings]

#     def populate(self):
#         if not self.is_current_app:
#             return

#         menu = self.toolbar.get_or_create_menu('precios-app', _('Precios'))

#         menu.add_sideframe_item(
#             name=_('Estado'),
#             url=admin_reverse('precios:estado'),
#         )

#         menu.add_modal_item(
#             name=_('Estado'),
#             url=admin_reverse('precios:estado'),
#         )


# toolbar_pool.register(PreciosToolbar)  # register the toolbar