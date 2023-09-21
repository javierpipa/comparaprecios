from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterUserForm, UpdateMemberForm
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import (
    cache_page, 
    never_cache, 
)

from django.http import JsonResponse


from precios.models import (
    Countries,
    Cities,
    Regions
)
from precios.pi_functions import safe_session, get_sessions

from members.models import (
    Member, 
    Lista, 
    ContenidoPlan,
    Periodo,
    MemberStats,

)
######
the_period   = Periodo.objects.filter(active=True).order_by('start_date').first()
######



# AJAX
def get_costo_despacho(request):
    costo_despacho = None
    if 'costo_despacho' in request.session:
        costo_despacho = request.session['costo_despacho']

    table = {
        'costo_despacho':costo_despacho, 
    }
    
    return JsonResponse(table, status=200, safe=False)

def set_costo_despacho(request):
    if request.method == 'GET' and request.is_ajax():
        costo_despacho = request.GET.get('costo_despacho')
        request.session['costo_despacho'] = costo_despacho


    return JsonResponse({'message':'ok'}, safe=False)
    
def load_countries(request):
    if request.method == 'GET' and request.is_ajax():
        countries = Countries.objects.all()

        return render(request, 'members/includes/countries_dropdown_list_options.html', {'countries': countries})

def load_regions(request):
    country_id = request.GET.get('country_id')
    country_label, region_label, comuna_label = safe_session(request, country_id, None, None)
    
    if country_id != '':
        regions = Regions.objects.filter(country_id=country_id).all()
    else:
        regions = {''}
    return render(request, 'members/includes/regions_dropdown_list_options.html', {'regions': regions})


def load_cities(request):
    country_id = request.GET.get('country_id')
    region_id = request.GET.get('region_id')
    country_label, region_label, comuna_label = safe_session(request, country_id, region_id, None)


    cities = Cities.objects.filter(country_id=country_id, region_id=region_id).all()
    return render(request, 'members/includes/city_dropdown_list_options.html', {'cities': cities})

def set_cobertura(request):
    country_id = request.GET.get('country_id')
    region_id = request.GET.get('region_id')
    comuna_id = request.GET.get('comuna_id')

    country_label, region_label, comuna_label = safe_session(request, country_id, region_id, comuna_id)
    table = {
        'country_label':country_label, 
        'region_label': region_label, 
        'comuna_label': comuna_label
    }
    
    return JsonResponse(table, status=200, safe=False)

def get_cobertura(request):
    country_id, region_id, comuna_id = get_sessions(request)


    country_label, region_label, comuna_label = safe_session(request, country_id, region_id, comuna_id)
    table = {
        'country_id': country_id,
        'country_label':country_label, 
        'region_id': region_id,
        'region_label': region_label, 
        'comuna_id': comuna_id,
        'comuna_label': comuna_label
    }
    
    return JsonResponse(table, status=200, safe=False)

@never_cache
@transaction.atomic
###############################
def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        # member_form = UpdateMemberForm(request.POST, instance=request.user.member)
        if form.is_valid() :
            # and member_form.is_valid():
            form.save()
            
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = authenticate(request, username=username, password=password)
            login(request, user)
            # member_form.save()
            messages.success(request,"Usuario registrado.")
            return redirect('pages-root')
    else:
        form = RegisterUserForm()

    return render(request, 'members/register_user.html', {
        'form' :form,
    })

@never_cache
def home(request):
    user = None
    if request.user.is_authenticated:
        user            = request.user
        member          = Member.objects.get(user=user)
        listas          = Lista.objects.filter(member=member)
        contenidoPlan   = ContenidoPlan.objects.filter(plan=user.member.account2.plan).order_by('my_order')
        stats           = MemberStats.objects.filter(member=member).order_by('objeto','period')
    else:
        listas = None
        contenidoPlan = None
        stats = None


    return render(request, 'members/home.html', {"user":user, 'listas': listas, 'contenidoPlan':contenidoPlan, 'stats': stats})

@never_cache
@login_required
def update_member(request):
    if request.method == "POST":
        member_form = UpdateMemberForm(request.POST, instance=request.user.member)
        if  member_form.is_valid():
            
            country_id = request.POST.get('country')
            comuna_id = request.POST.get('comuna')
            region_id = request.POST.get('region')
            safe_session(request, country_id, region_id, comuna_id)
            
            member_form.save()
            return redirect("pages-root")
    else:
        member_form = UpdateMemberForm(instance=request.user.member)
        safe_session(request, None, None, None)

    return render(request, 'members/update_member.html', {"member_form": member_form})

@never_cache
def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            messages.success(request,"Conectado.")
            return redirect('pages-root')
            
        else:
            messages.success(request,"Error.. No pudo logear, intenta nuevamente.")
            return redirect('members:login')
    else:
        return render(request, 'members/login.html', {})

@never_cache
@login_required
def logout_user(request):
    logout(request)
    messages.success(request,"Desconectado.")
    safe_session(request, None, None, None)
    return redirect('pages-root')
    

