import uuid
import logging
import base64
import re
from io import BytesIO
from datetime import datetime
from flask import Blueprint, request, flash, redirect, url_for, render_template, abort, send_file
import cloudinary.uploader
from pathlib import Path

from models.database import get_db, get_config_col
from services.document import generate_pdf, generate_docx, row_to_form_data, DOCX_TEMPLATE
from services.email_service import send_welcome_email_async, send_incomplete_reminder_email_async
from services.helpers import fmt_course_dates

public_bp = Blueprint('public', __name__)

@public_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        f = request.form
        photo_url = None
        sign_url = None
        token = uuid.uuid4().hex

        track = f.get("Track")
        level = f.get("Level")
        batch_index_str = f.get("Batch_Index")
        
        c_start = ""
        c_end = ""
        wa_link = ""
        gf_link = ""

        if track and level and batch_index_str and batch_index_str.isdigit():
            b_idx = int(batch_index_str)
            config_col = get_config_col()
            course_dates_doc = config_col.find_one({"_id": "course_dates"}) or {}
            key = f"{track}_{level}"
            batches = course_dates_doc.get(key, [])
            if isinstance(batches, dict):
                batches = [batches] if batches.get("start") else []
            if b_idx < len(batches):
                b = batches[b_idx]
                c_start = b.get("start", "")
                c_end = b.get("end", "")
                wa_link = b.get("wa", "")
                gf_link = b.get("gf", "")

        db = get_db()
        
        # Enforce strict server-side validation to block submissions from old cached tabs
        if not track or not level:
            flash("error", "Invalid or outdated form submission detected. Please refresh the page completely and try again.")
            return redirect(url_for('public.index') + "#nomination")
            
        if not f.get("Highest_Qualification"):
            flash("error", "Highest Qualification is a mandatory field. Please refresh and fill it out.")
            return redirect(url_for('public.index') + "#nomination")
        
        # Enforce server-side validation for GOT forms (Educational Qualifications)
        if level in ["Basic", "Advanced"]:
            if not f.get("Edu1_Year") or not f.get("Edu1_Degree") or not f.get("Edu1_University"):
                flash("error", "Detailed Educational Qualifications are mandatory for GOT forms.")
                return redirect(url_for('public.index') + "#nomination")

        # Handle signature upload directly for Bootcamp
        if level == "Bootcamp":
            sign_file = request.files.get("signature_file")
            sign_data = request.form.get("signature_data")
            try:
                import base64
                if sign_file and sign_file.filename != '':
                    res = cloudinary.uploader.upload(sign_file, folder="nominations_signs", resource_type="image")
                    sign_url = res.get("secure_url")
                elif sign_data:
                    header, encoded = sign_data.split(",", 1)
                    data = base64.b64decode(encoded)
                    res = cloudinary.uploader.upload(data, folder="nominations_signs", resource_type="image")
                    sign_url = res.get("secure_url")
            except Exception as e:
                logging.error(f"Signature upload error: {e}")

        existing = db.find_one({
            "aadhar": f.get("Aadhar"),
            "track": track,
            "level": level,
            "batch_index": batch_index_str
        })

        if existing:
            token = existing.get("token", token)
            photo_url = photo_url or existing.get("photo_url")
            sign_url = sign_url or existing.get("sign_url")

        doc = {
            "token": token, "submitted_at": datetime.now().isoformat(),
            "track": track, "level": level, "batch_index": batch_index_str,
            "title": f.get("Title"), "name": f.get("Name"), "dob": f.get("DOB"), "gender": f.get("Gender"),
            "contact": f.get("Contact_Number"), "email": f.get("Email"), "aadhar": f.get("Aadhar"),
            "native_state": f.get("Native_State"), "district": f.get("District"),
            "organisation": f.get("Organisation"), "department": f.get("Department"), "designation": f.get("Designation"),
            "status": f.get("Status"), "beneficiary_category": f.get("Beneficiary_Category"),
            "institute_address": f.get("Institute_Address"), "institute_contact": f.get("Institute_Contact"), "institute_email": f.get("Institute_Email"),
            "highest_qual": f.get("Highest_Qualification"),
            "edu1_year": f.get("Edu1_Year"), "edu1_degree": f.get("Edu1_Degree"), "edu1_university": f.get("Edu1_University"),
            "edu2_year": f.get("Edu2_Year"), "edu2_degree": f.get("Edu2_Degree"), "edu2_university": f.get("Edu2_University"),
            "edu3_year": f.get("Edu3_Year"), "edu3_degree": f.get("Edu3_Degree"), "edu3_university": f.get("Edu3_University"),
            "exp1_year": f.get("Exp1_Year"), "exp1_area": f.get("Exp1_Area_of_Expertise"), "exp1_centre": f.get("Exp1_Centre"),
            "exp2_year": f.get("Exp2_Year"), "exp2_area": f.get("Exp2_Area_of_Expertise"), "exp2_centre": f.get("Exp2_Centre"),
            "exp3_year": f.get("Exp3_Year"), "exp3_area": f.get("Exp3_Area_of_Expertise"), "exp3_centre": f.get("Exp3_Centre"),
            "prev_fsp": f.get("Previous_FSP_Program"), "prev_fsp_details": f.get("Previous_FSP_Details_1"),
            "course_start_date": c_start, "course_end_date": c_end, "whatsapp_link": wa_link, "google_form_link": gf_link,
            "resource_centre": f.get("Resource_Centre_Name"),
            "photo_url": photo_url, "sign_url": sign_url
        }

        # Generate PDF and upload to Cloudinary
        form_data = row_to_form_data(doc)
        try:
            pdf_buf = generate_pdf(form_data)
            upload_result = cloudinary.uploader.upload(
                pdf_buf.getvalue(),
                resource_type="raw",
                public_id=f"nominations/nomination_{token}.pdf",
                invalidate=True
            )
            doc["pdf_url"] = upload_result.get("secure_url", "")
        except Exception as e:
            logging.error(f"Cloudinary upload failed: {e}")
            doc["pdf_url"] = existing.get("pdf_url", "") if existing else ""

        if existing:
            db.replace_one({"_id": existing["_id"]}, doc)
        else:
            db.insert_one(doc)
            
            # Send emails based on level
            try:
                pdf_bytes = pdf_buf.getvalue() if 'pdf_buf' in locals() else None
                course_name = f"{f.get('Track')} - {f.get('Level')}"
                
                if str(f.get('Level')).lower() == 'bootcamp':
                    # Bootcamp forms only require signature, so send the PDF immediately as they don't need a photo.
                    send_welcome_email_async(
                        to_email=f.get("Email"),
                        name=f.get("Name"),
                        pdf_bytes=pdf_bytes,
                        whatsapp_link=wa_link,
                        course_name=course_name
                    )
                else:
                    # For GOT forms (Basic/Advanced), they need BOTH photo and signature to be valid.
                    # Send a reminder to upload media first (no PDF).
                    send_incomplete_reminder_email_async(
                        to_email=f.get("Email"),
                        whatsapp_link=wa_link,
                        course_name=course_name
                    )

            except Exception as e:
                logging.error(f"Failed to start async email thread: {e}")
            
        flash("success", "ok")
        return redirect(url_for('public.success', token=token))

    config_col = get_config_col()
    course_dates_doc = config_col.find_one({"_id": "course_dates"}) or {}
    available_courses = {}
    for track_level, batches in course_dates_doc.items():
        if track_level == "_id":
            continue
            
        if isinstance(batches, dict):
            batches = [batches] if batches.get("start") else []
            
        valid_batches = []
        for idx, b in enumerate(batches):
            start = b.get("start")
            end = b.get("end")
            wa = b.get("wa", "")
            if start and end:
                formatted = fmt_course_dates(start, end)
                if formatted:
                    valid_batches.append({"index": idx, "formatted": formatted, "wa": wa})
                    
        if valid_batches:
            available_courses[track_level] = valid_batches

    return render_template("index.html", available_courses=available_courses)


