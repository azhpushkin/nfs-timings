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
def format_racetime(value):
    return int_to_time(value)

