from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from schemas import form
from services import employee as employee_service
from core import oauth2
import database
import models

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)

@router.post("/templates/", response_model=form.FormTemplateResponse)
def create_form_template(template: form.FormTemplateCreate, db: Session = Depends(database.get_db)):
    new_template = models.FormTemplate(name=template.name)
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template

@router.post("/templates/{template_id}/fields/", response_model=form.FormFieldResponse)
def add_field_to_template(template_id: int, field: form.FormFieldCreate, db: Session = Depends(database.get_db)):
    template = db.query(models.FormTemplate).filter(models.FormTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Form template not found")
    
    new_field = models.FormField(template_id=template_id, **field.dict())
    db.add(new_field)
    db.commit()
    db.refresh(new_field)
    return new_field

@router.get("/templates/", response_model=List[form.FormTemplateResponse])
def list_form_templates(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Filter templates by the user's dealership ID
    templates = db.query(models.FormTemplate).filter(
        models.FormTemplate.dealership_id == current_user.dealership_id
    ).all()
    return templates

@router.get("/templates/{template_id}", response_model=form.FormTemplateResponse)
def get_form_template(template_id: int, db: Session = Depends(database.get_db)):
    template = db.query(models.FormTemplate).filter(models.FormTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Form template not found")
    return template



