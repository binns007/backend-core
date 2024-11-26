from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List,Dict
from schemas import form
from services import employee as employee_service
from core import oauth2, utils
import database
from schemas import employee
import models
import logging
logging.basicConfig(level=logging.DEBUG)


router = APIRouter(
    prefix="/form-builder",
    tags=["Form builder"]
)




async def notify_sales_executive(
    sales_exec_id: int,
    customer_name: str,
    form_id: int,
    db: Session
) -> None:
    """
    Send notification to sales executive about customer form submission
    """
    notification_data = employee.NotificationCreate(
        user_id=sales_exec_id,
        title="Form Submission Notification",
        message=f"Customer {customer_name} has submitted form #{form_id}",
        priority="normal"
    )
    
    await employee_service.create_in_app_notification(
        notification_data=notification_data,
        db=db
    )


@router.post("/forms/{form_instance_id}/submit/customer", response_model=Dict)
async def submit_customer_data(
    form_instance_id: int,
    data: Dict,
    db: Session = Depends(database.get_db)
):
    """
    Customer submits their part of the form data and notifies the sales executive
    """
    # Fetch the form instance with the sales executive information
    form_instance = db.query(models.FormInstance).join(
        models.User, models.FormInstance.generated_by == models.User.id
    ).filter(
        models.FormInstance.id == form_instance_id
    ).first()

    if not form_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form instance not found"
        )

    # Fetch the active template
    template = form_instance.template
    if not template.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Form template is not active"
        )

    # Validate fields to be filled by customer
    fields = db.query(models.FormField).filter(
        models.FormField.template_id == template.id,
        models.FormField.filled_by == "customer"
    ).all()

    field_map = {field.name: field for field in fields}

    # Validate required fields
    for field in fields:
        if field.is_required and field.name not in data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Required field missing: {field.name}"
            )

    responses = []
    for field_name, value in data.items():
        if field_name not in field_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unexpected field: {field_name}"
            )

        field = field_map[field_name]

        if field.field_type == "image":
            filename = utils.generate_unique_filename(value.filename)
            # Upload the image to S3 and get the URL
            s3_url = utils.upload_image_to_s3(value, "saastestd", filename)
            responses.append(models.FormResponse(
                form_instance_id=form_instance.id,
                form_field_id=field.id,
                value=s3_url
            ))
        else:
            # Handle text, number, or date types
            responses.append(models.FormResponse(
                form_instance_id=form_instance.id,
                form_field_id=field.id,
                value=str(value)  # Convert all values to string for storage
            ))

    # Save responses to the database
    db.add_all(responses)
    
    # Update form status
    form_instance.customer_submitted = True
    form_instance.customer_submitted_at = func.now()
    
    db.commit()

    # Send notification to sales executive
    await notify_sales_executive(
        sales_exec_id=form_instance.generated_by,
        customer_name=form_instance.customer_name,
        form_id=form_instance.id,
        db=db
    )

    return {
        "message": "Customer data submitted successfully",
        "form_id": form_instance.id
    }


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


@router.get("/forms/customer-fields/{form_id}/fields", response_model=List[form.FormFieldResponse])
def get_form_fields_by_form_id(
    form_id: int,
    db: Session = Depends(database.get_db),
):
    """
    Fetch fields of a specific form template using the form ID.
    """

    # Fetch the form instance by form_id
    form_instance = db.query(models.FormInstance).filter(
        models.FormInstance.id == form_id
    ).first()

    if not form_instance:
        raise HTTPException(status_code=404, detail="Form instance not found.")

    # Fetch the associated template for the form instance
    template = form_instance.template
    if not template:
        raise HTTPException(status_code=404, detail="Form template not found.")

    # Fetch all fields associated with the template
    fields = db.query(models.FormField).filter(
        models.FormField.template_id == template.id
    ).all()

    if not fields:
        raise HTTPException(status_code=404, detail="No fields found for the form.")

    return fields

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
            s3_url = utils.upload_image_to_s3(value, "hogspot", filename)
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

    return {"message": "Sales data submitted successfully", "form_instance_id": form_instance.id}

@router.post("/forms/amount-data/{form_instance_id}/submit/sales", response_model=dict)
def submit_customer_data(
    form_instance_id: int,
    total_price: float,
    amount_paid: float,
    balance_amount: float,
    vehicle_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """
    Save summarized customer data (pricing and vehicle) into the customers table.
    """
    # Validate form instance ownership and existence
    form_instance = db.query(models.FormInstance).filter(
        models.FormInstance.id == form_instance_id,
        models.FormInstance.generated_by == current_user.id
    ).first()

    if not form_instance:
        raise HTTPException(
            status_code=404,
            detail="Form instance not found or unauthorized."
        )

    # Check if a customer record already exists for this form instance
    existing_customer = db.query(models.Customer).filter(
        models.Customer.form_instance_id == form_instance_id
    ).first()

    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="Customer data for this form instance already exists."
        )

    # Create a new customer record
    new_customer = models.Customer(
        form_instance_id=form_instance_id,
        vehicle_id=vehicle_id,
        total_price=total_price,
        amount_paid=amount_paid,
        balance_amount=balance_amount,
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return {
        "message": "Customer data submitted successfully",
        "customer_id": new_customer.id,
    }


@router.get("/forms/{form_instance_id}/sales-data", response_model=dict)
def get_sales_data(
    form_instance_id: int,
    db: Session = Depends(database.get_db),
):
    """
    Fetch customer data submitted by the sales executive using form_instance_id.
    """
    # Fetch the form instance
    form_instance = db.query(models.FormInstance).filter(
        models.FormInstance.id == form_instance_id
    ).first()

    if not form_instance:
        raise HTTPException(status_code=404, detail="Form instance not found.")

    # Ensure only the creator of the form instance can access it
    

    # Fetch responses filled by the sales executive
    responses = (
        db.query(models.FormResponse)
        .join(models.FormField, models.FormResponse.form_field_id == models.FormField.id)
        .filter(
            models.FormResponse.form_instance_id == form_instance_id,
            models.FormField.filled_by == "sales_executive",
        )
        .all()
    )

    if not responses:
        raise HTTPException(status_code=404, detail="No data found for this form instance.")

    # Prepare response data
    sales_data = {
        "form_instance_id": form_instance.id,
        "customer_name": form_instance.customer_name,
        "created_at": form_instance.created_at,
        "responses": [
            {"field_name": response.form_field.name, "value": response.value}
            for response in responses
        ],
    }

    return sales_data


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
