import csv
import io
import zipfile
import re
from io import BytesIO
from flask import Blueprint, request, session, flash, redirect, url_for, render_template, send_file, current_app, abort
import os
from datetime import datetime
from bson.objectid import ObjectId
from pypdf import PdfWriter, PdfReader
from docx import Document
from docxcompose.composer import Composer
import cloudinary
import cloudinary.uploader

from models.database import get_db, get_config_col
from services.document import generate_pdf, generate_docx, row_to_form_data, DOCX_TEMPLATE

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/admin/dates", methods=["GET", "POST"])
def admin_dates():
    if not session.get("admin"):
        return redirect(url_for('admin.admin'))
    
    config_col = get_config_col()
    courses = {
        "ARVR_Basic": "GOT – AR & VR (Basic)",
        "ARVR_Advanced": "GOT – AR & VR (Advanced)",
        "ARVR_Bootcamp": "Bootcamp – AR & VR",
        "BDDS_Basic": "GOT – Big Data & Data Science (Basic)",
        "BDDS_Advanced": "GOT – Big Data & Data Science (Advanced)",
        "BDDS_Bootcamp": "Bootcamp – Big Data & Data Science"
    }

    if request.method == "POST":
        updates = {}
        for key in courses.keys():
            starts = request.form.getlist(f"{key}_start[]")
            ends = request.form.getlist(f"{key}_end[]")
            was = request.form.getlist(f"{key}_wa[]")
            gfs = request.form.getlist(f"{key}_gf[]")
            batches = []
            for s, e, w, gf_val in zip(starts, ends, was, gfs):
                if s and e:
                    batches.append({"start": s, "end": e, "wa": w, "gf": gf_val})
            updates[key] = batches
        
        config_col.update_one({"_id": "course_dates"}, {"$set": updates}, upsert=True)
        flash("Course dates updated successfully.", "success")
        return redirect(url_for('admin.admin_dates'))

    doc = config_col.find_one({"_id": "course_dates"}) or {}
    return render_template("admin_dates.html", courses=courses, config_dates=doc)

@admin_bp.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd == current_app.config["ADMIN_PASSWORD"]:
            session["admin"] = True
            return redirect(url_for('admin.admin'))
        flash("Wrong password.", "error")
    if not session.get("admin"):
        return render_template("admin_login.html")

    db = get_db()
    
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
        
    try:
        limit = int(request.args.get("limit", 50))
    except ValueError:
        limit = 50

    search_query = request.args.get("search", "").strip()
    track_filter = request.args.get("track", "").strip()
    level_filter = request.args.get("level", "").strip()
    batch_filter = request.args.get("batch_date", "").strip()
    tab = request.args.get("tab", "all")

    query = {}
    if search_query:
        query["$or"] = [
            {"name": {"$regex": search_query, "$options": "i"}},
            {"aadhar": {"$regex": search_query, "$options": "i"}},
            {"contact": {"$regex": search_query, "$options": "i"}},
            {"email": {"$regex": search_query, "$options": "i"}},
            {"token": {"$regex": search_query, "$options": "i"}},
            {"organisation": {"$regex": search_query, "$options": "i"}}
        ]
        
    if track_filter:
        query["track"] = track_filter
    if level_filter:
        query["level"] = level_filter
    if batch_filter:
        query["course_start_date"] = batch_filter
        
    if tab == "completed":
        query["photo_url"] = {"$ne": None, "$exists": True, "$type": "string"}
        query["sign_url"] = {"$ne": None, "$exists": True, "$type": "string"}

    total_records = db.count_documents(query)
    total_pages = (total_records + limit - 1) // limit
    
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages

    skip = (page - 1) * limit

    rows = list(db.find(query).sort("submitted_at", -1).skip(skip).limit(limit))
    for r in rows:
        r["id"] = str(r["_id"])
        
    tracks = db.distinct("track")
    levels = db.distinct("level")
    batch_dates = db.distinct("course_start_date")
    
    return render_template(
        "admin.html", 
        rows=rows, 
        page=page, 
        total_pages=total_pages, 
        total_records=total_records,
        search_query=search_query,
        track_filter=track_filter,
        level_filter=level_filter,
        batch_filter=batch_filter,
        tab=tab,
        tracks=[t for t in tracks if t],
        levels=[l for l in levels if l],
        batch_dates=[b for b in batch_dates if b],
        limit=limit
    )


@admin_bp.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for('admin.admin'))


