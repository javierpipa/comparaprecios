# Generated by Django 3.2.18 on 2023-09-28 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0039_auto_20230928_1613'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='unifica',
            name='unique_if_not_deleted',
        ),
        migrations.AddConstraint(
            model_name='unifica',
            constraint=models.UniqueConstraint(fields=('si_marca', 'si_nombre', 'si_medida_cant', 'si_grados2', 'si_unidades', 'si_envase', 'si_talla'), name='unique_if_not_deleted'),
        ),
    ]
