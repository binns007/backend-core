from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from schemas import branch
from services import branch as branch_service
from core import oauth2
import database

router = APIRouter(
    prefix="/branches",
    tags=["Branches"]
)

@router.post("/", response_model=branch.BranchResponse, status_code=status.HTTP_201_CREATED)
def create_branch(
    branch_data: branch.BranchCreate,
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    return branch_service.create_branch(branch_data, db, current_user)

@router.get("/", response_model=List[branch.BranchResponse])
def get_branches(
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    return branch_service.get_branches(db, current_user)

@router.put("/{branch_id}", response_model=branch.BranchResponse)
def update_branch(
    branch_id: int,
    branch_data: branch.BranchUpdate,
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    return branch_service.update_branch(branch_id, branch_data, db, current_user)

@router.delete("/{branch_id}")
def delete_branch(
    branch_id: int,
    db: Session = Depends(database.get_db),
    current_user = Depends(oauth2.get_current_user)
):
    return branch_service.delete_branch(branch_id, db, current_user)