from fastapi import Form
from fastapi import Request, Depends, HTTPException, APIRouter
from fastapi.responses import HTMLResponse
from rq import Queue
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

import database
from processing.make_requests import start_job_worker
from webui.dependencies import templates, get_db, rq_queue

jobs_router = APIRouter()


default_job_url = "https://nfs-stats.herokuapp.com/getmaininfo.json"


@jobs_router.get("/jobs", response_class=HTMLResponse)
def get_jobs(request: Request, db: Session = Depends(get_db)):
    all_jobs = database.jobs.get_jobs(db)
    return templates.TemplateResponse(
        "jobs_list.html",
        {"request": request, "default_job_url": default_job_url, "jobs": all_jobs},
    )


@jobs_router.get("/jobs/{job_id}", response_class=HTMLResponse)
def get_single_job(request: Request, job_id: int, db: Session = Depends(get_db)):
    job = database.jobs.get_single_job(db, job_id)
    job_requests = database.nfs_requests.get_requests_for_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return templates.TemplateResponse(
        "jobs_detail.html", {"request": request, "job": job, 'requests': job_requests}
    )


@jobs_router.post("/jobs")
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
        rq_queue.enqueue(start_job_worker, job.id)
        template = "jobs_detail.html"
        context = {"job": job}
    return templates.TemplateResponse(template, {"request": request, **context})


@jobs_router.post("/jobs/{job_id}/delete")
def delete_job(request: Request, job_id: int, db: Session = Depends(get_db)):
    job = database.jobs.get_single_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.is_running = False
    db.commit()

    return RedirectResponse(f"/jobs/{job.id}", status_code=302)
