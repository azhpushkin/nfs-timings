from datetime import datetime

from pydantic import BaseModel


class CreateJob(BaseModel):
    url: str


class Job(BaseModel):
    id: int
    url: str
    created_at: datetime

    class Config:
        orm_mode = True
