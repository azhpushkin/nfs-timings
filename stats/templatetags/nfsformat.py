from django import template

from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe


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


@register.filter
@stringfilter
def split_pilot(value):
    return mark_safe(value.replace(' ', '<br>'))


@register.filter
@stringfilter
def pilot_surname(value):
    return value.split(' ')[0]


@register.filter
def format_racetime(value):
    return int_to_time(value)[:-3]


@register.filter
def parse_stints_table_columns(value):
    mapping = {'P': 'pilot', 'B': 'best', 'S': 'sectors', 'A': 'average', 'L': 'link'}
    chars = [c.upper() for c in value]
    return {key: (char in chars) for char, key in mapping.items()}