@admin_bp.route("/admin/csv")
def admin_csv():
    if not session.get("admin"):
        abort(403)
    db = get_db()
    rows = list(db.find().sort("submitted_at", -1))
    for r in rows:
        r["id"] = str(r["_id"])
    if not rows:
        flash("No submissions yet.", "warning")
        return redirect(url_for('admin.admin'))

    import csv
    buf = io.StringIO()
    for r in rows:
        r.pop("_id", None)
    cols = list(rows[0].keys())
    writer = csv.DictWriter(buf, fieldnames=cols)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    buf.seek(0)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return send_file(
        io.BytesIO(buf.getvalue().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"NIELIT_Nominations_{ts}.csv",
    )


@admin_bp.route("/admin/pdf/<string:row_id>")
def admin_pdf_single(row_id):
    if not session.get("admin"):
        abort(403)
    db = get_db()
    row = db.find_one({"_id": ObjectId(row_id)})
    if not row:
        abort(404)
    form_data = row_to_form_data(row)
    pdf_buf = generate_pdf(form_data)
    safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_",
                       row.get("name") or "Nomination")
    return send_file(pdf_buf, mimetype="application/pdf", as_attachment=True,
                     download_name=f"Nomination_{safe_name}.pdf")


@admin_bp.route("/admin/pdf/all")
def admin_pdf_all():
    if not session.get("admin"):
        abort(403)
    db = get_db()
    
    if request.args.get("completed"):
        rows = list(db.find({"photo_url": {"$nin": [None, ""]}, "sign_url": {"$nin": [None, ""]}}).sort("submitted_at", 1))
    else:
        rows = list(db.find().sort("submitted_at", 1))
    if not rows:
        flash("No submissions yet.", "warning")
        return redirect(url_for('admin.admin'))

    writer = PdfWriter()
    for row in rows:
        form_data = row_to_form_data(row)
        pdf_buf = generate_pdf(form_data)
        reader = PdfReader(pdf_buf)
        for page in reader.pages:
            writer.add_page(page)

    out_buf = BytesIO()
    writer.write(out_buf)
    out_buf.seek(0)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return send_file(out_buf, mimetype="application/pdf", as_attachment=True,
                     download_name=f"All_Nominations_{ts}.pdf")



@admin_bp.route("/admin/docx/all")
def admin_docx_all():
    if not session.get("admin"):
        abort(403)
    db = get_db()
    
    if request.args.get("completed"):
        rows = list(db.find({"photo_url": {"$nin": [None, ""]}, "sign_url": {"$nin": [None, ""]}}).sort("submitted_at", 1))
    else:
        rows = list(db.find().sort("submitted_at", 1))
    if not rows:
        flash("No submissions yet.", "warning")
        return redirect(url_for('admin.admin'))

    master = None
    for row in rows:
        form_data = row_to_form_data(row)
        docx_buf = generate_docx(form_data)
        doc = Document(docx_buf)
        if master is None:
            master = Composer(doc)
        else:
            master.append(doc)

    out_buf = BytesIO()
    master.save(out_buf)
    out_buf.seek(0)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return send_file(out_buf, mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document", as_attachment=True,
                     download_name=f"All_Nominations_{ts}.docx")


@admin_bp.route("/admin/delete_all", methods=["POST"])
def admin_delete_all():
    if not session.get("admin"):
        abort(403)
        
    pwd = request.form.get("delete_password", "")
    expected_pwd = os.environ.get("DELETE_ALL_PASSWORD", "rccrcc")
    if pwd != expected_pwd:
        flash("Incorrect password to delete all.", "error")
        return redirect(url_for('admin.admin'))

    db = get_db()
    db.delete_many({})
    flash("All nominations deleted successfully.", "success")
    return redirect(url_for('admin.admin'))

@admin_bp.route("/admin/zip/pdfs")
def admin_zip_pdfs():
    if not session.get("admin"):
        abort(403)
    db = get_db()
    
    if request.args.get("completed"):
        rows = list(db.find({"photo_url": {"$nin": [None, ""]}, "sign_url": {"$nin": [None, ""]}}))
    else:
        rows = list(db.find())
        
    if not rows:
        flash("No submissions yet.", "warning")
        return redirect(url_for('admin.admin'))
    
    zip_buf = BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for row in rows:
            form_data = row_to_form_data(row)
            pdf_buf = generate_pdf(form_data)
            safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", row.get("name") or "Nomination")
            zf.writestr(f"Nomination_{safe_name}_{row.get('token')[:6]}.pdf", pdf_buf.getvalue())
            
    zip_buf.seek(0)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return send_file(zip_buf, mimetype="application/zip", as_attachment=True, download_name=f"All_PDFs_{ts}.zip")

