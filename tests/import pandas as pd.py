import pandas as pd
from django.db.models import F, Sum
from .models import SiteURLResults, Articulos, Unifica, Marcas

# Obtener todos los registros de SiteURLResults
queryset = SiteURLResults.objects.all()

# Convertir a un DataFrame de Pandas
df = pd.DataFrame(list(queryset.values()))

# Unificar nombres usando la tabla Unifica
unifica_queryset = Unifica.objects.all()
unifica_df = pd.DataFrame(list(unifica_queryset.values()))

# Iterar sobre las filas de la tabla Unifica y actualizar el DataFrame de SiteURLResults
for _, row in unifica_df.iterrows():
    si_nombre = row['si_nombre']
    si_grados = row['si_grados']
    si_medida_cant = row['si_medida_cant']
    si_unidades = row['si_unidades']
    entonces_nombre = row['entonces_nombre']
    entonces_grados = row['entonces_grados']
    entonces_medida_cant = row['entonces_medida_cant']
    entonces_unidades = row['entonces_unidades']

    # Actualizar los registros que coinciden con las condiciones
    df.loc[(df['nombre'].str.contains(si_nombre, na=False)) & \
           (df['grados'].astype(str) == si_grados) & \
           (df['medida_cant'] == si_medida_cant) & \
           (df['unidades'] == si_unidades),
           ['nombre', 'marca', 'medida_um', 'medida_cant', 'unidades', 'grados']] = \
        [entonces_nombre, row['entonces_marca'], row['entonces_medida_um'], entonces_medida_cant, entonces_unidades, entonces_grados]

# Agrupar por marca, nombre, medida_cant, unidades y grados, y sumar precio y precio_cantidad
aggregated_df = df.groupby(['marca', 'nombre', 'medida_cant', 'unidades', 'grados'], as_index=False).agg({
    'precio': Sum('precio'),
    'precio_cantidad': Sum('precio_cantidad')
})

# Crear registros en la tabla Articulos
for _, row in aggregated_df.iterrows():
    marca = Marcas.objects.get(id=row['marca'])
    nombre = row['nombre']
    medida_cant = row['medida_cant']
    unidades = row['unidades']
    grados = row['grados']

    Articulos.objects.update_or_create(
        marca=marca,
        nombre_original=nombre,
        defaults={
            'nombre': nombre,
            'medida_um': row['medida_um'],
            'medida_cant': medida_cant,
            'unidades': unidades,
            'dimension': row['dimension'],
            'color': row['color'],
            'envase': row['envase'],
            'grados': grados,
            'ean_13': row['ean_13'],
            'tipo': row['tipo'],
            'slug': f'{marca.slug}-{nombre}-{medida_cant}-{unidades}-{grados}',
        }
    )


#########


from django.apps import apps
from pyknow import *

# Definir la base de conocimiento
class MyKnowledgeEngine(KnowledgeEngine):
    pass

def generate_pyknow_rules():
    # Obtener la tabla Unifica
    Unifica = apps.get_model('myapp', 'Unifica')

    # Obtener todas las reglas
    all_rules = Unifica.objects.all()

    # Generar código PyKnow para cada regla
    for rule in all_rules:
        # Crear una nueva clase para la regla
        classname = f"{rule.si_marca.slug}_{rule.si_nombre}_{rule.si_medida_cant}_{rule.si_unidades}"
        new_class = type(classname, (Rule,), {})

        # Definir la condición de la regla
        si_marca = rule.si_marca.nombre
        si_nombre = rule.si_nombre
        si_grados = rule.si_grados
        si_medida_cant = rule.si_medida_cant
        si_unidades = rule.si_unidades
        new_class.salience = rule.contador

        # Definir la acción de la regla
        entonces_marca = rule.entonces_marca.nombre
        entonces_nombre = rule.entonces_nombre
        entonces_grados = rule.entonces_grados
        entonces_medida_cant = rule.entonces_medida_cant
        entonces_unidades = rule.entonces_unidades
        action_code = f"articulo.marca = '{entonces_marca}'; articulo.nombre = '{entonces_nombre}'; articulo.medida_cant = {entonces_medida_cant}; articulo.unidades = {entonces_unidades};"

        # Agregar la regla a la base de conocimiento
        MyKnowledgeEngine.rule(new_class(si_marca=si_marca, si_nombre=si_nombre, si_grados=si_grados, si_medida_cant=si_medida_cant, si_unidades=si_unidades)(action(action_code)))

    # Obtener el código Python generado
    code = MyKnowledgeEngine.__module__
    return code