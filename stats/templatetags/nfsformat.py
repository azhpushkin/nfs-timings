from django import template

from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
@stringfilter
def split_pilot(value):
    return mark_safe(value.replace(' ', '<br>'))
