# Generated by Django 3.2.18 on 2023-06-08 15:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0015_auto_20230608_1152'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='articulos',
            unique_together={('marca', 'nombre', 'medida_cant', 'grados2', 'unidades', 'envase')},
        ),
    ]
