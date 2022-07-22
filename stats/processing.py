from stats.models import Lap, BoardRequest, Team


def time_to_int(t: str) -> int:
    # This could sometimes fail, cause right after the pit it might
    # show pit time, but Except will catch it
    h, m, s = t.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


def int_to_time(t: int) -> str:
    t = int(t)
    h = t // 3600
    m = (t - 3600 * h) // 60
    s = t - (h * 3600) - (m * 60)
    return f'{h}:{m}:{s}'


def get_last_lap(s):
    if ':' in s:
        minutes, seconds = s.split(':')
        return float(seconds) + int(minutes)*60
    else:
        return float(s)


def process_json(board_request: BoardRequest):
    data = board_request.response_json.get('onTablo', {})
    if not data.get('isRace'):
        return

    total_race_time = time_to_int(data['totalRaceTime'])

    for team in data['teams']:
        if not (team.get('pilotName') or team.get('teamName')):
            # Probably this is Vovan
            continue

        try:
            pilot_name = team['pilotName']
            last_lap = get_last_lap(team['lastLap'])
            sector_1 = get_last_lap(team['lastLapS1'])
            sector_2 = get_last_lap(team['lastLapS2'])
            kart = int(team['kart'])
            team_number = int(team['number'])
            team_name = team['teamName']
            ontrack_time = time_to_int(team['totalOnTrack'])
        except Exception as e:
            # import ipdb; ipdb.set_trace()
            print(e)
            continue

        process_lap_lime(
            board_request,
            race_time=total_race_time,
            team_number=team_number,
            team_name=team_name,
            pilot_name=pilot_name,
            kart=kart,
            ontrack=ontrack_time,
            lap_time=last_lap,
            sector_1=sector_1,
            sector_2=sector_2
        )


def process_lap_lime(
        board_request: BoardRequest,
        race_time: int,
        team_number: int,
        team_name: str,
        pilot_name: str,
        kart: int,
        ontrack: int,
        lap_time: float,
        sector_1: float,
        sector_2: float,
):
    print('Processing: ', locals())
    if ontrack < 120:
        return

    if kart == 0:
        # No updates, simply ignore this
        return

    if sector_1 > 60 or sector_2 > 60:
        # Something is wrong here
        return

    last_lap_of_team = Lap.objects.filter(team_id=team_number).order_by('-created_at').first()

    if abs(sector_1 + sector_2 - lap_time) > 0.05:
        # Probably, middle of the lap, as sectors do not add up
        return

    if last_lap_of_team and last_lap_of_team.kart == kart and last_lap_of_team.lap_time == lap_time:
        # Same lap probably, skip it
        return

    team, _ = Team.objects.get_or_create(number=team_number, defaults={
        'name': team_name,
    })

    if not last_lap_of_team:
        stint = 1
    elif last_lap_of_team.kart == kart:
        stint = last_lap_of_team.stint
    else:
        stint = last_lap_of_team.stint + 1

    Lap.objects.create(
        board_request=board_request,
        created_at=board_request.created_at,
        team=team,
        pilot_name=pilot_name,
        kart=kart,
        race_time=race_time,
        stint=stint,
        lap_time=lap_time,
        sector_1=sector_1,
        sector_2=sector_2,
    )
