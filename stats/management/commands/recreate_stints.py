from django.core.management.base import BaseCommand

from stats.stints import recreate_stints_view


class Command(BaseCommand):
    help = "Recreates materialized view"

    def handle(self, *args, **options):
        recreate_stints_view()
