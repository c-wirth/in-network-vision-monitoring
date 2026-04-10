import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


class NotificationService:
    def send_clip_alert(self, email, clip_path):
        print("[DEBUG] inside send_clip_alert")
        print("[DEBUG] to_email:", email)
        msg = EmailMessage()
        msg.set_content(f"New clip saved:\n{clip_path}")

        msg["Subject"] = "New Detection"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("[DEBUG] email sent successfully")