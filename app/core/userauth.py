from fastapi import APIRouter, Request, Depends
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from config import settings
from datetime import datetime
import models, utils, database, oauth2

router = APIRouter(tags=["Auth"])

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    redirect_uri=settings.redirect_uri,
    client_kwargs={'scope': 'openid profile email https://www.googleapis.com/auth/user.birthday.read'}
)

@router.get('/login/google')
async def login_via_google(request: Request):
    redirect_uri = request.url_for('auth_via_google')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/auth/google')
async def auth_via_google(request: Request, db: Session = Depends(database.get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_data = await oauth.google.parse_id_token(request, token)

    # Use Google People API to get additional profile information
    resp = await oauth.google.get('https://people.googleapis.com/v1/people/me', token=token, params={'personFields': 'birthdays'})
    profile_info = resp.json()

    # Extract birth date if available
    birth_date = None
    birthdays = profile_info.get('birthdays')
    if birthdays:
        # Assuming the first entry is the primary birthday
        birth_date_info = birthdays[0].get('date')
        if birth_date_info:
            birth_date = datetime(
                year=birth_date_info.get('year', 1970),  # Default to 1970 if year is not provided
                month=birth_date_info.get('month', 1),
                day=birth_date_info.get('day', 1)
            ).date()

    # Check if the user already exists
    user = db.query(models.User).filter(models.User.email == user_data['email']).first()
    if not user:
        # If user does not exist, create a new user
        user = models.User(
            name=user_data['name'],
            email=user_data['email'],
            password=utils.hash(utils.generate_random_password()),  # Generate a random password
            date_of_birth=birth_date if birth_date else datetime(1970, 1, 1).date(),  # Use the retrieved birth date or default
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create an access token for the user
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
