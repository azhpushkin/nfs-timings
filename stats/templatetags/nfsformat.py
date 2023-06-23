from django import template
from django.utils.safestring import mark_safe

from stats.models import Race
from stats.models.race import RacePass

register = template.Library()


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


def split_pilot(value):
    return mark_safe(value.replace(' ', '<br>'))


def pilot_surname(value):
    return value.split(' ')[0]


def format_racetime(value):
    return int_to_time(value)[:-3]


def parse_stints_table_columns(value):
    mapping = {'P': 'pilot', 'B': 'best', 'S': 'sectors', 'A': 'average', 'L': 'link'}
    chars = [c.upper() for c in value]
    return {key: (char in chars) for char, key in mapping.items()}


def add_data_from_race_pass(request):
    race_id = request.session.get('current-race')
    race = Race.objects.filter(id=race_id).first() if race_id is not None else None

    if not (request.user.is_authenticated and race):
        return {}

    try:
        race_pass = RacePass.objects.get(race=race, user=request.user)
    except RacePass.DoesNotExist:
        return {}
    else:
        return {
            'user_badges': {
                int(kart): badge for kart, badge in race_pass.badges.items()
            },
            'user_accents': {
                int(kart): accent for kart, accent in race_pass.accents.items()
            },
            'user_notes': {int(kart): note for kart, note in race_pass.notes.items()},
            'show_first_stint': race_pass.show_first_stint,
        }
