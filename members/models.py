from django.db import models
from django.contrib.auth.admin import User


from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
import calendar


class TIPO_PLAN(models.TextChoices):
    PERSONAS        = "Personas"
    OFRECEN         = "Ofrecen"
    
class CLASE_PLAN(models.TextChoices):
    BASICO         = "Básico"
    AVANZADO       = "Avanzado"
    EMPRESA        = "Empresa"
    EMPRESA_FREE   = "Empresa Free"

class OBJETOS_EN_PLAN(models.TextChoices):
    USUARIOS          = "Usuarios."
    LISTAS            = "Listas de productos almacenados."
    BUSQUEDAS         = "Búsquedas."
    BUSQ_MARCAS       = "Búsquedas en marcas."
    EMAILS            = "Emails de lista."
    COMUNAS           = "Comunas de despacho o ubicacion de un país."
    SUPER_PROVEED     = "Supermercados o Proveedores que despachan en su(s) comuna(s) en un país."
    PROD_EN_LISTA     = "Productos en lista."
    INFORMES          = "Informes."
    PRODUCTOS         = "Productos."
    CUENTAS_BASICO    = "Cuentas Básico."
    CUENTAS_AVANZADO  = "Cuentas Avanzado."
    CUENTAS_EMPRESA   = "Cuentas Empresa."


class Plan(models.Model):
    nombre          = models.CharField(max_length=250, blank=True, null=True, help_text='Nombre del plan')
    leyenda         = models.CharField(max_length=400, blank=True, null=True, help_text='Leyenda del plan')
    icono           = models.CharField(max_length=100, blank=True, null=True, help_text='Icono del plan')
    area_class      = models.CharField(max_length=100, blank=True, null=True, help_text='Bootstrap  class')
    tipo            = models.CharField(
        max_length=30, choices=TIPO_PLAN.choices, default=TIPO_PLAN.PERSONAS, help_text='Tipo de plan'
    )
    clase           = models.CharField(
        max_length=30, choices=CLASE_PLAN.choices, default=CLASE_PLAN.BASICO, help_text='Clase de plan '
    )
    valor_mes       = models.PositiveIntegerField(
                            default=0,
                            blank=False,
                            null=False,)
    valor_agno      = models.PositiveIntegerField(
                            default=0,
                            blank=False,
                            null=False,)
    descto_anual    = models.PositiveIntegerField(
                            default=0,
                            blank=False,
                            null=False,
                            help_text='Porcentaje de descuento')

    leyenda_valor   = models.CharField(max_length=40, blank=True, null=True, help_text='Algo como Siempre, por este mes, etc')


    ### >Del boton de registro
    boton_registrarse_texto    = models.CharField(max_length=100, blank=True, null=True, help_text='Registrese o No activo')
    boton_registrarse_url      = models.CharField(max_length=200, blank=True, null=True, help_text='URL para registrarse,  # si es ninguna')


    costo_implementacion  = models.PositiveIntegerField(
                            default=0,
                            blank=False,
                            null=False,
                            help_text='Costo mínimo de implementación')

    notas_internas  = models.TextField(default='', blank=True, null=True)
    notas_web       = models.TextField(default='', blank=True, null=True)
    publico         = models.BooleanField(default=True,help_text='Plan visible en Internet')
    my_order        = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    def __str__(self):
        return "{0}:{1} {2}".format( self.tipo, self.clase, self.nombre)


    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Planes'
        ordering = ("tipo","clase", "valor_mes")
        unique_together = [['tipo', 'clase']]                            


class ContenidoPlan(models.Model):
    plan          = models.ForeignKey(Plan, on_delete=models.CASCADE, default=1)
    objeto        = models.CharField(
        max_length=100, choices=OBJETOS_EN_PLAN.choices, default=OBJETOS_EN_PLAN.USUARIOS, help_text='Nombre del Objeto, usuario, comunas, supermercados, listas, productos por lista, busquedas, emails'
    )
    cantidad      = models.PositiveIntegerField(
                            default=0,
                            blank=False,
                            null=False,
                            help_text='Cantidad Maxima al mes')
    todos         = models.BooleanField(default=False)
    my_order      = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    def __str__(self):
        return "{0}:{1} ".format( self.plan, self.objeto)

    class Meta:
        verbose_name = 'Contenido en Plan'
        verbose_name_plural = 'Contenido en Planes'
        ordering = ("plan","objeto","my_order")
        unique_together = [['plan', 'objeto']]  

