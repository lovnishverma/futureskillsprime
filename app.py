"""
NIELIT Nomination Form - Full Flask App
Features:
  - Online nomination form with photo + signature upload
  - Generates filled DOCX + PDF per submission
  - Participant can download their own PDF
  - Admin panel: view all submissions, download CSV, download individual or all-in-one PDF
"""

from reportlab.platypus import (Image as RLImage, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from pypdf import PdfReader, PdfWriter
from PIL import Image
from flask import (Flask, abort, flash, g, redirect, render_template,
                   request, send_file, session, url_for)
from docx.shared import Inches, Pt
from docx import Document
from pathlib import Path
from io import BytesIO
from datetime import datetime
import zipfile
import uuid
import tempfile
from bson.objectid import ObjectId
import cloudinary.uploader
import cloudinary
from pymongo import MongoClient
import re
import os
import logging
import json
import io
from dotenv import load_dotenv
load_dotenv()


# ── App setup ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "nielit_dev_secret_2026")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
app.config["UPLOAD_FOLDER"] = BASE_DIR / "static" / "uploads"
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD")

cloudinary.config(
    cloud_name="dyq802zwa",
    api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", "")
)

DOCX_TEMPLATE = BASE_DIR / "docxtemplates" / "GOT_Nomination_Form.docx"
ALLOWED_IMG = {"png", "jpg", "jpeg", "gif", "webp"}

logging.basicConfig(level=logging.INFO)


# ── Database ──────────────────────────────────────────────────────────────────
mongo_client = MongoClient(app.config["MONGO_URI"])
db_client = mongo_client["nielit_db"]
nominations_col = db_client["nominations"]


def get_db():
    return nominations_col


def init_db():
    nominations_col.create_index("token", unique=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMG


def save_upload(file_storage, prefix):
    """Save an uploaded image; return relative path or None."""
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename):
        return None
    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    fname = f"{prefix}_{uuid.uuid4().hex[:8]}.{ext}"
    save_path = app.config["UPLOAD_FOLDER"] / fname
    file_storage.save(str(save_path))
    # Resize large images to keep storage sane
    try:
        img = Image.open(str(save_path))
        img.thumbnail((600, 800), Image.LANCZOS)
        img.save(str(save_path))
    except Exception:
        pass
    return fname


def fmt_date(val):
    """Convert YYYY-MM-DD → DD-MM-YYYY."""
    if val and re.match(r"^\d{4}-\d{2}-\d{2}$", val):
        try:
            return datetime.strptime(val, "%Y-%m-%d").strftime("%d-%m-%Y")
        except Exception:
            pass
    return val or ""


def row_to_form_data(row):
    """Map DB row to the placeholder dict used by DOCX/PDF generation."""
    d = dict(row)
    name_full = f"{d.get('title','')} {d.get('name','')}".strip()
    return {
        "Title": d.get("title", ""),
        "Name": d.get("name", ""),
        "Full_Name": name_full,
        "Course_Name": _course_name(d.get("track", ""), d.get("level", "")),
        "Technology": _technology(d.get("track", "")),
        "Resource_Centre_Name": d.get("resource_centre", "NIELIT Chandigarh"),
        "Date_of_Training": fmt_date(d.get("course_start_date", "")),
        "Designation": d.get("designation", ""),
        "Organisation": d.get("organisation", ""),
        "DOB": fmt_date(d.get("dob", "")),
        "Gender": d.get("gender", ""),
        "Aadhar": d.get("aadhar", ""),
        "Contact_Number": d.get("contact", ""),
        "Email": d.get("email", ""),
        "Organisation_Department": _merge(d.get("organisation", ""), d.get("department", "")),
        "Contact_Number_Email": _merge(d.get("contact", ""), d.get("email", "")),
        "Edu1_Year": d.get("edu1_year", ""), "Edu1_Degree": d.get("edu1_degree", ""), "Edu1_University": d.get("edu1_university", ""),
        "Edu2_Year": d.get("edu2_year", ""), "Edu2_Degree": d.get("edu2_degree", ""), "Edu2_University": d.get("edu2_university", ""),
        "Edu3_Year": d.get("edu3_year", ""), "Edu3_Degree": d.get("edu3_degree", ""), "Edu3_University": d.get("edu3_university", ""),
        "Exp1_Year": d.get("exp1_year", ""), "Exp1_Area_of_Expertise": d.get("exp1_area", ""), "Exp1_Centre": d.get("exp1_centre", ""),
        "Exp2_Year": d.get("exp2_year", ""), "Exp2_Area_of_Expertise": d.get("exp2_area", ""), "Exp2_Centre": d.get("exp2_centre", ""),
        "Exp3_Year": d.get("exp3_year", ""), "Exp3_Area_of_Expertise": d.get("exp3_area", ""), "Exp3_Centre": d.get("exp3_centre", ""),
        "Today_Date": datetime.today().strftime("%d-%m-%Y"),
        "photo_path": d.get("photo_path"),
        "sign_path": d.get("sign_path"),
    }


def _course_name(track, level):
    track = (track or "").upper()
    level = (level or "").capitalize()
    names = {
        ("ARVR", "Basic"):    "GOT – AR & VR (Basic)",
        ("ARVR", "Advanced"): "GOT – AR & VR (Advanced)",
        ("ARVR", "Bootcamp"): "Bootcamp – AR & VR",
        ("BDDS", "Basic"):    "GOT – Big Data & Data Science (Basic)",
        ("BDDS", "Advanced"): "GOT – Big Data & Data Science (Advanced)",
        ("BDDS", "Bootcamp"): "Bootcamp – Big Data & Data Science",
    }
    return names.get((track, level), f"{track} {level}")


def _technology(track):
    t = (track or "").upper()
    return {"ARVR": "Augmented & Virtual Reality", "BDDS": "Big Data & Data Science"}.get(t, track)


def _merge(a, b, sep=" / "):
    parts = [x for x in [a, b] if x]
    return sep.join(parts) if parts else ""


# ── DOCX generation ───────────────────────────────────────────────────────────
def _replace_in_para(para, replacements):
    full = para.text
    if "{" not in full and "<<" not in full:
        return
    if para.runs:
        for run in para.runs:
            for k, v in replacements.items():
                run.text = run.text.replace(
                    f"{{{k}}}", v).replace(f"<<{k}>>", v)
        joined = "".join(r.text for r in para.runs)
        if "{" in joined or "<<" in joined:
            updated = joined
            for k, v in replacements.items():
                updated = updated.replace(f"{{{k}}}", v).replace(f"<<{k}>>", v)
            if updated != joined:
                para.runs[0].text = updated
                for r in para.runs[1:]:
                    r.text = ""


def generate_docx(form_data: dict) -> BytesIO:
    """Fill the DOCX template and return as BytesIO. Inserts photo into Photo cell."""
    doc = Document(str(DOCX_TEMPLATE))
    replacements = {k: (str(v) if v else "") for k, v in form_data.items()
                    if k not in ("photo_path", "sign_path")}

    for para in doc.paragraphs:
        _replace_in_para(para, replacements)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                # Check if this cell is the "Photo" placeholder cell
                cell_text = cell.text.strip()
                if cell_text in ("Photo", "{Photo}", "<<Photo>>"):
                    photo_fname = form_data.get("photo_path")
                    if photo_fname:
                        photo_full = app.config["UPLOAD_FOLDER"] / photo_fname
                        if photo_full.exists():
                            for para in cell.paragraphs:
                                para.clear()
                            run = cell.paragraphs[0].add_run()
                            try:
                                run.add_picture(
                                    str(photo_full), width=Inches(1.0))
                            except Exception:
                                cell.paragraphs[0].text = "[Photo]"
                    continue
                for para in cell.paragraphs:
                    _replace_in_para(para, replacements)

    for section in doc.sections:
        for para in section.header.paragraphs:
            _replace_in_para(para, replacements)
        for para in section.footer.paragraphs:
            _replace_in_para(para, replacements)

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


# ── PDF generation via ReportLab ──────────────────────────────────────────────
def generate_pdf(form_data: dict) -> BytesIO:
    """Generate a professional A4 PDF nomination form with photo + signature."""
    buf = BytesIO()

    NAVY = colors.HexColor("#0f2d52")
    BLUE = colors.HexColor("#1a4f8a")
    ACCENT = colors.HexColor("#e8a020")
    LGRAY = colors.HexColor("#f4f6f9")
    MGRAY = colors.HexColor("#d0d8e4")

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
    )
    W, H = A4
    usable_w = W - 3.6*cm

    styles = getSampleStyleSheet()

    def st(name, **kw):
        s = ParagraphStyle(name, **kw)
        return s

    title_st = st("t",  fontName="Helvetica-Bold", fontSize=13,
                  textColor=NAVY, alignment=1, spaceAfter=2)
    sub_st = st("s",  fontName="Helvetica",      fontSize=9,
                textColor=BLUE, alignment=1, spaceAfter=4)
    head_st = st("h",  fontName="Helvetica-Bold", fontSize=8,
                 textColor=colors.white, leading=11)
    label_st = st("l",  fontName="Helvetica-Bold",
                  fontSize=7.5, textColor=NAVY)
    val_st = st("v",  fontName="Helvetica",
                fontSize=8,   textColor=colors.black)
    small_st = st("sm", fontName="Helvetica-Oblique", fontSize=7,
                  textColor=colors.HexColor("#555555"))
    section_st = st("sec", fontName="Helvetica-Bold",
                    fontSize=8,  textColor=colors.white)

    def cell(text, style=val_st, bg=None, span=1):
        p = Paragraph(str(text) if text else "—", style)
        return p

    def section_header(title):
        return Table(
            [[Paragraph(title, section_st)]],
            colWidths=[usable_w],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), BLUE),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BLUE]),
            ])
        )

    def field_row(label, value, label_w=5.5*cm):
        return Table(
            [[Paragraph(label, label_st), Paragraph(
                str(value) if value else "", val_st)]],
            colWidths=[label_w, usable_w - label_w],
            style=TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, MGRAY),
                ("BACKGROUND", (0, 0), (0, -1), LGRAY),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )

    story = []

    # ── Header ──
    story.append(
        Paragraph("Government Officials Training Programme", title_st))
    story.append(
        Paragraph("Nomination Form — FutureSkills PRIME | NIELIT Chandigarh", sub_st))
    story.append(Table(
        [[""]],
        colWidths=[usable_w],
        rowHeights=[3],
        style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT), ("TOPPADDING",
                         (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)])
    ))
    story.append(Spacer(1, 8))

    # ── Programme details with photo ──
    photo_fname = form_data.get("photo_path")
    photo_elem = None
    if photo_fname:
        photo_full = app.config["UPLOAD_FOLDER"] / photo_fname
        if photo_full.exists():
            try:
                photo_elem = RLImage(
                    str(photo_full), width=2.8*cm, height=3.2*cm)
            except Exception:
                photo_elem = None

    prog_rows = [
        [Paragraph("PROGRAMME DETAILS", section_st), ""],
        [Paragraph("Training Programme", label_st), Paragraph(
            form_data.get("Course_Name", ""), val_st)],
        [Paragraph("Technology", label_st), Paragraph(
            form_data.get("Technology", ""), val_st)],
        [Paragraph("Resource Centre", label_st), Paragraph(
            form_data.get("Resource_Centre_Name", ""), val_st)],
        [Paragraph("Date of Training", label_st), Paragraph(
            form_data.get("Date_of_Training", ""), val_st)],
    ]
    col1_w = usable_w - 3.2*cm
    prog_table = Table(prog_rows, colWidths=[5*cm, col1_w - 5*cm])
    prog_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("SPAN", (0, 0), (-1, 0)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, MGRAY),
        ("BACKGROUND", (0, 1), (0, -1), LGRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    if photo_elem:
        outer = Table(
            [[prog_table, photo_elem]],
            colWidths=[col1_w, 3.2*cm],
            style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (1, 0), (1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ])
        )
        story.append(outer)
    else:
        # photo placeholder box
        ph_box = Table(
            [[Paragraph("Photo", ParagraphStyle(
                "ph", fontName="Helvetica-Oblique", fontSize=7, textColor=colors.grey, alignment=1))]],
            colWidths=[3.0*cm], rowHeights=[3.5*cm],
            style=TableStyle([
                ("BOX", (0, 0), (-1, -1), 1, MGRAY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        outer = Table([[prog_table, ph_box]], colWidths=[col1_w, 3.2*cm],
                      style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (1, 0), (1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        story.append(outer)

    story.append(Spacer(1, 6))

    # ── Personal information ──
    story.append(section_header("PERSONAL INFORMATION"))
    pi = [
        [Paragraph("Name", label_st), Paragraph(form_data.get("Full_Name", ""), val_st),
         Paragraph("Designation", label_st), Paragraph(form_data.get("Designation", ""), val_st)],
        [Paragraph("Organisation", label_st), Paragraph(form_data.get("Organisation", ""), val_st),
         Paragraph("Department", label_st), Paragraph(form_data.get("Organisation_Department", ""), val_st)],
        [Paragraph("Date of Birth", label_st), Paragraph(form_data.get("DOB", ""), val_st),
         Paragraph("Gender", label_st), Paragraph(form_data.get("Gender", ""), val_st)],
        [Paragraph("Aadhaar No.", label_st), Paragraph(form_data.get("Aadhar", ""), val_st),
         Paragraph("Contact / Email", label_st), Paragraph(form_data.get("Contact_Number_Email", ""), val_st)],
    ]
    lw = 3.8*cm
    vw = (usable_w/2) - lw
    pi_table = Table(pi, colWidths=[lw, vw, lw, vw])
    pi_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, MGRAY),
        ("BACKGROUND", (0, 0), (0, -1), LGRAY),
        ("BACKGROUND", (2, 0), (2, -1), LGRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(pi_table)
    story.append(Spacer(1, 6))

    # ── Educational qualifications ──
    story.append(section_header(
        "EDUCATIONAL / PROFESSIONAL QUALIFICATIONS (GRADUATION ONWARDS)"))
    edu_data = [
        [Paragraph("Sl.", label_st), Paragraph("Year", label_st),
         Paragraph("Degree / Programme", label_st), Paragraph("University / Institute", label_st)],
    ]
    for i in range(1, 4):
        edu_data.append([
            Paragraph(str(i), val_st),
            Paragraph(form_data.get(f"Edu{i}_Year", ""), val_st),
            Paragraph(form_data.get(f"Edu{i}_Degree", ""), val_st),
            Paragraph(form_data.get(f"Edu{i}_University", ""), val_st),
        ])
    edu_table = Table(edu_data, colWidths=[
                      1*cm, 2*cm, (usable_w-3*cm)/2, (usable_w-3*cm)/2])
    edu_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, MGRAY),
        ("BACKGROUND", (0, 0), (-1, 0), LGRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(edu_table)
    story.append(Spacer(1, 6))

    # ── Research/Technical experience ──
    story.append(section_header("RESEARCH / TECHNICAL EXPERIENCE"))
    exp_data = [
        [Paragraph("Sl.", label_st), Paragraph("Year", label_st),
         Paragraph("Area of Expertise", label_st), Paragraph("Centre / Organisation", label_st)],
    ]
    for i in range(1, 4):
        exp_data.append([
            Paragraph(str(i), val_st),
            Paragraph(form_data.get(f"Exp{i}_Year", ""), val_st),
            Paragraph(form_data.get(f"Exp{i}_Area_of_Expertise", ""), val_st),
            Paragraph(form_data.get(f"Exp{i}_Centre", ""), val_st),
        ])
    exp_table = Table(exp_data, colWidths=[
                      1*cm, 2*cm, (usable_w-3*cm)/2, (usable_w-3*cm)/2])
    exp_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, MGRAY),
        ("BACKGROUND", (0, 0), (-1, 0), LGRAY),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(exp_table)
    story.append(Spacer(1, 8))

    # ── Signature / recommendation row ──
    sign_fname = form_data.get("sign_path")
    sign_elem = Paragraph("Signature of Applicant", small_st)
    if sign_fname:
        sign_full = app.config["UPLOAD_FOLDER"] / sign_fname
        if sign_full.exists():
            try:
                sign_elem = RLImage(
                    str(sign_full), width=3.5*cm, height=1.5*cm)
            except Exception:
                pass

    sig_row = Table(
        [[
            Table([[sign_elem], [Paragraph("Signature of the Official", small_st)]],
                  colWidths=[usable_w*0.45],
                  style=TableStyle([("BOX", (0, 0), (-1, -1), 0.5, MGRAY), ("TOPPADDING", (0, 0), (-1, -1), 14),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1),
                                     4), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM")])),
            Table([[Paragraph("", val_st)],
                   [Paragraph("Recommended / Not Recommended", small_st)],
                   [Paragraph("(Name & Designation with Seal)", small_st)]],
                  colWidths=[usable_w*0.45],
                  style=TableStyle([("BOX", (0, 0), (-1, -1), 0.5, MGRAY), ("TOPPADDING", (0, 0), (-1, -1), 14),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1),
                                     4), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM")])),
        ]],
        colWidths=[usable_w*0.5, usable_w*0.5],
        style=TableStyle([("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                          ("LEFTPADDING", (1, 0), (1, -1), 4)])
    )
    story.append(sig_row)

    # ── Footer ──
    story.append(Spacer(1, 6))
    story.append(Table(
        [[Paragraph(
            f"Submitted on {form_data.get('Today_Date','')} | NIELIT Chandigarh — FutureSkills PRIME", small_st)]],
        colWidths=[usable_w],
        style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), LGRAY), ("TOPPADDING", (0, 0), (-1, -1), 4),
                          ("BOTTOMPADDING", (0, 0), (-1, -1),
                           4), ("LEFTPADDING", (0, 0), (-1, -1), 6),
                          ("BOX", (0, 0), (-1, -1), 0.5, MGRAY)])
    ))

    doc.build(story)
    buf.seek(0)
    return buf


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        f = request.form
        photo_fname = save_upload(request.files.get("photo"), "photo")
        sign_fname = save_upload(request.files.get("signature"), "sign")
        token = uuid.uuid4().hex

        db = get_db()
        doc = {
            "token": token, "submitted_at": datetime.now().isoformat(),
            "track": f.get("Track"), "level": f.get("Level"),
            "title": f.get("Title"), "name": f.get("Name"), "dob": f.get("DOB"), "gender": f.get("Gender"),
            "contact": f.get("Contact_Number"), "email": f.get("Email"), "aadhar": f.get("Aadhar"),
            "native_state": f.get("Native_State"), "district": f.get("District"),
            "organisation": f.get("Organisation"), "department": f.get("Department"), "designation": f.get("Designation"),
            "status": f.get("Status"), "beneficiary_category": f.get("Beneficiary_Category"),
            "highest_qual": f.get("Highest_Qualification"),
            "edu1_year": f.get("Edu1_Year"), "edu1_degree": f.get("Edu1_Degree"), "edu1_university": f.get("Edu1_University"),
            "edu2_year": f.get("Edu2_Year"), "edu2_degree": f.get("Edu2_Degree"), "edu2_university": f.get("Edu2_University"),
            "edu3_year": f.get("Edu3_Year"), "edu3_degree": f.get("Edu3_Degree"), "edu3_university": f.get("Edu3_University"),
            "exp1_year": f.get("Exp1_Year"), "exp1_area": f.get("Exp1_Area_of_Expertise"), "exp1_centre": f.get("Exp1_Centre"),
            "exp2_year": f.get("Exp2_Year"), "exp2_area": f.get("Exp2_Area_of_Expertise"), "exp2_centre": f.get("Exp2_Centre"),
            "exp3_year": f.get("Exp3_Year"), "exp3_area": f.get("Exp3_Area_of_Expertise"), "exp3_centre": f.get("Exp3_Centre"),
            "prev_fsp": f.get("Previous_FSP_Program"), "prev_fsp_details": f.get("Previous_FSP_Details_1"),
            "course_start_date": f.get("Course_Start_Date"), "resource_centre": f.get("Resource_Centre_Name"),
            "photo_path": photo_fname, "sign_path": sign_fname
        }

        # Generate PDF and upload to Cloudinary
        form_data = row_to_form_data(doc)
        try:
            pdf_buf = generate_pdf(form_data)
            upload_result = cloudinary.uploader.upload(
                pdf_buf.getvalue(),
                resource_type="raw",
                public_id=f"nominations/nomination_{token}.pdf"
            )
            doc["pdf_url"] = upload_result.get("secure_url", "")
        except Exception as e:
            logging.error(f"Cloudinary upload failed: {e}")
            doc["pdf_url"] = ""

        db.insert_one(doc)
        flash("success", "ok")
        return redirect(url_for("success", token=token))

    return render_template("index.html")


@app.route("/success/<token>")
def success(token):
    db = get_db()
    row = db.find_one({"token": token})
    if not row:
        abort(404)
    return render_template("success.html", token=token, name=row["name"])


@app.route("/download/pdf/<token>")
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


@app.route("/download/docx/<token>")
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


# ── Admin routes ──────────────────────────────────────────────────────────────

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd == app.config["ADMIN_PASSWORD"]:
            session["admin"] = True
            return redirect(url_for("admin"))
        flash("Wrong password.", "error")
    if not session.get("admin"):
        return render_template("admin_login.html")

    db = get_db()
    rows = list(db.find().sort("submitted_at", -1))
    for r in rows:
        r["id"] = str(r["_id"])
    return render_template("admin.html", rows=rows)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin"))


@app.route("/admin/csv")
def admin_csv():
    if not session.get("admin"):
        abort(403)
    db = get_db()
    rows = list(db.find().sort("submitted_at", -1))
    for r in rows:
        r["id"] = str(r["_id"])
    if not rows:
        flash("No submissions yet.", "warning")
        return redirect(url_for("admin"))

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


@app.route("/admin/pdf/<string:row_id>")
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


@app.route("/admin/pdf/all")
def admin_pdf_all():
    if not session.get("admin"):
        abort(403)
    db = get_db()
    rows = list(db.find().sort("submitted_at", 1))
    if not rows:
        flash("No submissions yet.", "warning")
        return redirect(url_for("admin"))

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


@app.route("/admin/delete/<string:row_id>", methods=["POST"])
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
        for f in [row.get("photo_path"), row.get("sign_path")]:
            if f:
                try:
                    (app.config["UPLOAD_FOLDER"] / f).unlink(missing_ok=True)
                except Exception:
                    pass
        db.delete_one({"_id": obj_id})
    flash("Entry deleted.", "success")
    return redirect(url_for("admin"))


# ── Init & run ────────────────────────────────────────────────────────────────

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":

    app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)
    app.config["MONGO_URI"] = "mongodb+srv://indiaaischeme:nielit4321@cluster0.ler36mh.mongodb.net/?appName=Cluster0"
    init_db()
    app.run(debug=True, port=5000)
