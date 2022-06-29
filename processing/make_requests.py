import time
import traceback
from datetime import datetime

import requests

from database import jobs, nfs_requests
from database.base import SessionLocal

session = SessionLocal()


def start_job_worker(job_id: int):
    print(f"Starting worker for job {job_id}")
    job = jobs.get_single_job(session, job_id)
    while True:
        print(f"[{job_id}] Requesting {job.url}")
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

        session.add(nfs_request)
        session.commit()
        session.refresh(nfs_request)
        time.sleep(4)
