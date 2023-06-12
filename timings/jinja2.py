from django.template.backends.utils import csrf_input
from django.templatetags.static import static
from django.urls import reverse

from jinja2 import Environment

from stats.templatetags.nfsformat import format_racetime


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {
            'static': static,
            'url': reverse,
            'csrf_token': csrf_input
        }
    )
    env.filters.update({
        'format_racetime': format_racetime
    })
    return env
