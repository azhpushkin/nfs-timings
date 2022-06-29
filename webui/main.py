from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import FastAPI, Form
from starlette.responses import RedirectResponse

from database.base import SessionLocal
from rq import Queue
import database
from settings import WEBUI_ROOT

from worker.worker import  start_job_worker

app = FastAPI()
default_job_url = "https://nfs-stats.herokuapp.com/getmaininfo.json"
queue = Queue(connection=database.redis_conn)


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
        "jobs_list.html",
        {"request": request, "default_job_url": default_job_url, "jobs": all_jobs},
    )


@app.get("/jobs/{job_id}", response_class=HTMLResponse)
def get_single_job(request: Request, job_id: int, db: Session = Depends(get_db)):
    job = database.jobs.get_single_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return templates.TemplateResponse(
        "jobs_detail.html", {"request": request, "job": job}
    )


@app.post("/jobs")
def add_new_job(request: Request, job_url: str = Form(), db: Session = Depends(get_db)):
    job = database.jobs.create_new_job(db, job_url)
    if not job:
        template = "jobs_list.html"
        context = {
            "error": "Some job is already running",
            "default_job_url": job_url,
            "jobs": database.jobs.get_jobs(db),
        }
    else:
        queue.enqueue(start_job_worker, job.id)
        template = "jobs_detail.html"
        context = {"job": job}
    return templates.TemplateResponse(template, {"request": request, **context})


@app.post("/jobs/{job_id}/delete")
def delete_job(request: Request, job_id: int, db: Session = Depends(get_db)):
    job = database.jobs.get_single_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.is_running = False
    db.commit()

    return RedirectResponse(f'/jobs/{job.id}', status_code=302)
