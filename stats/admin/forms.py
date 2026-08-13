from django import forms

from stats.models import Race, User


class RaceAccessForm(forms.ModelForm):
    allowed_users = forms.ModelMultipleChoiceField(
        label='Users with access',
        queryset=User.objects.order_by('username'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Superusers have access to every race whether or not they are selected.',
    )

    class Meta:
        model = Race
        exclude = ('allowed_users',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['allowed_users'] = self.instance.allowed_users.all()


class UserRaceAccessForm(forms.ModelForm):
    allowed_races = forms.ModelMultipleChoiceField(
        label='Races with access',
        queryset=Race.objects.order_by('-created_at'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Superusers have access to every race whether or not they are selected.',
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'is_active', 'is_superuser', 'allowed_races')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['allowed_races'] = self.instance.allowed_races.all()
