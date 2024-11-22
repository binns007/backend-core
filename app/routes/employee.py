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
def send_in_app_notification(
    notification_data: employee.NotificationCreate,
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user_authenticated)
):
    """
    Send an in-app notification to a specific user
    Requires authentication and admin privileges
    """
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can send notifications"
        )
    
    
    return employee_service.create_in_app_notification(notification_data, db)


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