@public_bp.route("/success/<token>")
def success(token):
    db = get_db()
    row = db.find_one({"token": token})
    if not row:
        abort(404)
    return render_template("success.html", token=token, name=row.get("name", "Applicant"), whatsapp_link=row.get("whatsapp_link"), google_form_link=row.get("google_form_link"), is_bootcamp=(row.get("level") == "Bootcamp"))


@public_bp.route("/download/pdf/<token>")
def download_pdf(token):
    db = get_db()
    row = db.find_one({"token": token})
    if not row:
        abort(404)
    form_data = row_to_form_data(row)
    pdf_buf = generate_pdf(form_data)
    safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_",
                       row.get("name") or "Nomination")
    return send_file(
        pdf_buf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"Nomination_{safe_name}.pdf",
    )

@public_bp.route("/preview/pdf/<token>")
def preview_pdf(token):
    db = get_db()
    row = db.find_one({"token": token})
    if not row:
        abort(404)
        
    form_data = row_to_form_data(row)
    safe_name = "".join(c for c in form_data.get("Name", "Applicant") if c.isalnum() or c in " _-").strip()
    pdf_buf = generate_pdf(form_data)
    return send_file(
        pdf_buf,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"Nomination_{safe_name}.pdf",
    )


@public_bp.route("/download/docx/<token>")
def download_docx(token):
    db = get_db()
    row = db.find_one({"token": token})
    if not row:
        abort(404)
    if not DOCX_TEMPLATE.exists():
        abort(500, "DOCX template missing")
    form_data = row_to_form_data(row)
    docx_buf = generate_docx(form_data)
    safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", row["name"] or "Nomination")
    return send_file(
        docx_buf,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=f"Nomination_{safe_name}.docx",
    )


