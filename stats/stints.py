import traceback
from datetime import datetime

import requests
from django.db import connection, DatabaseError
from django.utils import timezone

from stats.models import BoardRequest, RaceLaunch
from stats.processing import process_json


def recreate_stints_info_view(race_id: int):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            drop materialized view if exists stints_info
        """
        )
        cursor.execute(
            f"""
            create materialized view stints_info as (
                with stints as (
                    select
                        mode() within group (order by pilot_name) as pilot,
                        team_id,
                        stint,
                        -- pick most common kart to avoid issues caused by wrong kart
                        mode() within group (order by kart) as kart,
                        count(*)                       as laps_amount,
                        min(race_time) as stint_started_at,
                        min(lap_time) as best_lap,
                        min(sector_1) as best_sector_1,
                        min(sector_2) as best_sector_2,
                        array_agg(lap_time order by lap_time) as lap_times
                    from laps
                    where race_id = {race_id}
                    group by team_id, stint
                )
                select
                    *,
                    concat(team_id, '-', stint) as stint_id,
                    (best_sector_1 + best_sector_2) as best_theoretical,
                    (select avg(m) from unnest(lap_times[:laps_amount * 0.8]) m) as avg_80
                    
                from stints
            )
        """
        )


def refresh_stints_info_view():
    try:
        with connection.cursor() as cursor:
            cursor.execute("""refresh materialized view stints_info""")
    except DatabaseError as e:
        print('Error updating view: ' + str(e))


def request_api():
    current_race: RaceLaunch = RaceLaunch.objects.filter(is_active=True).first()
    if not current_race:
        print('OK: No race in progress')
        return
    api_url = current_race.api_url

    try:
        response = requests.get(api_url)
    except Exception as e:
        BoardRequest.objects.create(
            url=api_url,
            race=current_race,
            created_at=timezone.now(),
            status=0,
            response=traceback.format_exc(),
            response_json={},
            is_processed=True,  # nothing to do here
        )
        print(f'FAIL: request to {api_url} failed')
        return

    try:
        if response.status_code != 200:
            raise ValueError('Not 200 status')
        board_request = BoardRequest.objects.create(
            url=api_url,
            race=current_race,
            created_at=timezone.now(),
            status=response.status_code,
            response=response.content,
            response_json=response.json(),
            is_processed=False,
        )
        print(f'OK: {board_request} saved fine')
        process_json(board_request)
    except:
        print(f'FAIL: Detected issue, status {response.status_code}')
        b = BoardRequest.objects.create(
            url=api_url,
            race=current_race,
            created_at=timezone.now(),
            status=response.status_code,
            response=response.content,
            response_json={},
            is_processed=True,  # nothing to do here as well
        )
        print(f'FAIL: {b} written for debugging purposes')
    else:
        board_request.is_processed = True
        board_request.save(update_fields=['is_processed'])
        print(
            f'OK: {board_request} processed correctly, {board_request.laps.count()} written'
        )
