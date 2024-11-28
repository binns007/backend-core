from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models
from schemas import branch

def create_branch(branch_data: branch.BranchCreate, db: Session, current_user: models.User):
    if current_user.role != models.RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can create branches"
        )
    
    new_branch = models.Branch(
        **branch_data.model_dump(),
        dealership_id=current_user.dealership_id
    )
    
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)
    return new_branch

def get_branches(db: Session, current_user: models.User):
    return db.query(models.Branch).filter(
        models.Branch.dealership_id == current_user.dealership_id
    ).all()

def update_branch(branch_id: int, branch_data: branch.BranchUpdate, db: Session, current_user: models.User):
    branch_query = db.query(models.Branch).filter(
        models.Branch.id == branch_id,
        models.Branch.dealership_id == current_user.dealership_id
    )
    branch_obj = branch_query.first()
    
    if not branch_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch with id {branch_id} not found"
        )
    
    branch_query.update(branch_data.model_dump(exclude_unset=True))
    db.commit()
    return branch_query.first()

def delete_branch(branch_id: int, db: Session, current_user: models.User):
    branch_query = db.query(models.Branch).filter(
        models.Branch.id == branch_id,
        models.Branch.dealership_id == current_user.dealership_id
    )
    branch = branch_query.first()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch with id {branch_id} not found"
        )
    
    branch_query.delete()
    db.commit()
    return {"message": "Branch deleted successfully"}