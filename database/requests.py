import sqlalchemy as sa

from database.base import Base


class Request(Base):
    __tablename__ = "requests"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime)
    status = sa.Column(sa.Integer)
    job_id = sa.Column(sa.Integer, sa.ForeignKey("jobs.id"))

    response = sa.Column(sa.Text)
    response_json = sa.Column(sa.JSON)
