# Generated by Django 3.2.7 on 2021-10-25 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PJI110', '0012_auto_20211024_1436'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='militar_tipo',
            name='Id_Mil',
        ),
        migrations.AddField(
            model_name='militar_tipo',
            name='Id_Mil',
            field=models.ManyToManyField(to='PJI110.Militar'),
        ),
        migrations.RemoveField(
            model_name='militar_tipo',
            name='Id_TipEsc',
        ),
        migrations.AddField(
            model_name='militar_tipo',
            name='Id_TipEsc',
            field=models.ManyToManyField(to='PJI110.TipoEscala'),
        ),
    ]
