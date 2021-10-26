# Generated by Django 3.2.7 on 2021-10-16 18:16

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('PJI110', '0005_alter_militar_vsb_mil'),
    ]

    operations = [
        migrations.AddField(
            model_name='militar_dispensa',
            name='Begin_Mil_Disp',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='militar_dispensa',
            name='End_Mil_Disp',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
