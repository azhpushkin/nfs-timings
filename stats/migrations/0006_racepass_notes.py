# Generated by Django 4.0.6 on 2023-06-13 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0005_racepass_accents_racepass_badges'),
    ]

    operations = [
        migrations.AddField(
            model_name='racepass',
            name='notes',
            field=models.JSONField(default=dict),
        ),
    ]
