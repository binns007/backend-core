from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from services import auth, dealership as func_dealership
from schemas import user, dealership
import database
import models
from core import utils,oauth2
from core import otp
from datetime import datetime, timedelta

router = APIRouter(
    tags=['Dealership']
)

@router.post("/register-dealership")
def register_dealership(
    dealership_data: dealership.DealershipCreate, db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    return func_dealership.register_dealership_service(dealership_data, db, current_user)

