# Generated by Django 3.2.7 on 2021-10-24 17:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('PJI110', '0011_auto_20211021_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='militar_tipo',
            name='DtSv_P_Mil_TipEsc',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='militar_tipo',
            name='DtSv_V_Mil_TipEsc',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='militar_tipo',
            name='NumSv_P_Mil_TipEsc',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='militar_tipo',
            name='NumSv_V_Mil_TipEsc',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
