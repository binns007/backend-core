from email.mime.text import MIMEText
import smtplib
import random, string
import random
from config import settings


def send_otp(email: str, otp: int):
    msg = MIMEText(f"Your OTP is {otp}")
    msg['Subject'] = 'Verify your email'
    msg['From'] = 'thegluping@gmail.com'
    msg['To'] = email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('thegluping@gmail.com', 'nagdlooaljrggarm')
        server.sendmail('thegluping@gmail.com', email, msg.as_string())

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

