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

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        logging.info(f"Welcome email successfully sent to {to_email}")
        
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {e}")
