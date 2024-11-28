from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Existing database settings
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    
    # Existing authentication settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    # Existing AWS settings
    AWS_SERVER_PUBLIC_KEY: str
    AWS_SERVER_SECRET_KEY: str
    
    # Existing Google OAuth settings
    google_client_id: str
    google_client_secret: str
    redirect_uri: str
    
    # New email notification settings
    smtp_server: str = "smtp.gmail.com"  # Default value
    smtp_port: int = 587  # Default value
    smtp_username: str
    smtp_password: str
    from_email: str
    
    # New SMS notification settings (Twilio)
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_from_number: str
    
    # New optional notification settings
    notification_retry_attempts: int = 3  # Default value
    notification_retry_delay: int = 60  # Default delay in seconds
    enable_email_notifications: bool = True  # Feature flag for email
    enable_sms_notifications: bool = True  # Feature flag for SMS
    
    class Config:
        env_file = Path("/home/ubuntu/dev/backend-core/.env")

settings = Settings(
    _env_file=Path("/home/ubuntu/dev/backend-core/.env"), 
    _env_file_encoding="utf-8"
)