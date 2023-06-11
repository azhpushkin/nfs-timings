from django.db import connection, DatabaseError


def recreate_stints_view():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            drop materialized view if exists stints
        """
        )
        cursor.execute(
            f"""
            create materialized view stints as (
                with stints as (
                    select
                        race_id,
                        
                        -- pick most common kart number to avoid issues caused by wrong kart 
                        --  (0 means kart number is not set)
                        mode() within group (order by case when kart = 0 then null else kart end) as kart,
                        
                        (array_agg(pilot_name order by lap_number desc))[1] as pilot,
                        team,
                        stint,
                        min(race_time) as stint_started_at,
                        
                        count(*) as laps_amount,
                        array_agg(lap_time order by lap_time) as lap_times,
                        
                        min(lap_time) as best_lap,
                        min(sector_1) as best_sector_1,
                        min(sector_2) as best_sector_2
                        
                    from laps
                    group by race_id, team, stint
                )
                select
                    *,
                    -- TODO: coalesce (kart, -1) to indicate unknown kart
                    concat(team, '-', stint) as stint_id,
                    (best_sector_1 + best_sector_2) as best_theoretical,
                    (select avg(m) from unnest(lap_times[:laps_amount * 0.8]) m) as avg_80
                from stints
                -- only 20 teams in BG, usually mechanics test karts during race using team #44 or team #69
                where team <= 20
            )
        """
        )


def refresh_stints_view():
    try:
        with connection.cursor() as cursor:
            cursor.execute("""refresh materialized view stints_info""")
    except DatabaseError as e:
        print('Error updating view: ' + str(e))
