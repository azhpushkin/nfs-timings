from rq import Queue
from starlette.templating import Jinja2Templates

import database
from database.base import SessionLocal
from settings import WEBUI_ROOT


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


rq_queue = Queue(connection=database.redis_conn)


templates = Jinja2Templates(directory=WEBUI_ROOT / "templates")
