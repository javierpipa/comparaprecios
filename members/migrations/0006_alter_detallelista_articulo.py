# Generated by Django 3.2.18 on 2023-09-27 19:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0033_auto_20230917_1801'),
        ('members', '0005_auto_20230817_1717'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detallelista',
            name='articulo',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='precios.articulos'),
        ),
    ]
