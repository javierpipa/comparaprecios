# Generated by Django 3.2.18 on 2023-08-17 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_auto_20230817_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='icono',
            field=models.CharField(blank=True, help_text='Icono del plan', max_length=100, null=True),
        ),
    ]
