# Generated by Django 3.2.18 on 2023-08-17 20:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0036_alter_site_crawler'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='corporacion',
            field=models.ForeignKey(default=6, help_text='Grupo de empresas', on_delete=django.db.models.deletion.SET_DEFAULT, to='precios.corporation'),
        ),
    ]
