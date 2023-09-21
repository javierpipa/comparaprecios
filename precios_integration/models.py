from django.db import models
from cms.models import CMSPlugin
from precios.models import Settings
from members.models import Plan, ContenidoPlan

class SettingsPluginModel(CMSPlugin):
    Settings = models.ForeignKey(Settings,on_delete=models.CASCADE)

    def __unicode__(self):
        # return self.Settings.key
        return "{0}: {1}".format(self.Settings.key, self.Settings.value)


class PlanPluginModel(CMSPlugin):
    Plan = models.ForeignKey(Plan,on_delete=models.CASCADE)

    # def copy_relations(self, oldinstance):
    #     # Before copying related objects from the old instance, the ones
    #     # on the current one need to be deleted. Otherwise, duplicates may
    #     # appear on the public version of the page
    #     self.associated_item.all().delete()

    #     for associated_item in oldinstance.associated_item.all():
    #         # instance.pk = None; instance.pk.save() is the slightly odd but
    #         # standard Django way of copying a saved model instance
    #         associated_item.pk = None
    #         associated_item.plugin = self
    #         associated_item.save()


    def __unicode__(self):
        return "{0}:{1} {2}".format( self.Plan.tipo, self.Plan.clase, self.Plan.nombre)


class ContenidoPlanPluginModel(CMSPlugin):
    ContenidoPlan = models.ForeignKey(ContenidoPlan,on_delete=models.CASCADE)

    # def copy_relations(self, oldinstance):
    #     # Before copying related objects from the old instance, the ones
    #     # on the current one need to be deleted. Otherwise, duplicates may
    #     # appear on the public version of the page
    #     self.associated_item.all().delete()

    #     for associated_item in oldinstance.associated_item.all():
    #         # instance.pk = None; instance.pk.save() is the slightly odd but
    #         # standard Django way of copying a saved model instance
    #         associated_item.pk = None
    #         associated_item.plugin = self
    #         associated_item.save()

    # def __unicode__(self):
    #     return "{0}:{1} ".format( self.ContenidoPlan.plan, self.ContenidoPlan.objeto)


# {% if user.is_authenticated %}
#     <a href="{% url 'precios:brands' %}" class="dropdown-item">Marcas</a>
# {% endif %}
# <!-- <a href="https://policies.devop.cl/privacy?hl=es-419&amp;fg=1" class="dropdown-item text-muted">Privacidad</a>
# <a href="https://www.devop.cl/services/?subid1" class="dropdown-item text-muted">Negocios</a>
# <a href="https://policies.devop.cl/terms?hl=es-419&amp;fg=1" class="dropdown-item text-muted">Condiciones</a>
# <a href="https://www.devop.cl/intl/es-419_cl/ads/?subi1" class="dropdown-item text-muted">Publicidad</a> -->