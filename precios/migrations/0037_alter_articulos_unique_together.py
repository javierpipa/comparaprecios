# Generated by Django 3.2.18 on 2023-09-28 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0036_alter_articulos_index_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='articulos',
            unique_together={('marca', 'nombre', 'medida_cant', 'grados2', 'unidades', 'envase', 'talla')},
        ),
    ]
