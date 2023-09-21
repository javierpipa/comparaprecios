from django.contrib import admin
from cms.admin.placeholderadmin import PlaceholderAdminMixin

# Register your models here.
from .models import (
    SettingsPluginModel, 
    PlanPluginModel,
    ContenidoPlanPluginModel
)



class PlanPluginModelAdmin(PlaceholderAdminMixin, admin.ModelAdmin):
    pass

class ContenidoPlanPluginModelAdmin(PlaceholderAdminMixin, admin.ModelAdmin):
    pass

admin.site.register(PlanPluginModel, PlanPluginModelAdmin)
admin.site.register(ContenidoPlanPluginModel, ContenidoPlanPluginModelAdmin)