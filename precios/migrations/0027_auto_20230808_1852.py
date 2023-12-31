# Generated by Django 3.2.18 on 2023-08-08 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0026_auto_20230724_2009'),
    ]

    operations = [
        migrations.CreateModel(
            name='Estadistica_Consulta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clase_consultada', models.CharField(max_length=100)),
                ('elemento_id', models.PositiveIntegerField()),
                ('fecha', models.DateField()),
                ('cantidad_vista', models.PositiveIntegerField(default=0)),
                ('texto_busqueda', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Estadistica Consultas',
                'verbose_name_plural': 'Estadisticas de Consultas',
                'ordering': ('clase_consultada', 'fecha'),
            },
        ),
        migrations.CreateModel(
            name='EstadisticasBlackList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agente', models.CharField(max_length=200, unique=True)),
                ('no_contabilizar', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Estadisticas Black List',
                'verbose_name_plural': 'Estadisticas Black List',
            },
        ),
        migrations.AddIndex(
            model_name='estadistica_consulta',
            index=models.Index(fields=['clase_consultada', 'elemento_id'], name='precios_est_clase_c_af2cc7_idx'),
        ),
        migrations.AddIndex(
            model_name='estadistica_consulta',
            index=models.Index(fields=['fecha'], name='precios_est_fecha_b05646_idx'),
        ),
    ]
