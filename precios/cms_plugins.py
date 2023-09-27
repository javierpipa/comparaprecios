from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import gettext_lazy as _



# from precios_integration.models import (
#     SettingsPluginModel, 
#     PlanPluginModel,
#     ContenidoPlanPluginModel
# )


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


# #### Planes de members
# class PlanPluginPublisher(CMSPluginBase):
#     model = PlanPluginModel  # model where plugin data are saved
#     module = _("Precios")
#     name = _("Planes Plugin")  # name of the plugin in the interface
#     render_template = "precios_integration/planes.html"
#     cache = False
#     allow_children = True

#     def render(self, context, instance, placeholder):
#         planes          = PlanPluginModel.objects.filter(Plan__publico=True).order_by('Plan__my_order')
#         # all()
#         # filter(publico=True, tipo=TIPO_PLAN.PERSONAS).order_by('my_order')
#         arr_planes      = []
#         for plan in planes:
#             contenidoPlan   = ContenidoPlanPluginModel.objects.all()
#         # filter(ContenidoPlan=instance)
#         # .order_by('my_order')
#             contenido     = {
#                 'plan': plan,
#                 'incorpora' : contenidoPlan
#             }
#             arr_planes.append(contenido)
#         context.update({'instance': arr_planes})
#         return context

# plugin_pool.register_plugin(PlanPluginPublisher)  # register the plugin


# #### Contenido de planes de members
# class ContenidoPlanCMSPlugin(CMSPluginBase):
#     render_template = 'precios_integration/contenido_plan.html'
#     name = 'Child'
#     model = ContenidoPlanPluginModel
#     require_parent = True  # Is it required that this plugin is a child of another plugin?
#     # You can also specify a list of plugins that are accepted as parents,
#     # or leave it away completely to accept all
#     parent_classes = ['PlanPluginPublisher']

#     def render(self, context, instance, placeholder):
#         context = super(ContenidoPlanCMSPlugin, self).render(context, instance, placeholder)
#         return context

# plugin_pool.register_plugin(ContenidoPlanCMSPlugin)  # register the plugin