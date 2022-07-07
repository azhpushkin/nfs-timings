from stats.models import Lap, BoardRequest, Team


def time_to_int(t: str) -> int:
    h, m, s = t.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


def int_to_time(t: int) -> str:
    t = int(t)
    h = t // 3600
    m = (t - 3600 * h) // 60
    s = t - (h * 3600) - (m * 60)
    return f'{h}:{m}:{s}'


def process_json(board_request: BoardRequest):
    data = board_request.response_json['onTablo']
    if not data['isRace']:
        return

    total_race_time = time_to_int(data['totalRaceTime'])

    for team in data['teams']:
        pilot_name = team['pilotName']
        last_lap = team['lastLap']
        kart = team['kart']
        team_number = team['number']
        team_name = team['teamName']
        ontrack_time = time_to_int(team['totalOnTrack'])

        process_lap_lime(
            board_request,
            race_time=total_race_time,
            team_number=team_number,
            team_name=team_name,
            pilot_name=pilot_name,
            kart=kart,
            ontrack=ontrack_time,
            lap_time=last_lap
        )


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
