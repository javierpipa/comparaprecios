from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import gettext_lazy as _

# from .models import Hello

# from precios_integration.models import SettingsPluginModel



# class SettingsPluginPublisher(CMSPluginBase):
#     model = SettingsPluginModel  # model where plugin data are saved
#     module = _("Precios")
#     name = _("Settings Plugin")  # name of the plugin in the interface
#     render_template = "precios_integration/settings_plugin.html"
#     cache = False

#     def render(self, context, instance, placeholder):
#         context.update({'instance': instance})
#         return context

# plugin_pool.register_plugin(SettingsPluginPublisher)  # register the plugin


# # @plugin_pool.register_plugin
# class HelloPlugin(CMSPluginBase):
#     model = CMSPlugin
#     name = _("Hello Plugin")
#     render_template = "hello_plugin.html"
#     cache = False

#     def render(self, context, instance, placeholder):
#         context = super().render(context, instance, placeholder)
#         return context

# plugin_pool.register_plugin(HelloPlugin)  # register the plugin