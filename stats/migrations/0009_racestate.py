# Generated by Django 4.0.6 on 2023-06-22 23:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0008_racepass_show_first_stint'),
    ]

    operations = [
        migrations.CreateModel(
            name='RaceState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('race_time', models.PositiveIntegerField()),
                ('team_states', models.JSONField()),
                ('board_request', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='race_state', to='stats.boardrequest')),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='race_states', to='stats.race')),
            ],
        ),
    ]
