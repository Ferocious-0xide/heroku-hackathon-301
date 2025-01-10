from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import user as models
from ..schemas import user as schemas

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/form")
async def show_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@router.post("/submit")
async def create_user(
    request: Request,
    email: str = Form(...),
    address: str = Form(...),
    comments: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = models.User(email=email, address=address, comments=comments)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return templates.TemplateResponse(
        "form.html",
        {
            "request": request,
            "message": "Submission successful!"
        }
    )