class Account(models.Model):
    plan            = models.ForeignKey(Plan, on_delete=models.PROTECT, blank=True, null=True, default=1)
    created         = models.DateTimeField(auto_now_add=True)
    active          = models.BooleanField(default=True)
    def __str__(self):
        return "{0} ".format( self.plan)

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
        # ordering = ("plan","objeto","my_order")
        # unique_together = [['plan', 'objeto']]


class Member(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    direccion   = models.CharField(max_length=250, blank=True, null=True, help_text='Dirección')
    country      = models.ForeignKey(to='precios.Countries', on_delete=models.SET_NULL, blank=True, null=True , help_text='País')
    region      = models.ForeignKey(to='precios.Regions', on_delete=models.SET_NULL, blank=True, null=True, help_text='Región')
    comuna      = models.ForeignKey(to='precios.Cities', on_delete=models.PROTECT, blank=True, null=True, help_text='Comuna')
    account2    = models.ForeignKey(Account, on_delete=models.PROTECT, blank=True, null=True, default=4, help_text='Cuenta')

    def __str__(self) -> str:
        return self.user.username
        
class Contrato(models.Model):
    site = models.ForeignKey(to="precios.Site", on_delete=models.CASCADE, related_name='contratos', help_text='Sitios asociados al contrato')
    plan = models.ForeignKey(Plan, related_name='contratos', on_delete=models.CASCADE, help_text='Planes asociados al contrato')
    member = models.ForeignKey(Member, related_name='contratos', on_delete=models.CASCADE, help_text='Miembros asociados al contrato')
    fecha_inicio = models.DateField(auto_now=True, help_text='Fecha de inicio del contrato')
    fecha_fin = models.DateField(null=True, help_text='Fecha de finalización del contrato')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contrato #{self.id}"
    
    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
    

@receiver(post_save, sender=User)
def create_member(sender, instance, created, **kwargs):
    if created:
        Member.objects.create(user=instance)


##########
class Periodo(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField('active', default=True)
    last_update = models.DateField(auto_now=True)
    closed = models.BooleanField('Data on this period is gotten', default=False)

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        return str(self.end_date.year) + ' - ' + str(calendar.month_name[self.end_date.month])

    @staticmethod
    def autocomplete_search_fields():
        return 'start_date',

    class Meta:
        verbose_name_plural = 'Períodos'
        verbose_name = 'Período'

class MemberStats(models.Model):
    member          = models.ForeignKey(Member, on_delete=models.CASCADE, default=1)
    objeto          = models.CharField(
        max_length=100, choices=OBJETOS_EN_PLAN.choices, default=OBJETOS_EN_PLAN.USUARIOS, help_text='Nombre del Objeto, usuario, comunas, supermercados, listas, productos por lista, busquedas, emails'
    )
    period = models.ForeignKey(Periodo, on_delete=models.PROTECT)
    cuantity = models.BigIntegerField(null=True)

    class Meta:
        verbose_name_plural = 'MemberStats'
        verbose_name = 'MemberStats'
        ordering = ["member", "objeto", "-period"]
        unique_together = ("member", "objeto", "period")

    def period_desc(self):
        return str(self.period.start_date)

    def __str__(self):
        return str(self.objeto)


class Lista(models.Model):
    member          = models.ForeignKey(Member, on_delete=models.CASCADE, default=1)
    nombre_lista    = models.CharField(max_length=250, blank=True, null=True, help_text='Nombre de su lista')
    created         = models.DateTimeField(editable=False,default=timezone.now)
    updated         = models.DateTimeField(auto_now=True,auto_now_add=False)
    public          = models.BooleanField(default=False, help_text='Lista pública')

    def __str__(self) -> str:
        return self.nombre_lista

    @property
    def articleCount(self) -> int:
        return DetalleLista.objects.filter(lista=self).count()

    class Meta:
        verbose_name = 'Lista'
        verbose_name_plural = 'Listas'
        ordering = ("member","nombre_lista")
        unique_together = [['member', 'nombre_lista']]
        

class DetalleLista(models.Model):
    lista           = models.ForeignKey(Lista, on_delete=models.CASCADE, default=1)
    articulo        = models.ForeignKey(to='precios.Articulos', on_delete=models.CASCADE, blank=True, null=True, db_constraint=False)
    cantidad        = models.IntegerField(default=0)

    def __str__(self):
        return "{0}: {1} ".format( self.lista, self.articulo)

    class Meta:
        verbose_name = 'Detalles de Lista'
        verbose_name_plural = 'Detalles de Listas'
