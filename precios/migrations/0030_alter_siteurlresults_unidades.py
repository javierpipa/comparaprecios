# Generated by Django 3.2.18 on 2023-08-22 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0029_auto_20230817_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteurlresults',
            name='unidades',
            field=models.FloatField(default=1),
        ),
    ]
