from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import gettext_lazy as _


class MembersApphook(CMSApp):
    app_name = "members"
    name = _("Members Application")

    def get_urls(self, page=None, language=None, **kwargs):
        return ["members.urls"]


apphook_pool.register(MembersApphook)  # register the application
