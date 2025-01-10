from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import engine, Base
from .routes import user

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI HTMX Template")
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(user.router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
