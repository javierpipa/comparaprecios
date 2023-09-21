from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Member
from precios.models import Cities, Regions, Countries

class RegisterUserForm(UserCreationForm):
    email       = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    first_name  = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name   = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class':'form-control'}))
    

    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'



class UpdateMemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ('direccion','country','region','comuna')


    direccion  = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        

        if 'country' in self.data:
            country_id = int(self.data.get('country'))

            try:
                country_id = int(self.data.get('country'))
                self.fields['region'].queryset = Regions.objects.filter(country_id=country_id).order_by('name')
                
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            pass
            # self.fields['region'].queryset = self.instance.region.all()
            # order_by('name')

        
        if 'region' in self.data:
            country_id = int(self.data.get('country'))
            region_id = int(self.data.get('region'))
            # print(f'region_id={region_id}')
            try:
                region_id = int(self.data.get('region'))
                country_id = int(self.data.get('country'))
                self.fields['comuna'].queryset = Cities.objects.filter(country_id=country_id, region_id=region_id).order_by('name')
                
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            pass
            # self.fields['comuna'].queryset = self.instance.country.city_set.order_by('name')
        