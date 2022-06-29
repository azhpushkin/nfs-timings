from datetime import datetime
from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, Session

from database.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime)
    is_running = sa.Column(sa.Boolean)
    url = sa.Column(sa.Text)

    requests = sa.orm.relationship("NFSRequest")


def get_jobs(db: Session) -> List[Job]:
    return db.query(Job).order_by(Job.created_at.desc()).limit(10)


def get_single_job(db: Session, job_id: int) -> Job:
    return db.query(Job).where(Job.id == job_id).first()


def create_new_job(db: Session, job_url: str) -> Optional[Job]:
    is_one_running_now = db.query(Job).where(Job.is_running == True).exists()
    if db.query(is_one_running_now).scalar():
        # Only one currently running might be present
        return None

    new_job = Job(created_at=datetime.now(), url=job_url)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job
