# Generated by Django 4.0.6 on 2022-07-22 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0002_lap_sector_1_lap_sector_2'),
    ]

    operations = [
        migrations.AddField(
            model_name='lap',
            name='ontrack',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]