import os
import threading
import logging
import base64
import requests

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

def send_incomplete_reminder_email_async(to_email, whatsapp_link, course_name, pdf_bytes=None):
    """
    Spawns a background thread to send the reminder email asking for photo/signature.
    """
    thread = threading.Thread(
        target=_send_reminder_email,
        args=(to_email, whatsapp_link, course_name, pdf_bytes)
    )
    thread.daemon = True
    thread.start()

def _send_email(to_email, name, pdf_bytes, whatsapp_link, course_name):
    try:
        sender_email = os.environ.get("SENDER_EMAIL", "nielitchdropar@gmail.com")
        apps_script_url = "https://script.google.com/macros/s/AKfycbzepkxz2ze5ru2TgagpVFqj3j-nPt7ats38R6K9ezvi0_aWPAKhTtG6UYVLRI_Uy_iSYg/exec"

        subject = f"Welcome to {course_name} - FutureSkills Prime"
        
        body = f"""Dear {name},

Thank you for registering for the {course_name} program under FutureSkills Prime.

Please find your official nomination form attached to this email. 

"""
        if whatsapp_link:
            body += f"Join the official WhatsApp group for your batch here: {whatsapp_link}\n\n"
            
        body += "Best regards,\nNIELIT Team"

        payload = {
            "to": to_email,
            "subject": subject,
            "body": body
        }

        if pdf_bytes:
            payload["attachmentBase64"] = base64.b64encode(pdf_bytes).decode('utf-8')
            payload["attachmentName"] = "Nomination_Form.pdf"

        res = requests.post(apps_script_url, json=payload, timeout=20)
        
        if res.status_code == 200:
            result = res.json()
            if result.get("status") == "success":
                logging.info(f"Welcome email successfully sent to {to_email} via API")
            else:
                logging.error(f"API returned error when sending email to {to_email}: {result.get('message')}")
        else:
            logging.error(f"Failed to send email to {to_email}: HTTP {res.status_code} - {res.text}")
        
    except Exception as e:
        logging.error(f"Exception sending email to {to_email}: {e}")

def _send_reminder_email(to_email, whatsapp_link, course_name, pdf_bytes=None):
    try:
        sender_email = os.environ.get("SENDER_EMAIL", "nielitchdropar@gmail.com")
        apps_script_url = "https://script.google.com/macros/s/AKfycbzepkxz2ze5ru2TgagpVFqj3j-nPt7ats38R6K9ezvi0_aWPAKhTtG6UYVLRI_Uy_iSYg/exec"
        
        subject = f"Action Required: Upload Photo & Signature - {course_name}"
        
        body = f"""Good afternoon, all!

Thank you for joining this group and enrolling in our course.

Kindly upload your passport-size photo and signature through the link below:

https://futureskillsprime.onrender.com/search

Please note that uploading both the photo and signature is mandatory for all participants. Applications without a valid photo and signature will not be considered valid and may not be accepted.

Alternatively, you can also print the attached form, paste a color photo in the desired location, sign the form, scan it, and send that form directly in the WhatsApp group to Project Assistant Mr. Ravi Kant.

Once the upload is completed, please download your completed nomination form.

"""
        if whatsapp_link:
            body += f"Join the official WhatsApp group for your batch here: {whatsapp_link}\n\n"
            
        body += "Regards,\n\nNIELIT Chandigarh"
        
        payload = {
            "to": to_email,
            "subject": subject,
            "body": body
        }

        if pdf_bytes:
            payload["attachmentBase64"] = base64.b64encode(pdf_bytes).decode('utf-8')
            payload["attachmentName"] = "Nomination_Form.pdf"

        res = requests.post(apps_script_url, json=payload, timeout=20)
        
        if res.status_code == 200:
            result = res.json()
            if result.get("status") == "success":
                logging.info(f"Reminder email successfully sent to {to_email} via API")
            else:
                logging.error(f"API returned error when sending reminder to {to_email}: {result.get('message')}")
        else:
            logging.error(f"Failed to send reminder email to {to_email}: HTTP {res.status_code} - {res.text}")
        
    except Exception as e:
        logging.error(f"Exception sending reminder email to {to_email}: {e}")
