from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import FastAPI, Form


from database.base import SessionLocal
import database
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
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/jobs", response_class=HTMLResponse)
def get_jobs(request: Request, db: Session = Depends(get_db)):
    all_jobs = database.jobs.get_jobs(db)
    return templates.TemplateResponse(
        "jobs_list.html", {"request": request, "jobs": all_jobs}
    )


@app.get("/jobs/{job_id}", response_class=HTMLResponse)
def get_single_job(request: Request, job_id: int, db: Session = Depends(get_db)):
    job = database.jobs.get_single_job(db, job_id)
    return templates.TemplateResponse(
        "jobs_detail.html", {"request": request, "job": job}
    )


@app.post("/jobs")
def add_new_job(request: Request, job_url: str = Form(), db: Session = Depends(get_db)):
    job = database.jobs.create_new_job(db, job_url)
    return templates.TemplateResponse(
        "jobs_detail.html", {"request": request, "job": job}
    )
