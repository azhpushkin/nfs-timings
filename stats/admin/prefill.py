import json

from django import forms
from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse

from stats.models import PrefillOptions


class PrettyJSONField(forms.JSONField):
    """Keep Django's JSON validation while displaying indented JSON."""

    def prepare_value(self, value):
        if value is None:
            return ''
        return json.dumps(value, ensure_ascii=False, indent=2)


class PrefillOptionsForm(forms.ModelForm):
    api_urls = PrettyJSONField(
        widget=forms.Textarea(
            attrs={'class': 'vLargeTextField prefill-json', 'rows': 12}
        )
    )
    race_lengths = PrettyJSONField(
        widget=forms.Textarea(
            attrs={'class': 'vLargeTextField prefill-json', 'rows': 12}
        )
    )

    class Meta:
        model = PrefillOptions
        fields = ('api_urls', 'race_lengths')

    class Media:
        css = {'all': ('stats/prefill_admin.css',)}


@admin.register(PrefillOptions)
class PrefillOptionsAdmin(admin.ModelAdmin):
    form = PrefillOptionsForm
    fields = ('api_urls', 'race_lengths')
    change_form_template = 'admin/stats/prefilloptions/change_form.html'

    class Media:
        css = {'all': ('stats/prefill_admin.css',)}

    def changelist_view(self, request, extra_context=None):
        options = PrefillOptions.get_solo()
        url = reverse('admin:stats_prefilloptions_change', args=(options.pk,))
        return redirect(url)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/fill-defaults/',
                self.admin_site.admin_view(self.fill_defaults_view),
                name='stats_prefilloptions_fill_defaults',
            ),
            path(
                '<path:object_id>/confirm-fill-defaults/',
                self.admin_site.admin_view(self.confirm_fill_defaults_view),
                name='stats_prefilloptions_confirm_fill_defaults',
            ),
        ]
        return custom_urls + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['confirm_fill_defaults_url'] = reverse(
            'admin:stats_prefilloptions_confirm_fill_defaults',
            args=(object_id,),
        )
        return super().change_view(request, object_id, form_url, extra_context)

    def confirm_fill_defaults_view(
        self, request: HttpRequest, object_id: str
    ) -> HttpResponse:
        options = get_object_or_404(PrefillOptions, pk=object_id)
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'original': options,
            'title': 'Confirm filling default prefill options',
            'fill_defaults_url': reverse(
                'admin:stats_prefilloptions_fill_defaults', args=(options.pk,)
            ),
            'change_url': reverse(
                'admin:stats_prefilloptions_change', args=(options.pk,)
            ),
        }
        return render(
            request,
            'admin/stats/prefilloptions/confirm_fill_defaults.html',
            context,
        )

    def fill_defaults_view(self, request: HttpRequest, object_id: str) -> HttpResponse:
        if request.method != 'POST':
            return redirect('admin:stats_prefilloptions_change', object_id)

        options = get_object_or_404(PrefillOptions, pk=object_id)
        options.api_urls = PrefillOptions.DEFAULT_API_URLS
        options.race_lengths = PrefillOptions.DEFAULT_RACE_LENGTHS
        options.save(update_fields=('api_urls', 'race_lengths'))
        self.message_user(request, 'Default prefill options were applied.', messages.SUCCESS)
        return redirect('admin:stats_prefilloptions_change', object_id)
