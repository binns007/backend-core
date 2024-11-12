from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from schemas import form
from services import employee as employee_service
from core import oauth2
import database
import models
import logging
logging.basicConfig(level=logging.DEBUG)


router = APIRouter(
    prefix="/form-builder",
    tags=["Form builder"]
)

@router.post("/templates/", response_model=form.FormTemplateResponse)
def create_form_template(template: form.FormTemplateCreate,
                         db: Session = Depends(database.get_db),
                         current_user: models.User = Depends(oauth2.get_current_user)):
    dealership_id = current_user.dealership_id
    new_template = models.FormTemplate(name=template.name, dealership_id = dealership_id)
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template


@router.post("/templates/{template_id}/fields/", response_model=List[form.FormFieldResponse])
def add_fields_to_template(template_id: int, fields: List[form.FormFieldCreate], db: Session = Depends(database.get_db)):
    try:
        template = db.query(models.FormTemplate).filter(models.FormTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Form template not found")
        
        new_fields = []
        for field in fields:
            new_field = models.FormField(template_id=template_id, **field.dict())
            db.add(new_field)
            new_fields.append(new_field)
        
        db.commit()
        for field in new_fields:
            db.refresh(field)
        
        return new_fields
    except Exception as e:
        print("Error adding fields:", e)
        raise HTTPException(status_code=500, detail="An error occurred while adding fields.")


@router.get("/templates/", response_model=List[form.FormTemplateResponse])
def list_form_templates(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Filter templates by the user's dealership ID
    templates = db.query(models.FormField).filter(
        models.FormTemplate.dealership_id == current_user.dealership_id
    ).all()
    return templates

@router.get("/templates/{template_id}", response_model=form.FormTemplateResponse)
def get_form_template(template_id: int, db: Session = Depends(database.get_db)):
    template = db.query(models.FormTemplate).filter(models.FormTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Form template not found")
    return template



