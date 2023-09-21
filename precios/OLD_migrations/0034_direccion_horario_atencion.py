# Generated by Django 3.2.18 on 2023-08-09 21:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('precios', '0033_auto_20230809_1721'),
    ]

    operations = [
        migrations.CreateModel(
            name='Direccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direccion', models.CharField(blank=True, help_text='Dirección', max_length=300, null=True)),
                ('comuna', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='precios.cities')),
                ('site', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='precios.site')),
            ],
        ),
        migrations.CreateModel(
            name='horario_atencion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.ManyToManyField(to='precios.DiasSemana')),
                ('direccion', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='precios.direccion')),
                ('horario', models.ManyToManyField(to='precios.HorasDespacho')),
            ],
            options={
                'verbose_name': 'Horario atencion',
                'verbose_name_plural': 'Horarios de atencion',
            },
        ),
    ]
