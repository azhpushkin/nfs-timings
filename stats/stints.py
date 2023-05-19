from django.db import connection, DatabaseError


def recreate_stints_info_view():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            drop materialized view if exists stints_info
        """
        )
        cursor.execute(
            f"""
            create materialized view stints_info as (
                with race as (
                    select id, skip_first_stint
                    from race_launches
                    order by is_active desc, created_at desc
                    limit 1
                ),
                stints as (
                    select
                        mode() within group (order by pilot_name) as pilot,
                        teams.number team_id,
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
                    join race on
                        laps.race_id = race.id
                    join teams
                        on laps.team_id = teams.id  
                    group by teams.number, stint
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
