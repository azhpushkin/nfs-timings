from django.db import connection


def recreate_stints_info_view():
    with connection.cursor() as cursor:
        cursor.execute("""
            drop materialized view if exists stints_info
        """)
        cursor.execute("""
            create materialized view stints_info as (
                with stints as (
                    select
                        string_agg(distinct pilot_name, ' OR ') as pilot,
                        team_id,
                        stint,
                        kart,
                        count(*)                       as laps_amount,
                        min(lap_time) as best_lap,
                        array_agg(lap_time order by lap_time) as lap_times
                    from laps
                    group by team_id, stint, kart
                )
                select
                    *,
                    concat(team_id, '-', stint) as stint_id,
                    (select avg(m) from unnest(lap_times[:laps_amount * 0.8]) m) as avg_80,
                    (select avg(m) from unnest(lap_times[:laps_amount * 0.4]) m) as avg_40
                from stints
            )
        """)


def refresh_stints_info_view():
    with connection.cursor() as cursor:
        cursor.execute("""refresh materialized view stints_info""")
