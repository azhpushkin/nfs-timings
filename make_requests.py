from redengine import RedEngine
import requests

import django
import os

# Setup django to use models
os.environ['DJANGO_SETTINGS_MODULE'] = 'timings.settings'
django.setup()

from stats.models import Lap, Config

app = RedEngine()


@app.task('every 5 seconds')
def request_api():
    config = Config.objects.first()
    if config and config.api_url:
        api_url = config.api_url
    else:
        api_url = ''

    try:
        response = requests.get(job.url)
    except Exception as e:
        nfs_request = nfs_requests.NFSRequest(
            created_at=datetime.now(),
            status=0,
            job_id=job.id,
            response=traceback.format_exc(),
            response_json={},
        )
    else:
        nfs_request = nfs_requests.NFSRequest(
            created_at=datetime.now(),
            status=response.status_code,
            job_id=job.id,
            response=traceback.format_exc(),
            response_json=response.json(),
        )

    data = BoardRequest
    print('hi', Lap.objects.count())


if __name__ == "__main__":
    app.run()