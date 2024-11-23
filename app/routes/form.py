from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List
from schemas import form
from services import employee as employee_service
from core import oauth2, utils
import database
import models
import logging
logging.basicConfig(level=logging.DEBUG)


router = APIRouter(
    prefix="/form-builder",
    tags=["Form builder"]
)


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


@router.get("/templates/", response_model=List[form.FormListResponse])
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



@router.put("/templates/{template_id}/activate", response_model=dict)
def activate_form_template(
    template_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Admin endpoint to activate a form template.
    """

    # Fetch the template
    template = db.query(models.FormTemplate).filter(models.FormTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Form template not found.")

    # Ensure the current user belongs to the same dealership
    if template.dealership_id != current_user.dealership_id:
        raise HTTPException(status_code=403, detail="Unauthorized action.")

    # Deactivate other templates for the same dealership
    db.query(models.FormTemplate).filter(
        models.FormTemplate.dealership_id == template.dealership_id,
        models.FormTemplate.is_active == True
    ).update({"is_active": False})
    db.commit()

    # Activate the new template
    template.is_active = True
    template.last_activated_at = func.now()  # Set activation time
    db.commit()
    db.refresh(template)

    return {"message": f"Template '{template.name}' has been activated successfully."}


@router.get("/forms/active", response_model=List[form.FormFieldResponse])
def get_active_form_fields(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Fetch fields of the most recently activated form template for the current user's dealership.
    """

    dealership_id = current_user.dealership_id
    if not dealership_id:
        raise HTTPException(status_code=404, detail="Dealership not found for the user.")

    # Fetch the most recently activated template for the dealership
    active_template = db.query(models.FormTemplate).filter(
        models.FormTemplate.dealership_id == dealership_id,
        models.FormTemplate.is_active == True
    ).first()

    if not active_template:
        raise HTTPException(status_code=404, detail="No active form template found for this dealership.")

    # Fetch all fields associated with the active form template
    fields = db.query(models.FormField).filter(
        models.FormField.template_id == active_template.id
    ).all()

    if not fields:
        raise HTTPException(status_code=404, detail="No fields found for the active form.")

    return fields



@router.post("/forms/create", response_model=dict)
def create_form_instance(
    customer_name: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Sales executive generates a new form instance for a customer.
    """
    dealership_id = current_user.dealership_id
    if not dealership_id:
        raise HTTPException(status_code=404, detail="Sales executive is not associated with a dealership.")

    # Fetch the active form template for the dealership
    template = db.query(models.FormTemplate).filter(
        models.FormTemplate.dealership_id == dealership_id,
        models.FormTemplate.is_active == True
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="No active form template found for this dealership.")

    # Create a new form instance
    form_instance = models.FormInstance(
        template_id=template.id,
        generated_by=current_user.id,
        customer_name=customer_name    )

    db.add(form_instance)
    db.commit()
    db.refresh(form_instance)

    return {"message": "Form instance created successfully.", "form_instance_id": form_instance.id}




@router.post("/forms/{form_instance_id}/submit/sales", response_model=dict)
def submit_sales_data(
    form_instance_id: int,
    data: dict,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """
    Sales executive submits their part of the form data.
    """
    # Fetch the form instance
    form_instance = db.query(models.FormInstance).filter(
        models.FormInstance.id == form_instance_id,
        models.FormInstance.generated_by == current_user.id
    ).first()

    if not form_instance:
        raise HTTPException(status_code=404, detail="Form instance not found or unauthorized.")

    # Fetch the active template
    template = form_instance.template
    if not template.is_active:
        raise HTTPException(status_code=400, detail="Form template is not active.")

    # Validate fields to be filled by sales executive
    fields = db.query(models.FormField).filter(
        models.FormField.template_id == template.id,
        models.FormField.filled_by == "sales_executive"
    ).all()

    field_map = {field.name: field for field in fields}

    responses = []
    for field_name, value in data.items():
        if field_name not in field_map:
            raise HTTPException(status_code=400, detail=f"Unexpected field: {field_name}.")

        field = field_map[field_name]

        if field.field_type == "image":
            filename = utils.generate_unique_filename(value.filename)

            # Upload the image to S3 and get the URL
            s3_url =utils.upload_image_to_s3(value,"hogspot",filename)
            responses.append(models.FormResponse(
                form_instance_id=form_instance.id,
                form_field_id=field.id,
                value=s3_url
            ))
        else:
            # Handle text or other simple types
            responses.append(models.FormResponse(
                form_instance_id=form_instance.id,
                form_field_id=field.id,
                value=value
            ))

    # Save responses to the database
    db.add_all(responses)
    db.commit()

    return {"message": "Sales data submitted successfully."}




# @router.post("/forms/{form_instance_id}/submit/customer", response_model=dict)
# def submit_customer_data(
#     form_instance_id: int,
#     data: dict,
#     db: Session = Depends(database.get_db),
#     s3_client: S3Client = Depends(get_s3_client),  # Inject S3 client
# ):
#     """
#     Customer submits their part of the form data.
#     """
#     # Fetch the form instance
#     form_instance = db.query(models.FormInstance).filter(
#         models.FormInstance.id == form_instance_id
#     ).first()

#     if not form_instance:
#         raise HTTPException(status_code=404, detail="Form instance not found.")

#     # Fetch the active template
#     template = form_instance.template
#     if not template.is_active:
#         raise HTTPException(status_code=400, detail="Form template is not active.")

#     # Validate fields to be filled by customer
#     fields = db.query(models.FormField).filter(
#         models.FormField.template_id == template.id,
#         models.FormField.filled_by == "customer"
#     ).all()

#     field_map = {field.name: field for field in fields}

#     responses = []
#     for field_name, value in data.items():
#         if field_name not in field_map:
#             raise HTTPException(status_code=400, detail=f"Unexpected field: {field_name}.")

#         field = field_map[field_name]

#         if field.field_type == "image":
#             # Upload the image to S3 and get the URL
#             s3_url = upload_image_to_s3(s3_client, value, folder="form-images")
#             responses.append(models.FormResponse(
#                 form_instance_id=form_instance.id,
#                 form_field_id=field.id,
#                 value=s3_url
#             ))
#         else:
#             # Handle text or other simple types
#             responses.append(models.FormResponse(
#                 form_instance_id=form_instance.id,
#                 form_field_id=field.id,
#                 value=value
#             ))

#     # Save responses to the database
#     db.add_all(responses)
#     db.commit()

#     return {"message": "Customer data submitted successfully."}
