from django.contrib import admin
from cms.admin.placeholderadmin import PlaceholderAdminMixin

from members.models import (
    Member,
    Lista, 
    DetalleLista,
    Plan,
    ContenidoPlan,
    Periodo,
    MemberStats,
    Account,
    Contrato,
)

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmmin

class UserMemberInline(admin.StackedInline):
    model = Member
    can_delete: bool  = False

class ListaInline(admin.TabularInline):
    model = Lista
    can_delete: bool  = False
    extra = 0
    fields = ('nombre_lista','created', 'updated')
    readonly_fields = ('created', 'updated')

class MemberStatsInline(admin.TabularInline):
    model = MemberStats
    can_delete: bool  = False
    fields = ('objeto','period', 'cuantity')
    readonly_fields = ('objeto','period', 'cuantity')
    extra = 0

class DetalleListaInline(admin.TabularInline):
    model = DetalleLista
    can_delete: bool  = False
    fields = ('articulo','cantidad')
    readonly_fields = ('articulo','cantidad')
    extra = 0


class AccountUserAdmmin(AuthUserAdmmin):
    def add_view(self, *args, **kwargs):
        self.inlines = []
        return super(AccountUserAdmmin,self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines = [UserMemberInline]
        return super(AccountUserAdmmin,self).change_view(*args, **kwargs)


class ContenidoPlanInline(admin.TabularInline):
    model = ContenidoPlan
    extra = 0
    can_delete = True
    ordering = ('my_order',)



class PlanAdmmin(PlaceholderAdminMixin, admin.ModelAdmin):
    # pass
    list_display = (
        "nombre",
        "tipo",
        "publico",
        "clase",
        "valor_mes",
        "valor_agno",
        
    )
    inlines = [ContenidoPlanInline,]
    list_filter = ('publico','clase', 'tipo')


class ContenidoPlanAdmin(admin.ModelAdmin):
    list_display = (
        "plan",
        "objeto",
        "cantidad",
        "todos",
        
    )

class MemberStatsAdmin(admin.ModelAdmin):
    list_display = (
        "member",
        "period",
        "objeto",
        "cuantity",
        
    )
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "plan",
        "created",
        "active",
    )

class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "direccion",
        "country",
        "comuna",
        "account2",
    )
    list_filter = ('country',)
    inlines     = [ListaInline, MemberStatsInline]

class ListaAdmin(admin.ModelAdmin):
    list_display = (
        "member",
        "nombre_lista",
        "created",
        "updated",
    )
    
    inlines     = [DetalleListaInline]

class ContratoAdmin(admin.ModelAdmin):
    list_display = (
        "site",
        "plan",
        "member",
        "fecha_inicio",
    )
    


admin.site.unregister(User)
admin.site.register(User, AccountUserAdmmin)
admin.site.register(Lista,ListaAdmin )
admin.site.register(DetalleLista )
admin.site.register(Plan, PlanAdmmin)
admin.site.register(ContenidoPlan,ContenidoPlanAdmin )
admin.site.register(Periodo)
admin.site.register(MemberStats, MemberStatsAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Contrato, ContratoAdmin)