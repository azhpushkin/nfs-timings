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
                        -- pick most common kart to avoid issues caused by wrong kart
                        mode() within group (order by kart) as kart,
                        count(*)                       as laps_amount,
                        min(lap_time) as best_lap,
                        min(sector_1) as best_sector_1,
                        min(sector_2) as best_sector_2,
                        array_agg(lap_time order by lap_time) as lap_times
                    from laps
                    group by team_id, stint
                )
                select
                    *,
                    concat(team_id, '-', stint) as stint_id,
                    (best_sector_1 + best_sector_2) as best_theoretical,
                    (select avg(m) from unnest(lap_times[:laps_amount * 0.8]) m) as avg_80
                    
                from stints
            )
        """)


def refresh_stints_info_view():
    with connection.cursor() as cursor:
        cursor.execute("""refresh materialized view stints_info""")
