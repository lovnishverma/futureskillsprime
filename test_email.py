import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
smtp_port = int(os.getenv("SMTP_PORT", 587))
smtp_username = os.getenv("SMTP_USERNAME")
smtp_password = os.getenv("SMTP_PASSWORD")
sender_email = os.getenv("SENDER_EMAIL")
receiver_email = sender_email

try:
    msg = MIMEText("This is a test email to verify the SMTP configuration.")
    msg['Subject'] = "Test Email from FSP Admin"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.send_message(msg)
    server.quit()
    print("SUCCESS: Test email sent successfully to", receiver_email)
except Exception as e:
    print("ERROR:", str(e))
