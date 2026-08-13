import json

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError

from stats.models import Race, User


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


class RaceAccessForm(forms.ModelForm):
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

    class Media:
        css = {'all': ('stats/admin.css',)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['allowed_users'] = self.instance.allowed_users.all()


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
