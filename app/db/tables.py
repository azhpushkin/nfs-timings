import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Jobs(Base):
    __tablename__ = "jobs"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime)
    url = sa.Column(sa.Text)