@public_bp.route("/search", methods=["GET", "POST"])
def search():
    rows = []
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            db = get_db()
            cursor = db.find({"$or": [
                {"aadhar": query}, 
                {"contact": query}, 
                {"email": query},
                {"token": query}
            ]}).sort("submitted_at", -1)
            rows = list(cursor)
            if not rows:
                flash("No nomination found with that detail. Please try again.", "error")
    return render_template("search.html", rows=rows)

import base64

@public_bp.route("/upload_media/<token>", methods=["POST"])
def upload_media(token):
    db = get_db()
    row = db.find_one({"token": token})
    if not row:
        abort(404)
        
    old_row = row.copy()

    photo_file = request.files.get("photo")
    sign_file = request.files.get("signature_file")
    sign_data = request.form.get("signature_data")

    photo_url = row.get("photo_url")
    sign_url = row.get("sign_url")

    if photo_file and photo_file.filename != '':
        res = cloudinary.uploader.upload(photo_file, folder="nominations_photos", resource_type="image")
        photo_url = res.get("secure_url")

    if sign_file and sign_file.filename != '':
        res = cloudinary.uploader.upload(sign_file, folder="nominations_signs", resource_type="image")
        sign_url = res.get("secure_url")
    elif sign_data:
        # Base64 data: data:image/png;base64,iVBORw0KGgo...
        header, encoded = sign_data.split(",", 1)
        data = base64.b64decode(encoded)
        res = cloudinary.uploader.upload(data, folder="nominations_signs", resource_type="image")
        sign_url = res.get("secure_url")

    # Update DB
    db.update_one({"token": token}, {"$set": {"photo_url": photo_url, "sign_url": sign_url}})
    row = db.find_one({"token": token})  # Get updated row

    # Regenerate PDF with photo and sign, then upload to Cloudinary
    form_data = row_to_form_data(row)
    try:
        pdf_buf = generate_pdf(form_data)
        upload_result = cloudinary.uploader.upload(
            pdf_buf.getvalue(),
            resource_type="raw",
            public_id=f"nominations/nomination_{token}.pdf"
        )
        db.update_one({"token": token}, {"$set": {"pdf_url": upload_result.get("secure_url", "")}})
        row["pdf_url"] = upload_result.get("secure_url", "")
    except Exception as e:
        logging.error(f"Cloudinary PDF upload failed during media update: {e}")

    # Check if form is completed (has both photo and sign for GOT form)
    level = str(row.get('level')).lower()
    
    # Was it already completed BEFORE this upload?
    # For GOT, complete means having both photo and sign.
    old_row_completed = bool(old_row.get('photo_url') and old_row.get('sign_url')) if level != 'bootcamp' else True
    
    if level != 'bootcamp':
        if row.get('photo_url') and row.get('sign_url') and not old_row_completed:
            # It just became completed! Send the PDF.
            try:
                course_name = f"{row.get('track')} - {row.get('level')}"
                send_welcome_email_async(
                    to_email=row.get("email"),
                    name=row.get("name"),
                    pdf_bytes=pdf_buf.getvalue(),
                    whatsapp_link=row.get("whatsapp_link"),
                    course_name=course_name
                )
            except Exception as e:
                logging.error(f"Failed to send completed welcome email: {e}")

    flash("Media uploaded successfully! Your form has been updated.", "success")
    return render_template("search.html", rows=[row])



