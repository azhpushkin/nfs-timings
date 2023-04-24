import logging

from django.core.management.base import BaseCommand
from redengine import RedEngine

from stats.stints import request_api, refresh_stints_info_view


class Command(BaseCommand):
    help = "Launches worker that performs requests to API"

    def handle(self, *args, **options):
        app = RedEngine()

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)

        task_logger = logging.getLogger('redengine.task')
        task_logger.addHandler(handler)

        # register tasks in the worker
        app.task('every 5 seconds')(request_api)
        app.task("after task 'request_api'")(refresh_stints_info_view)

        app.run()
