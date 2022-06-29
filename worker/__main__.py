import requests
import traceback
import time


from redis import Redis
from rq import Queue

import database
from database.base import SessionLocal

queue = Queue(connection=Redis())
session = SessionLocal()


def start_job_worker(job_id: int):
    job = database.jobs.get_single_job(session, job_id)
    while True:
        try:
            response = requests.get("https://nfs-stats.herokuapp.com/getmaininfo.json")
        except Exception as e:
            print(e)
        else:
            print(response)

        time.sleep(1)
