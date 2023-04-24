# Generated by Django 4.0.6 on 2023-04-24 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0003_lap_ontrack'),
    ]

    operations = [
        migrations.CreateModel(
            name='RaceLaunch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_url', models.URLField(default='https://nfs-stats.herokuapp.com/getmaininfo.json')),
                ('created_at', models.DateTimeField()),
                ('name', models.CharField(max_length=64)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'race_launches',
            },
        ),
        migrations.DeleteModel(
            name='Config',
        ),
    ]