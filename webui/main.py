from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from webui import jobs
from database.tables import SessionLocal
from settings import WEBUI_ROOT

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.mount("/static", StaticFiles(directory=WEBUI_ROOT / "static"), name="static")


templates = Jinja2Templates(directory=WEBUI_ROOT / "templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/jobs", response_class=HTMLResponse)
async def get_jobs(request: Request, db: Session = Depends(get_db)):
    all_jobs = jobs.get_jobs(db)
    return templates.TemplateResponse(
        "jobs.html", {"request": request, "jobs": all_jobs}
    )
