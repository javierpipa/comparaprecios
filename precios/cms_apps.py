from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import gettext_lazy as _


class PreciosApphook(CMSApp):
    app_name = "precios"
    name = _("Aplicacion Precios")

    def get_urls(self, page=None, language=None, **kwargs):
        return ["precios.urls"]


apphook_pool.register(PreciosApphook)  # register the application