@admin_bp.route("/admin/zip/docxs")
def admin_zip_docxs():
    if not session.get("admin"):
        abort(403)
    db = get_db()
    
    if request.args.get("completed"):
        rows = list(db.find({"photo_url": {"$nin": [None, ""]}, "sign_url": {"$nin": [None, ""]}}))
    else:
        rows = list(db.find())
        
    if not rows:
        flash("No submissions yet.", "warning")
        return redirect(url_for('admin.admin'))
    
    zip_buf = BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for row in rows:
            form_data = row_to_form_data(row)
            docx_buf = generate_docx(form_data)
            safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", row.get("name") or "Nomination")
            zf.writestr(f"Nomination_{safe_name}_{row.get('token')[:6]}.docx", docx_buf.getvalue())
            
    zip_buf.seek(0)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return send_file(zip_buf, mimetype="application/zip", as_attachment=True, download_name=f"All_DOCXs_{ts}.zip")


@admin_bp.route("/admin/delete/<string:row_id>", methods=["POST"])
def admin_delete(row_id):
    if not session.get("admin"):
        abort(403)
    db = get_db()
    try:
        obj_id = ObjectId(row_id)
    except Exception:
        abort(400)
    row = db.find_one({"_id": obj_id})
    if row:
        db.delete_one({"_id": obj_id})
    flash("Entry deleted.", "success")
    return redirect(url_for('admin.admin'))


@admin_bp.route("/admin/edit_batch/<row_id>", methods=["GET", "POST"])
def admin_edit_batch(row_id):
    if not session.get("admin"):
        return redirect(url_for('admin.admin'))

    db = get_db()
    try:
        obj_id = ObjectId(row_id)
    except Exception:
        abort(400)
        
    row = db.find_one({"_id": obj_id})
    if not row:
        flash("Record not found.", "error")
        return redirect(url_for('admin.admin'))

    config_col = get_config_col()
    course_dates_doc = config_col.find_one({"_id": "course_dates"}) or {}
    
    track = row.get("track", "")
    level = row.get("level", "")
    key = f"{track}_{level}"
    
    batches = course_dates_doc.get(key, [])
    if isinstance(batches, dict):
        batches = [batches] if batches.get("start") else []
        
    valid_batches = []
    for idx, b in enumerate(batches):
        start = b.get("start")
        end = b.get("end")
        wa = b.get("wa", "")
        if start and end:
            valid_batches.append({"index": idx, "start": start, "end": end, "wa": wa})

    if request.method == "POST":
        new_batch_index_str = request.form.get("new_batch_index")
        if not new_batch_index_str or not new_batch_index_str.isdigit():
            flash("Invalid batch selection.", "error")
            return redirect(request.url)
            
        b_idx = int(new_batch_index_str)
        if b_idx >= len(valid_batches):
            flash("Selected batch is out of range.", "error")
            return redirect(request.url)
            
        b = valid_batches[b_idx]
        
        # Update MongoDB
        row["course_start_date"] = b["start"]
        row["course_end_date"] = b["end"]
        row["whatsapp_link"] = b["wa"]
        row["batch_index"] = str(b_idx)
        
        # Regenerate PDF
        form_data = row_to_form_data(row)
        try:
            pdf_buf = generate_pdf(form_data)
            token = row.get("token")
            upload_result = cloudinary.uploader.upload(
                pdf_buf.getvalue(),
                resource_type="raw",
                public_id=f"nominations/nomination_{token}.pdf",
                invalidate=True
            )
            row["pdf_url"] = upload_result.get("secure_url", "")
        except Exception as e:
            flash(f"Batch updated in DB, but PDF regeneration failed: {e}", "warning")
            
        db.replace_one({"_id": obj_id}, row)
        flash(f"Batch successfully updated to {b['start']}. Document regenerated.", "success")
        return redirect(url_for('admin.admin'))

    row["id"] = str(row["_id"])
    return render_template("admin_edit_batch.html", row=row, valid_batches=valid_batches)


# ── Init & run ────────────────────────────────────────────────────────────────

@admin_bp.app_errorhandler(404)
def page_not_found(e):

    return render_template('404.html'), 404
