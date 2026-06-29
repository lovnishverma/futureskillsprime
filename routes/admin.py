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
    rows = list(db.find().sort("submitted_at", -1))
    completed_rows = []
    for r in rows:
        r["id"] = str(r["_id"])
        if r.get("photo_url") and r.get("sign_url"):
            completed_rows.append(r)
    return render_template("admin.html", rows=rows, completed_rows=completed_rows)


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


# ── Init & run ────────────────────────────────────────────────────────────────

@admin_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



