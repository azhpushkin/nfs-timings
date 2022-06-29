from datetime import datetime
from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, Session

from database.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime)
    url = sa.Column(sa.Text)

    requests = sa.orm.relationship("Request")


def get_jobs(db: Session) -> List[Job]:
    return db.query(Job).order_by(Job.created_at.desc()).limit(10)


def get_single_job(db: Session, job_id: int) -> List[Job]:
    return db.query(Job).where(Job.id == job_id).first()


def create_new_job(db: Session, job_url: str) -> Job:
    new_job = Job(created_at=datetime.now(), url=job_url)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job
