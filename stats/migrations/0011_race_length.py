# Generated by Django 4.0.6 on 2023-06-28 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0010_remove_racepass_show_first_stint'),
    ]

    operations = [
        migrations.AddField(
            model_name='race',
            name='length',
            field=models.IntegerField(default=14400, help_text='Race length in seconds. 7200 for MINI, 14400 for 4h, 25200 for 7h, 36000 for 10h'),
        ),
    ]
