# Generated by Django 3.2.18 on 2023-07-24 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0024_auto_20230612_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='allpalabras',
            name='tipo',
            field=models.CharField(blank=True, choices=[('Inútiles', 'Inutil'), ('Unidades de medida', 'Umedida'), ('Sufijos de nombre', 'Sujifo Nombre'), ('Unidades', 'Unidad'), ('Packs', 'Packs'), ('Tallas', 'Talla'), ('Colores', 'Color'), ('Envases', 'Envase')], help_text='Palabra es tipo', max_length=20, null=True),
        ),
    ]
