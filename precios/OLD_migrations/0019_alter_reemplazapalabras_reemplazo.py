# Generated by Django 3.2.18 on 2023-06-09 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0018_alter_articulos_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reemplazapalabras',
            name='reemplazo',
            field=models.CharField(default='', max_length=100),
        ),
    ]
