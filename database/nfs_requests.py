from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import Session

from database.base import Base


class NFSRequest(Base):
    __tablename__ = "requests"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime)
    status = sa.Column(sa.Integer)
    job_id = sa.Column(sa.Integer, sa.ForeignKey("jobs.id"))

    response = sa.Column(sa.Text)
    response_json = sa.Column(sa.JSON)


def get_requests_for_job(db: Session, job_id: int) -> List[NFSRequest]:
    return db.query(NFSRequest).where(NFSRequest.job_id == job_id).order_by(NFSRequest.created_at.desc()).limit(20)


def get_single_request(db: Session, request_id: int) -> NFSRequest:
    return db.query(NFSRequest).where(NFSRequest.id == request_id).first()
