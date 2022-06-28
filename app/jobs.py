from typing import List

from sqlalchemy.orm import Session

from datetime import datetime

from pydantic import BaseModel

import tables


class CreateJob(BaseModel):
    url: str


class Job(BaseModel):
    id: int
    url: str
    created_at: datetime

    class Config:
        orm_mode = True


def get_jobs(db: Session) -> List[Job]:
    return db.query(tables.Job).order_by(tables.Job.created_at.desc())


def create_new_job(db: Session, job: CreateJob) -> Job:
    new_job = tables.Job(
        created_at=datetime.now(),
        url=job.url
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job
