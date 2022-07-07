# Generated by Django 4.0.6 on 2022-07-07 19:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BoardRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('url', models.TextField()),
                ('status', models.IntegerField()),
                ('response', models.TextField()),
                ('response_json', models.JSONField()),
                ('is_processed', models.BooleanField(db_index=True, default=False)),
            ],
            options={
                'db_table': 'requests',
            },
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'teams',
            },
        ),
        migrations.CreateModel(
            name='Lap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('team_number', models.IntegerField(db_index=True)),
                ('pilot_name', models.TextField()),
                ('kart', models.TextField(db_index=True)),
                ('race_time', models.IntegerField()),
                ('stint', models.IntegerField()),
                ('lap_time', models.FloatField()),
                ('board_request', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='laps', to='stats.boardrequest')),
            ],
            options={
                'db_table': 'laps',
            },
        ),
    ]
