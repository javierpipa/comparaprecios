# Generated by Django 3.2.18 on 2023-08-09 21:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0032_auto_20230809_1658'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='areasdespacho',
            name='direccion',
        ),
        migrations.RemoveField(
            model_name='areasdespacho',
            name='no_es_despacho',
        ),
    ]
