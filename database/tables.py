import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import settings

Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime)
    url = sa.Column(sa.Text)

    requests = sa.orm.relationship('Request')


class Request(Base):
    __tablename__ = 'requests'

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime)
    status = sa.Column(sa.Integer)
    job_id = sa.Column(sa.Integer, sa.ForeignKey('jobs.id'))

    response = sa.Column(sa.Text)
    response_json = sa.Column(sa.JSON)


engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
