from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import settings

Base = declarative_base()

"""
Re-create all the tables with:

from database.base import Base, engine
Base.metadata.create_all(engine)
"""


engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
