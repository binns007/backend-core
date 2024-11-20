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