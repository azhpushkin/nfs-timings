from stats.models import Lap, BoardRequest, Team


def process_lap_lime(
    board_request: BoardRequest,
    race_time: int,
    team_number: int,
    team_name: str,
    pilot_name: str,
    kart: int,
    ontrack: int,
    lap_time: float
):
    if ontrack < 120:
        return

    if lap_time > 50:
        return

    if race_time < 300:
        # First 5 minutes might be full of fights, ignore them
        return

    last_lap_of_team = Lap.objects.filter(team_number=team_number).order_by('-created_at').first()

    if last_lap_of_team and last_lap_of_team.kart == kart and last_lap_of_team.lap_time == lap_time:
        # Same lap probably, skip it
        return

    if not Team.objects.filter(number=team_number):
        Team.objects.create(number=team_number, name=team_name)

    if not last_lap_of_team:
        stint = 1
    elif last_lap_of_team.kart == kart:
        stint = last_lap_of_team.stint
    else:
        stint = last_lap_of_team.stint + 1

    new_lap = Lap.objects.create(
        board_request=board_request,
        created_at=board_request.created_at,
        team_number=team_number,
        pilot_name=pilot_name,
        kart=kart,
        race_time=race_time,
        stint=stint,
        lap_time=lap_time,
    )

