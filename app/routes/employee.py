from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from schemas import employee
from services import employee as employee_service
from core import oauth2
import database

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)

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
    current_user = Depends(oauth2.get_current_user)
):
    return employee_service.get_employees(db, current_user)

@router.put("/{employee_id}", response_model=employee.EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_data: employee.EmployeeUpdate,
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    return employee_service.update_employee(employee_id, employee_data, db, current_user)

@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    return employee_service.delete_employee(employee_id, db, current_user)