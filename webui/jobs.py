from typing import List

from sqlalchemy.orm import Session

from datetime import datetime

from pydantic import BaseModel

from database.tables import Job as JobTable


class Job(BaseModel):
    id: int
    url: str
    created_at: datetime

    class Config:
        orm_mode = True


def get_jobs(db: Session) -> List[Job]:
    return db.query(JobTable).order_by(JobTable.created_at.desc())


def get_single_job(db: Session, job_id: int) -> List[Job]:
    return db.query(JobTable).where(JobTable.id == job_id).first()


def create_new_job(db: Session, job_url: str) -> Job:
    new_job = JobTable(created_at=datetime.now(), url=job_url)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job
