from django import forms
from django.forms import BaseFormSet, TextInput, formset_factory
from precios.models import (
    Settings,
    Site, 
    Pages, 
    Marcas,
    Articulos,
    Corporation,
    Site,
    SiteURLResults,
    Vendedores,
    PriceHistory,
    Unifica,
)
from members.models import (
    Plan, 
    TIPO_PLAN,
    ContenidoPlan,
    OBJETOS_EN_PLAN,
    
)
class Unifica_Rule(forms.Form):
    si_fuera = forms.IntegerField(min_value=1, required=True)
    entonces = forms.IntegerField(min_value=1, required=True)
    

class UnifcaForm(forms.ModelForm):
    class Meta:
        model = Unifica
        fields = [
            "si_marca",
            "si_nombre",
            "si_grados2",
            "si_medida_cant",
            "si_unidades",
            "entonces_marca",
            "entonces_nombre",
            "entonces_grados2",
            "entonces_medida_cant",
            "entonces_unidades",
        ]


class CorporationForm(forms.ModelForm):
    class Meta:
        model = Corporation
        fields = [
            "notas",
            "nombre",
        ]
        
class MarcasForm(forms.ModelForm):
    class Meta:
        model = Marcas
        fields = [
            "nombre",
        ]


class CorporationForm(forms.ModelForm):
    class Meta:
        model = Corporation
        fields = [
            "notas",
            "nombre",
        ]


class ArticulosForm(forms.ModelForm):
    class Meta:
        model = Articulos
        fields = [
            "nombre",
            "nombre_original",
            "marca",
            "medida_um",    
            "medida_cant",  
            "unidades",     
            "dimension",    
            "color",        
            "envase",       
            "grados",       
            "ean_13",       
            "tipo",          
        ]
        readonly_fields=('slug')
        # inlines = [SelectorCampoInline]


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = [
            "siteName",
        ]


class SiteURLResultsForm(forms.ModelForm):
    class Meta:
        model = SiteURLResults
        fields = "__all__"
        # fields = [
        #     "site",
        #     "idproducto",
        #     "marca",
        #     "nombre",
        #     "precio",
        #     "medida_cant",
        #     "medida_um",
        #     "categoria",
        #     "descripcion",
        #     "tipo",
        #     "proveedor",
        #     "stock",
        #     "unidades",
        #     "image",
        #     "reglas"
        # ]


class VendedoresForm(forms.ModelForm):
    class Meta:
        model = Vendedores
        fields = []



class PriceHistoryForm(forms.ModelForm):
    class Meta:
        model = PriceHistory
        fields = [
            "Oldprecio",
            # "OldDate",
        ]

def get_sites():
    sitelist = []
    sites = Site.objects.filter(enable=True)
    for site in sites:
        sitelist.append([site.pk,  site.siteName])

    return sitelist

def get_planes():
    planeslist = []
    planes = Plan.objects.filter(tipo=TIPO_PLAN.OFRECEN, publico=True).order_by('my_order')
    for plan in planes:
        planeslist.append([plan.pk,  plan.nombre])

    return planeslist


class NameForm(forms.Form):
    marca       = forms.CharField(label='Marca', max_length=100, required=False)
    nombre      = forms.CharField(label='', max_length=100, required=False)
    # salida_csv  = forms.BooleanField(label='csv')
    # site_id_choices = get_sites()
    # sites = forms.MultipleChoiceField( choices=site_id_choices, label="Supermercado", required=False)

    # # marcas = forms.MultipleChoiceField(choices=site_id_choices, label="Macas", required=False) 
    # def __init__(self, *args, **kwargs):
    #     selectedservices = kwargs.pop('sites')
    #     super(NameForm, self).__init__(*args, **kwargs)
    #     self.fields['service'].choices = [(t.id, t.service) for t in AllServices.objects.filter(industrycode=user.userprofile.industry)]
    #     self.fields['service'].initial = selectedservices

# class CotizaForm2(forms.Form):
#     your_name = forms.CharField(label="Your name", max_length=100)

    

class CotizaForm(forms.Form):
    # class Meta:
    #     model = Site
    #     fields = ('siteURL',)
    
    # siteURL = forms.URLField(initial="http://", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'URL Dominio',}))
    
    planes_choices = get_planes()
    # plan = forms.ChoiceField( choices=planes_choices, label="Plan", required=True, widget=forms.Select(attrs={'class':'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        

       
