from django import template

from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from stats.processing import int_to_time

register = template.Library()


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
