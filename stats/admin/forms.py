import json
from urllib.parse import urlsplit

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError
from django.utils.html import format_html, format_html_join

from stats.models import PrefillOptions, Race, User


class KartOverridesField(forms.JSONField):
    """One-line JSON object input that treats a blank value as no overrides."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', False)
        kwargs.setdefault('widget', forms.TextInput(attrs={'size': 72}))
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values or value is None:
            return {}
        parsed_value = super().to_python(value)
        if parsed_value is None:
            return {}
        if not isinstance(parsed_value, dict):
            raise ValidationError('Enter a JSON object, for example {"15": 88}.')
        return parsed_value

    def prepare_value(self, value):
        if not isinstance(value, dict):
            return ''
        return json.dumps(value, ensure_ascii=False, separators=(',', ': '))


class RelaxedHttpUrlField(forms.CharField):
    """Accept HTTP(S) URLs with local hostnames such as `simulator`."""

    def validate(self, value):
        super().validate(value)
        if value in self.empty_values:
            return
        parsed_url = urlsplit(value)
        if parsed_url.scheme not in ('http', 'https') or not parsed_url.netloc:
            raise ValidationError('Enter an absolute HTTP or HTTPS URL.')


def prefill_choices(value, expected_type):
    """Ignore malformed JSON configuration entries rather than breaking Admin."""
    if not isinstance(value, list):
        return []
    return [
        (entry['label'], entry['value'])
        for entry in value
        if isinstance(entry, dict)
        and isinstance(entry.get('label'), str)
        and isinstance(entry.get('value'), expected_type)
    ]


class PrefillTextInput(forms.TextInput):
    """A free-form input enhanced with a mobile-safe JS suggestion list."""

    def __init__(self, choices, *args, **kwargs):
        self.choices = choices
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        input_id = (attrs or {}).get('id', f'id_{name}')
        attrs = {
            **(attrs or {}),
            'autocomplete': 'off',
            'class': f"{(attrs or {}).get('class', '')} prefill-input".strip(),
            'data-prefill-panel': f'{input_id}_prefills',
        }
        input_html = super().render(name, value, attrs, renderer)
        choices_html = format_html_join(
            '\n',
            '<button type="button" class="prefill-choice" data-value="{}">{}</button>',
            ((option_value, label) for label, option_value in self.choices),
        )
        return format_html(
            '<span class="prefill-combobox">{}'
            '<span id="{}" class="prefill-panel" hidden>{}</span></span>',
            input_html,
            f'{input_id}_prefills',
            choices_html,
        )


class ApiUrlInput(PrefillTextInput):
    def render(self, name, value, attrs=None, renderer=None):
        input_id = (attrs or {}).get('id', f'id_{name}')
        input_html = super().render(name, value, attrs, renderer)
        return format_html(
            '{} <button type="button" class="button api-url-open" '
            'data-url-input="{}">Open URL</button>',
            input_html,
            input_id,
        )


class RaceAccessForm(forms.ModelForm):
    api_url = RelaxedHttpUrlField(label='API URL')
    kart_overrides = KartOverridesField(
        label='Kart overrides',
        help_text='Optional JSON map of raw kart number to displayed kart number, e.g. {"15": 88}.',
    )
    allowed_users = forms.ModelMultipleChoiceField(
        label='Users with access',
        queryset=User.objects.order_by('username'),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'race-access-checklist'}
        ),
        help_text='Superusers have access to every race whether or not they are selected.',
    )

    class Meta:
        model = Race
        exclude = ('allowed_users',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        prefill_options = PrefillOptions.get_solo()
        api_url_choices = prefill_choices(prefill_options.api_urls, str)
        length_choices = prefill_choices(prefill_options.race_lengths, int)
        self.fields['api_url'].widget = ApiUrlInput(api_url_choices, attrs={'size': 72})
        self.fields['length'].widget = PrefillTextInput(
            [(label, str(value)) for label, value in length_choices],
            attrs={'size': 12, 'inputmode': 'numeric'}
        )
        if self.instance.pk:
            self.initial['allowed_users'] = self.instance.allowed_users.all()

    field_order = (
        'name',
        'created_at',
        'is_active',
        'api_url',
        'length',
        'kart_overrides',
        'allowed_users',
    )

    class Media:
        css = {'all': ('stats/admin.css',)}
        js = ('stats/race_admin.js',)


class UserRaceAccessForm(UserChangeForm):
    allowed_races = forms.ModelMultipleChoiceField(
        label='Races with access',
        queryset=Race.objects.order_by('-created_at'),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'race-access-checklist'}
        ),
        help_text='Superusers have access to every race whether or not they are selected.',
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'is_active', 'is_superuser', 'allowed_races')

    class Media:
        css = {'all': ('stats/admin.css',)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['allowed_races'] = self.instance.allowed_races.all()
