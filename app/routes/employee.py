from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from schemas import employee
from services import employee as employee_service
from core import oauth2
import database
import models

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)

# Static routes first



@router.get("/notifications", response_model=List[employee.NotificationResponse])
def get_my_notifications(
    only_unread: bool = False,
    limit: int = 20,
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user_authenticated)
):
    """
    Get notifications for the current user
    """
    return employee_service.get_user_notifications(
        current_user.id, 
        db, 
        only_unread, 
        limit
    )


@router.post("/{employee_id}/notify", status_code=status.HTTP_200_OK)
async def notify_employee_endpoint(
    employee_id: int,
    notification_data: employee.SingleNotification,
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user_authenticated)
):
    """Send a notification to a specific employee"""
    return await employee_service.notify_employee(employee_id, notification_data, db, current_user)

@router.post("/notify-batch", status_code=status.HTTP_200_OK)
async def notify_batch_employees_endpoint(
    notification_data: employee.BatchNotification,
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user_authenticated)
):
    """Send notifications to multiple employees based on filters"""
    return await employee_service.notify_batch_employees(notification_data, db, current_user)


@router.get("/roles", response_model=List[employee.RoleResponse])
def get_roles(
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """Get list of all available roles"""
    return employee_service.get_available_roles(db, current_user)

@router.post("/", response_model=employee.EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee_data: employee.EmployeeCreate,
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    return employee_service.create_employee(employee_data, db, current_user)

@router.get("/", response_model=List[employee.EmployeeResponse])
def get_employees(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user_authenticated)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return employee_service.get_employees(db, current_user)

@router.post("/activate", status_code=status.HTTP_200_OK)
def activate_employee(
    activation_data: employee.EmployeeActivation,
    db: Session = Depends(database.get_db)
):
    return employee_service.activate_employee_account(activation_data, db)



# Dynamic routes with path parameters last
@router.get("/{employee_id}", response_model=employee.EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """Get detailed information about a specific employee"""
    return employee_service.get_employee_by_id(employee_id, db, current_user)

@router.put("/{employee_id}", response_model=employee.EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_data: employee.EmployeeUpdate,
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    return employee_service.update_employee(employee_id, employee_data, db, current_user)

@router.patch("/{employee_id}/role", response_model=employee.EmployeeResponse)
def update_role(
    employee_id: int,
    role_update: employee.RoleUpdate,
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """Update the role of an employee"""
    return employee_service.update_employee_role(employee_id, role_update, db, current_user)

@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    return employee_service.delete_employee(employee_id, db, current_user)

@router.post("/notifications", response_model=employee.NotificationResponse)
async def send_in_app_notification(
    notification_data: employee.NotificationCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user_authenticated)
):
    """
    Send an in-app notification to a specific user
    Requires authentication and admin privileges
    """
    if current_user.role != models.RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can send notifications"
        )
    
    return await employee_service.create_in_app_notification(notification_data, db, current_user)


@router.patch("/notifications/read")
def mark_notifications_read(
    notification_ids: List[int],
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user_authenticated)
):
    """
    Mark specific notifications as read
    """
    return {
        "updated_count": employee_service.mark_notifications_as_read(
            notification_ids, 
            current_user.id, 
            db
        )
    }


@router.patch("/forms/{form_instance_id}/verify-sales", response_model=dict)
def verify_sales_data(
    form_instance_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Verify sales data for a form instance and mark it as sales verified.
    """
    # Fetch the form instance
    form_instance = db.query(models.FormInstance).filter(
        models.FormInstance.id == form_instance_id
    ).first()

    if not form_instance:
        raise HTTPException(status_code=404, detail="Form instance not found.")

    # Ensure only sales executives or admins can verify
    if current_user.role not in [models.RoleEnum.sales_executive, models.RoleEnum.admin]:
        raise HTTPException(status_code=403, detail="Unauthorized to verify sales data.")

    # Check if customer has submitted data
    if not form_instance.customer_submitted:
        raise HTTPException(status_code=400, detail="Customer data not yet submitted.")

    # Mark as sales verified
    form_instance.sales_verified = True
    db.commit()

    return {
        "message": "Sales data verified successfully.",
        "form_instance_id": form_instance.id
    }


@router.get("/forms/sales-verified", response_model=List[dict])
def get_sales_verified_forms(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Retrieve all sales verified form instances with customer and sales data.
    """
    # Filter form instances that are sales verified, belonging to the user's dealership
    form_instances = (
        db.query(models.FormInstance)
        .join(models.FormTemplate)
        .filter(
            models.FormTemplate.dealership_id == current_user.dealership_id,
            models.FormInstance.sales_verified == True
        )
        .all()
    )

    verified_forms = []
    for form_instance in form_instances:
        # Fetch customer data
        customer = db.query(models.Customer).filter(
            models.Customer.form_instance_id == form_instance.id
        ).first()

        # Fetch customer and sales responses
        customer_responses = (
            db.query(models.FormResponse)
            .join(models.FormField)
            .filter(
                models.FormResponse.form_instance_id == form_instance.id,
                models.FormField.filled_by == "customer"
            )
            .all()
        )

        sales_responses = (
            db.query(models.FormResponse)
            .join(models.FormField)
            .filter(
                models.FormResponse.form_instance_id == form_instance.id,
                models.FormField.filled_by == "sales_executive"
            )
            .all()
        )

        # Prepare customer details dictionary with default values if customer is None
        customer_details = {
            "total_price": customer.total_price if customer else None,
            "amount_paid": customer.amount_paid if customer else None,
            "balance_amount": customer.balance_amount if customer else None,
        }

        verified_forms.append({
            "form_instance_id": form_instance.id,
            "customer_name": form_instance.customer_name,
            "customer_data": [
                {"field_name": resp.form_field.name, "value": resp.value}
                for resp in customer_responses
            ],
            "sales_data": [
                {"field_name": resp.form_field.name, "value": resp.value}
                for resp in sales_responses
            ],
            "customer_details": customer_details
        })

    return verified_forms


@router.get("/forms/customer-submitted", response_model=List[dict])
def get_customer_submitted_forms(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Retrieve all customer submitted form instances with customer data.
    """
    # Filter form instances that are customer submitted, belonging to the user's dealership
    form_instances = (
        db.query(models.FormInstance)
        .join(models.FormTemplate)
        .filter(
            models.FormTemplate.dealership_id == current_user.dealership_id,
            models.FormInstance.customer_submitted == True,
            models.FormInstance.sales_verified == False
        )
        .all()
    )

    submitted_forms = []
    for form_instance in form_instances:
        # Fetch customer responses
        customer_responses = (
            db.query(models.FormResponse)
            .join(models.FormField)
            .filter(
                models.FormResponse.form_instance_id == form_instance.id,
                models.FormField.filled_by == "customer"
            )
            .all()
        )

        submitted_forms.append({
            "form_instance_id": form_instance.id,
            "customer_name": form_instance.customer_name,
            "customer_submitted_at": form_instance.customer_submitted_at,
            "customer_data": [
                {"field_name": resp.form_field.name, "value": resp.value}
                for resp in customer_responses
            ]
        })

    return submitted_forms