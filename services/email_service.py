import os
import smtplib
import threading
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_welcome_email_async(to_email, name, pdf_bytes, whatsapp_link, course_name):
    """
    Spawns a background thread to send the welcome email so it doesn't block the web request.
    """
    thread = threading.Thread(
        target=_send_email,
        args=(to_email, name, pdf_bytes, whatsapp_link, course_name)
    )
    thread.daemon = True
    thread.start()

def send_incomplete_reminder_email_async(to_email, whatsapp_link, course_name):
    """
    Spawns a background thread to send the reminder email asking for photo/signature.
    """
    thread = threading.Thread(
        target=_send_reminder_email,
        args=(to_email, whatsapp_link, course_name)
    )
    thread.daemon = True
    thread.start()

def _send_email(to_email, name, pdf_bytes, whatsapp_link, course_name):
    try:
        smtp_server = os.environ.get("SMTP_SERVER")
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        smtp_user = os.environ.get("SMTP_USERNAME")
        smtp_pass = os.environ.get("SMTP_PASSWORD")
        sender_email = os.environ.get("SENDER_EMAIL", smtp_user)
        
        if not smtp_server or not smtp_user or not smtp_pass:
            logging.warning("SMTP credentials not configured. Skipping welcome email.")
            return

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = f"Welcome to {course_name} - FutureSkills Prime"

        body = f"""Dear {name},

Thank you for registering for the {course_name} program under FutureSkills Prime.

Please find your official nomination form attached to this email. 

"""
        if whatsapp_link:
            body += f"Join the official WhatsApp group for your batch here: {whatsapp_link}\n\n"
            
        body += "Best regards,\nNIELIT Team"
        
        msg.attach(MIMEText(body, 'plain'))

        if pdf_bytes:
            part = MIMEApplication(pdf_bytes, Name="Nomination_Form.pdf")
            part['Content-Disposition'] = 'attachment; filename="Nomination_Form.pdf"'
            msg.attach(part)

        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        logging.info(f"Welcome email successfully sent to {to_email}")
        
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {e}")

def _send_reminder_email(to_email, whatsapp_link, course_name):
    try:
        smtp_server = os.environ.get("SMTP_SERVER")
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        smtp_user = os.environ.get("SMTP_USERNAME")
        smtp_pass = os.environ.get("SMTP_PASSWORD")
        sender_email = os.environ.get("SENDER_EMAIL", smtp_user)
        
        if not smtp_server or not smtp_user or not smtp_pass:
            logging.warning("SMTP credentials not configured. Skipping reminder email.")
            return

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = f"Action Required: Upload Photo & Signature - {course_name}"

        body = f"""Good afternoon, all!

Thank you for joining this group and enrolling in our course.

Kindly upload your passport-size photo and signature through the link below:

https://futureskillsprime.onrender.com/search

Please note that uploading both the photo and signature is mandatory for all participants. Applications without a valid photo and signature will not be considered valid and may not be accepted.

Once the upload is completed, please download your nomination form.

"""
        if whatsapp_link:
            body += f"Join the official WhatsApp group for your batch here: {whatsapp_link}\n\n"
            
        body += "Regards,\n\nNIELIT Chandigarh"
        
        msg.attach(MIMEText(body, 'plain'))

        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        logging.info(f"Reminder email successfully sent to {to_email}")
        
    except Exception as e:
        logging.error(f"Failed to send reminder email to {to_email}: {e}")
