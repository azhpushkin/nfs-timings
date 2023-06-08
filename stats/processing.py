import traceback
from datetime import time

from processing.response_type import NFSResponseDict, TeamEntry
from stats.models.race import Lap, BoardRequest, Team, Race


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
    return f'{h:2}:{m:02}:{s:02}'


def get_last_lap(s):
    if ':' in s:
        minutes, seconds = s.split(':')
        return float(seconds) + int(minutes) * 60
    else:
        return float(s)


def process_json(board_request: BoardRequest, race: Race):
    try:
        response_parsed: NFSResponseDict = NFSResponseDict.parse_obj(
            board_request.response_json
        )
        if not response_parsed.onTablo.isRace:
            return
    except:
        traceback.print_exc()
        return

    for entry in response_parsed.onTablo.teams:
        try:
            process_lap_entry(
                board_request, race, response_parsed.onTablo.totalRaceTime, entry
            )
        except:
            traceback.print_exc()
            continue


def time_to_float(t: time):
    return t.hour * 3600 + t.minute * 60 + t.second


def process_lap_entry(
    board_request: BoardRequest, race: Race, race_time: time, entry: TeamEntry
):

    if not (entry.lastLapS1 and entry.lastLapS2):
        return

    if (
        entry.lastLapS1
        and entry.lastLapS2
        and (entry.lastLapS1.to_float() > 60 or entry.lastLapS2.to_float() > 60)
    ):
        # Something is wrong here
        return

    team, _ = Team.objects.get_or_create(
        number=entry.number,
        race=race,
        defaults={
            'name': entry.teamName,
        },
    )
    if team.name != entry.teamName:
        team.name = entry.teamName
        team.save(update_fields=['name'])

    last_lap_of_team: Lap = (
        Lap.objects.filter(race=race, team_id=team.id).order_by('-created_at').first()
    )
    print('Processing: ', entry)

    if last_lap_of_team and last_lap_of_team.lap_number == entry.lapCount:
        return

    if (
        entry.lastLapS1
        and entry.lastLapS2
        and abs(
            entry.lastLapS1.to_float()
            + entry.lastLapS2.to_float()
            - entry.lastLap.to_float()
        )
        >= 0.010001
    ):
        # Probably, middle of the lap, as sectors do not add up
        print(
            f'Cannot process {board_request}, sectors of team number={entry.number} do not add up'
            f'(s1: {entry.lastLapS1}, s2: {entry.lastLapS2}, total: {entry.lastLap})'
        )
        return

    if not last_lap_of_team:
        stint = 1
    elif last_lap_of_team.ontrack > time_to_float(entry.totalOnTrack):
        stint = last_lap_of_team.stint + 1
    else:
        stint = last_lap_of_team.stint

    Lap.objects.create(
        race_id=race.id,
        board_request_id=board_request.id,
        team_id=team.id,
        created_at=board_request.created_at,
        pilot_name=entry.pilotName,
        kart=entry.kart,
        race_time=time_to_float(race_time),
        stint=stint,
        ontrack=time_to_float(entry.totalOnTrack),
        lap_time=entry.lastLap.to_float(),
        lap_number=entry.lapCount,
        sector_1=entry.lastLapS1.to_float(),
        sector_2=entry.lastLapS2.to_float(),
    )
    print(f'Created LAP for number={entry.number}, {entry.lapCount}')
