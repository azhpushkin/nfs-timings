from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from settings import WEBUI_ROOT
from webui.dependencies import templates
from webui.jobs import jobs_router

app = FastAPI()


app.mount("/static", StaticFiles(directory=WEBUI_ROOT / "static"), name="static")
app.include_router(jobs_router)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
