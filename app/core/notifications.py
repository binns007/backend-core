# core/notifications.py
from fastapi import HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import aiohttp
import logging
from typing import Optional
from schemas.employee import NotificationPriority
from config import settings

# Set up logging
logger = logging.getLogger(__name__)

class NotificationError(Exception):
    """Custom exception for notification-related errors"""
    pass

# Email configuration
EMAIL_CONFIG = {
    "smtp_server": settings.smtp_server,
    "smtp_port": settings.smtp_port,
    "smtp_username": settings.smtp_username,
    "smtp_password": settings.smtp_password,
    "from_email": settings.from_email
}

# SMS configuration (Twilio)
SMS_CONFIG = {
    "account_sid": settings.twilio_account_sid,
    "auth_token": settings.twilio_auth_token,
    "from_number": settings.twilio_from_number
}

async def send_email(
    to_email: str,
    subject: str,
    message: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM
) -> bool:
    """
    Send an email using configured email service (SMTP)
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        message: Email body content
        priority: NotificationPriority enum value
    
    Returns:
        bool: True if successful, raises exception otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['from_email']
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add priority headers if needed
        if priority == NotificationPriority.HIGH:
            msg['X-Priority'] = '1'
            msg['X-MSMail-Priority'] = 'High'
        
        # Add message body
        msg.attach(MIMEText(message, 'plain'))

        # Connect to SMTP server and send
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['smtp_username'], EMAIL_CONFIG['smtp_password'])
            server.send_message(msg)

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        raise NotificationError(f"Email delivery failed: {str(e)}")

async def send_sms(
    to_phone: str,
    message: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM
) -> bool:
    """
    Send SMS using configured SMS service (Twilio)
    
    Args:
        to_phone: Recipient phone number (E.164 format)
        message: SMS content
        priority: NotificationPriority enum value
    
    Returns:
        bool: True if successful, raises exception otherwise
    """
    try:
        client = Client(SMS_CONFIG['account_sid'], SMS_CONFIG['auth_token'])
        
        # Add priority indicator to message if high priority
        if priority == NotificationPriority.HIGH:
            message = "🚨 URGENT: " + message

        # Send message through Twilio
        message = client.messages.create(
            body=message,
            from_=SMS_CONFIG['from_number'],
            to=to_phone
        )

        logger.info(f"SMS sent successfully to {to_phone}, SID: {message.sid}")
        return True

    except TwilioRestException as e:
        logger.error(f"Twilio error sending SMS to {to_phone}: {str(e)}")
        raise NotificationError(f"SMS delivery failed: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to send SMS to {to_phone}: {str(e)}")
        raise NotificationError(f"SMS delivery failed: {str(e)}")

# Utility functions for notification handling
async def format_notification_message(
    template_name: str,
    context: dict,
    notification_type: str
) -> str:
    """
    Format notification message using templates
    
    Args:
        template_name: Name of the template to use
        context: Dictionary of values to insert into template
        notification_type: Type of notification (email/sms)
    
    Returns:
        str: Formatted message
    """

    templates = {
        "task_assignment": {
            "email": """
                New Task Assignment

                Task: {task_name}
                Due Date: {due_date}
                Priority: {priority}

                Details:
                {description}

                Please log in to the system to view more details.
            """,
            "sms": "New task: {task_name} due {due_date}. Priority: {priority}"
        },
        "meeting_reminder": {
            "email": """
                Meeting Reminder

                Meeting: {meeting_name}
                Time: {meeting_time}
                Location: {location}

                Agenda:
                {agenda}
            """,
            "sms": "Reminder: {meeting_name} at {meeting_time}, {location}"
        }
    }
    
    template = templates.get(template_name, {}).get(notification_type)
    if not template:
        raise NotificationError(f"Template {template_name} not found for {notification_type}")
    
    return template.format(**context)

