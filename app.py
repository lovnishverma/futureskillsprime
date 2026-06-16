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
from reportlab.lib.units import cm, mm, inch
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

# Call it immediately when the module is imported by Gunicorn
init_db()


# ── Helpers ───────────────────────────────────────────────────────────────────




import urllib.request


def fetch_image_as_jpeg(url, target_size=None):
    import urllib.request
    import tempfile
    from io import BytesIO
    from PIL import Image, ImageOps
    req = urllib.request.urlopen(url)
    img = Image.open(BytesIO(req.read()))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    if target_size:
        # Replaced ImageOps.fit with ImageOps.contain
        img = ImageOps.contain(img, target_size, Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
        
    fd, path = tempfile.mkstemp(suffix=".jpg")
    import os
    os.close(fd)
    img.save(path, format="JPEG")
    return path

def upload_to_cloudinary(file_obj, folder_name):
    """Upload file directly to Cloudinary and return secure URL."""
    if not file_obj or file_obj.filename == '':
        return None
    try:
        res = cloudinary.uploader.upload(file_obj, folder=folder_name, resource_type="image")
        return res.get("secure_url")
    except Exception as e:
        logging.error(f"Cloudinary upload failed: {e}")
        return None

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
        "Course_Start_Date": fmt_date(d.get("course_start_date", "")),
        "Native_State": d.get("native_state", ""),
        "District": d.get("district", ""),
        "Status": d.get("status", ""),
        "Beneficiary_Category": d.get("beneficiary_category", ""),
        "Level": d.get("level", ""),
        "Applicant_Name": name_full,
        "Gov_ID_Number": d.get("aadhar", ""),
        "Organization_Academic_Institute": d.get("organisation", ""),
        "Role": d.get("designation", ""),
        "Highest_Qualification": f"{d.get('highest_qual', '')}",
        "Previous_FSP_Program": d.get("prev_fsp", ""),
        "Previous_FSP_Details_1": d.get("prev_fsp_details", ""),
        "Previous_FSP_Details_2": "",
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
        "Institute_Details": _merge(_merge(d.get("institute_address", ""), d.get("institute_contact", "")), d.get("institute_email", "")),
        "photo_url": d.get("photo_url", ""),
        "sign_url": d.get("sign_url", ""),
        "Edu1_Year": d.get("edu1_year", ""), "Edu1_Degree": d.get("edu1_degree", ""), "Edu1_University": d.get("edu1_university", ""),
        "Edu2_Year": d.get("edu2_year", ""), "Edu2_Degree": d.get("edu2_degree", ""), "Edu2_University": d.get("edu2_university", ""),
        "Edu3_Year": d.get("edu3_year", ""), "Edu3_Degree": d.get("edu3_degree", ""), "Edu3_University": d.get("edu3_university", ""),
        "Exp1_Year": d.get("exp1_year", ""), "Exp1_Area_of_Expertise": d.get("exp1_area", ""), "Exp1_Centre": d.get("exp1_centre", ""),
        "Exp2_Year": d.get("exp2_year", ""), "Exp2_Area_of_Expertise": d.get("exp2_area", ""), "Exp2_Centre": d.get("exp2_centre", ""),
        "Exp3_Year": d.get("exp3_year", ""), "Exp3_Area_of_Expertise": d.get("exp3_area", ""), "Exp3_Centre": d.get("exp3_centre", ""),
        "Today_Date": datetime.today().strftime("%d-%m-%Y"),
        "photo_url": d.get("photo_url"),
        "sign_url": d.get("sign_url"),
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
    template_path = Path("docxtemplates/Bootcamp_Nomination_Form.docx") if form_data.get("Level") == "Bootcamp" else DOCX_TEMPLATE
    doc = Document(str(template_path))
    replacements = {k: (str(v) if v else "") for k, v in form_data.items()
                    if k not in ("photo_url", "sign_url")}

    level_val = (form_data.get("Level") or "").capitalize()
    if level_val in ("Advanced", "Basic"):
        prog_title = f"Government Officials Training ({level_val}) Programme"
    else:
        prog_title = "Government Officials Training Programme"

    for para in doc.paragraphs:
        if "Government Officials Training Programme" in para.text:
            for run in para.runs:
                run.text = run.text.replace("Government Officials Training Programme", prog_title)

        cell_text = para.text.strip()
        if "{Photo}" in cell_text or "<<Photo>>" in cell_text or cell_text == "Photo":
            photo_url = form_data.get("photo_url")
            if photo_url:
                try:
                    img_buf = fetch_image_as_jpeg(photo_url, target_size=(300, 375))
                    para.clear()
                    run = para.add_run()
                    # run.add_picture(img_buf, width=Inches(1.2), height=Inches(1.5))
                    run.add_picture(img_buf, width=Inches(0.96), height=Inches(1.2))
                except Exception:
                    para.text = "[Photo]"
            continue
        elif "{Signature}" in cell_text or "<<Signature>>" in cell_text or cell_text == "Signature":
            sign_url = form_data.get("sign_url")
            if sign_url:
                try:
                    img_buf = fetch_image_as_jpeg(sign_url, target_size=(300, 100))
                    para.clear()
                    run = para.add_run()
                    # run.add_picture(img_buf, width=Inches(1.5), height=Inches(0.5))
                    run.add_picture(img_buf, width=Inches(1.2), height=Inches(0.4))
                except Exception:
                    para.text = "[Signature]"
            continue
        
        _replace_in_para(para, replacements)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                # Check if this cell is the "Photo" placeholder cell
                cell_text = cell.text.strip()
                if "{Photo}" in cell_text or "<<Photo>>" in cell_text or cell_text == "Photo":
                    photo_url = form_data.get("photo_url")
                    if photo_url:
                        try:
                            img_buf = fetch_image_as_jpeg(photo_url, target_size=(300, 375))
                            for para in cell.paragraphs:
                                para.clear()
                            run = cell.paragraphs[0].add_run()
                            # run.add_picture(img_buf, width=Inches(1.2), height=Inches(1.5))
                            run.add_picture(img_buf, width=Inches(0.96), height=Inches(1.2))
                        except Exception:
                            cell.paragraphs[0].text = "[Photo]"
                    continue
                elif "{Signature}" in cell_text or "<<Signature>>" in cell_text or cell_text == "Signature":
                    sign_url = form_data.get("sign_url")
                    if sign_url:
                        try:
                            img_buf = fetch_image_as_jpeg(sign_url, target_size=(300, 100))
                            cell.text = ""
                            run = cell.paragraphs[0].add_run()
                            # run.add_picture(img_buf, width=Inches(1.5), height=Inches(0.5))
                            run.add_picture(img_buf, width=Inches(1.2), height=Inches(0.4))
                            from docx.enum.text import WD_ALIGN_PARAGRAPH
                            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                        except Exception:
                            cell.paragraphs[0].text = "[Signature]"
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
    """Generate a simple A4 PDF nomination form matching the DOCX template."""
    buf = BytesIO()
    
    if form_data.get("Level") == "Bootcamp":
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            topMargin=0.8*cm, bottomMargin=0.8*cm,
            leftMargin=1.2*cm, rightMargin=1.2*cm,
        )
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_st = ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=12, alignment=1, spaceAfter=4)
        norm_st = ParagraphStyle('norm', fontName='Helvetica', fontSize=9)
        bold_st = ParagraphStyle('bold', fontName='Helvetica-Bold', fontSize=9)
        
        # Header
        elements.append(Paragraph("National Institute of Electronics and Information Technology Chandigarh", title_st))
        elements.append(Paragraph("An autonomous scientific society under administrative control of<br/>Ministry of Electronics and Information Technology (MeitY), Government of India", ParagraphStyle('sub', fontName='Helvetica-Bold', fontSize=10, alignment=1, spaceAfter=8)))
        elements.append(Paragraph("FutureSkills PRIME (Programme for Re-skilling/Up-skilling of IT Manpower for Employability)", ParagraphStyle('sub2', fontName='Helvetica-Bold', fontSize=10, alignment=1, spaceAfter=14)))
        
        usable_w = A4[0] - 2.4*cm
        
        data = [
            [Paragraph("Resource Centre Name", bold_st), ":", Paragraph(form_data.get("Resource_Centre_Name", ""), norm_st)],
            [Paragraph("Technology", bold_st), ":", Paragraph(f"{form_data.get('Technology', '')}      Role: {form_data.get('xxx', 'Co-Lead')}", norm_st)],
            ["1", Paragraph("Course Name", norm_st), ":", Paragraph(form_data.get("Course_Name", ""), norm_st)],
            ["2", Paragraph("Course Start Date", norm_st), ":", Paragraph(form_data.get("Course_Start_Date", ""), norm_st)],
            ["3", Paragraph("Applicant Name (as per Gov ID)", norm_st), ":", Paragraph(form_data.get("Applicant_Name", ""), norm_st)],
            ["4", Paragraph("Date of Birth", norm_st), ":", Paragraph(form_data.get("DOB", ""), norm_st)],
            ["5", Paragraph("Gender", norm_st), ":", Paragraph(form_data.get("Gender", ""), norm_st)],
            ["6", Paragraph("Mobile Number", norm_st), ":", Paragraph(form_data.get("Contact_Number", ""), norm_st)],
            ["7", Paragraph("Email ID (official ID preferred)", norm_st), ":", Paragraph(form_data.get("Email", ""), norm_st)],
            ["8", Paragraph("Native State", norm_st), ":", Paragraph(form_data.get("Native_State", ""), norm_st)],
            ["9", Paragraph("District", norm_st), ":", Paragraph(form_data.get("District", ""), norm_st)],
            ["10", Paragraph("Government-issued ID Number<br/>(Aadhar copy enclosed)", norm_st), ":", Paragraph(form_data.get("Gov_ID_Number", ""), norm_st)],
            ["11", Paragraph("Organization/Academic Institute (if applicable)", norm_st), ":", Paragraph(form_data.get("Organization_Academic_Institute", ""), norm_st)],
            ["12", Paragraph("Highest Qualification (with Degree & Branch)", norm_st), ":", Paragraph(form_data.get("Highest_Qualification", ""), norm_st)],
            ["13", Paragraph("Status (Pursuing/ Passed out)", norm_st), ":", Paragraph(form_data.get("Status", ""), norm_st)],
            ["14", Paragraph("Beneficiary Category (Tick as applicable)", norm_st), ":", Paragraph(form_data.get("Beneficiary_Category", ""), norm_st)],
            ["15", Paragraph("Involved in previous FSP Program", norm_st), ":", Paragraph(form_data.get("Previous_FSP_Program", ""), norm_st)],
            ["16", Paragraph("If previous answer is, yes provide details<br/>(Program Name / Conducting Institute / Date)", norm_st), ":", Paragraph(f"1. {form_data.get('Previous_FSP_Details_1', '')}<br/>2. {form_data.get('Previous_FSP_Details_2', '')}", norm_st)],
        ]
        
        t_style = TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 4),
            ('SPAN', (0, 0), (1, 0)), 
            ('SPAN', (0, 1), (1, 1)), 
        ])
        
        data[0].insert(1, "")
        data[1].insert(1, "")
        
        t = Table(data, colWidths=[usable_w*0.05, usable_w*0.35, usable_w*0.05, usable_w*0.55])
        t.setStyle(t_style)
        elements.append(t)
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("I hereby declare that all the information provided above is true.", norm_st))
        elements.append(Spacer(1, 10))
        
        sign_img = None
        if form_data.get("sign_url"):
            try:
                sign_buf = fetch_image_as_jpeg(form_data["sign_url"], target_size=(300, 100))
                sign_img = RLImage(sign_buf, width=1.5*inch, height=0.5*inch)
                sign_img.hAlign = 'RIGHT'
            except Exception:
                pass

        if sign_img:
            elements.append(sign_img)
        else:
            elements.append(Spacer(1, 0.5*inch))
            
        elements.append(Paragraph("Applicant Signature", ParagraphStyle('r', fontName='Helvetica-Bold', fontSize=9, alignment=2)))
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("(For office purpose)<br/>The above submitted information has been verified and recommended.", norm_st))
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("(Signature)<br/>Course Co-ordinator", ParagraphStyle('r2', fontName='Helvetica-Bold', fontSize=9, alignment=2)))
        
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("1 Any of the government issued ID: Aadhaar card<br/>2 Participants are not allowed to enroll in the same program for more than once", ParagraphStyle('small', fontName='Helvetica-Oblique', fontSize=8)))
        
        doc.build(elements)
        buf.seek(0)
        return buf
        
    # --- END BOOTCAMP BRANCH ---


    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=0.8*cm, bottomMargin=0.8*cm,
        leftMargin=1.2*cm, rightMargin=1.2*cm,
    )
    W, H = A4
    usable_w = W - 3.6*cm

    styles = getSampleStyleSheet()
    
    title_st = ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=12, alignment=1, spaceAfter=4)
    sub_st = ParagraphStyle('sub', fontName='Helvetica-Bold', fontSize=10, alignment=1, spaceAfter=8)
    norm_st = ParagraphStyle('norm', fontName='Helvetica', fontSize=9)
    bold_st = ParagraphStyle('bold', fontName='Helvetica-Bold', fontSize=9)
    right_st = ParagraphStyle('right', fontName='Helvetica', fontSize=9, alignment=2)
    
    story = []
    
    story.append(Paragraph("Nomination Form", title_st))
    
    level_val = (form_data.get("Level") or "").capitalize()
    if level_val in ("Advanced", "Basic"):
        prog_title = f"Government Officials Training ({level_val}) Programme"
    else:
        prog_title = "Government Officials Training Programme"
        
    story.append(Paragraph(prog_title, sub_st))
    
    # Table 0: Training Programme Details
    story.append(Paragraph("Training Programme Details", bold_st))
    t0_data = [
        [Paragraph("Name of Training Programme", norm_st), Paragraph(form_data.get("Course_Name", ""), norm_st)],
        [Paragraph("Name of Technology", norm_st), Paragraph(form_data.get("Technology", ""), norm_st)],
        [Paragraph("Resource Centre Name", norm_st), Paragraph(form_data.get("Resource_Centre_Name", ""), norm_st)],
        [Paragraph("Date of Training", norm_st), Paragraph(form_data.get("Date_of_Training", ""), norm_st)]
    ]
    t0 = Table(t0_data, colWidths=[usable_w*0.4, usable_w*0.6])
    t0.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 2)
    ]))
    story.append(t0)
    story.append(Spacer(1, 4))
    
    # Table 1: Personal Information
    story.append(Paragraph("Personal Information", bold_st))
    t1_data = [
        [Paragraph("NAME<br/>Prof./Dr./Mr./Ms.", norm_st), Paragraph(f"{form_data.get('Title','')} {form_data.get('Name','')}", norm_st), "", ""],
        [Paragraph("DESIGNATION:", norm_st), Paragraph(form_data.get("Designation", ""), norm_st), Paragraph("ORGANISATION:", norm_st), Paragraph(form_data.get("Organisation", ""), norm_st)],
        [Paragraph("DATE OF BIRTH :", norm_st), Paragraph(form_data.get("DOB", ""), norm_st), Paragraph("GENDER(M/F)", norm_st), Paragraph(form_data.get("Gender", ""), norm_st)],
        [Paragraph("AADHAR No.", norm_st), Paragraph(form_data.get("Aadhar", ""), norm_st), "", ""],
        [Paragraph("CONTACT NUMBER &<br/>E- MAIL", norm_st), Paragraph(f"{form_data.get('Contact_Number','')} / {form_data.get('Email','')}", norm_st), "", ""],
        [Paragraph("NAME OF THE<br/>ORGANISATION/<br/>DEPARTMENT", norm_st), Paragraph(form_data.get("Organisation_Department", ""), norm_st), "", ""],
        [Paragraph("COMPLETE ADDRESS /<br/>CONTACT NUMBERS /<br/>E- MAIL OF THE INSTITUTE", norm_st), Paragraph(form_data.get('Institute_Details', ''), norm_st), "", ""]
    ]
    t1 = Table(t1_data, colWidths=[usable_w*0.25, usable_w*0.25, usable_w*0.25, usable_w*0.25])
    t1.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('SPAN', (1,0), (3,0)),
        ('SPAN', (1,3), (3,3)),
        ('SPAN', (1,4), (3,4)),
        ('SPAN', (1,5), (3,5)),
        ('SPAN', (1,6), (3,6)),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 2)
    ]))
    story.append(t1)
    story.append(Spacer(1, 4))
    
    # Table 2: Educational Qualifications
    story.append(Paragraph("Educational / Professional Qualifications", bold_st))
    t2_data = [
        [Paragraph("EDUCATIONAL / PROFESSIONAL QUALIFICATIONS (GRADUATION ONWARDS)", bold_st), "", "", ""],
        [Paragraph("SL. No.", bold_st), Paragraph("YEAR", bold_st), Paragraph("DEGREE", bold_st), Paragraph("UNIVERSITY/INSTITUTE", bold_st)],
        ["1", Paragraph(form_data.get("Edu1_Year",""), norm_st), Paragraph(form_data.get("Edu1_Degree",""), norm_st), Paragraph(form_data.get("Edu1_University",""), norm_st)],
        ["2", Paragraph(form_data.get("Edu2_Year",""), norm_st), Paragraph(form_data.get("Edu2_Degree",""), norm_st), Paragraph(form_data.get("Edu2_University",""), norm_st)],
        ["3", Paragraph(form_data.get("Edu3_Year",""), norm_st), Paragraph(form_data.get("Edu3_Degree",""), norm_st), Paragraph(form_data.get("Edu3_University",""), norm_st)]
    ]
    t2 = Table(t2_data, colWidths=[usable_w*0.1, usable_w*0.2, usable_w*0.3, usable_w*0.4])
    t2.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('SPAN', (0,0), (3,0)),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (3,1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 2)
    ]))
    story.append(t2)
    story.append(Spacer(1, 4))
    
    # Table 3: Experience
    t3_data = [
        [Paragraph("RESEARCH / TECHNICAL EXPERIENCE", bold_st), "", "", ""],
        [Paragraph("SL.NO.", bold_st), Paragraph("YEAR", bold_st), Paragraph("AREA OF EXPERTISE", bold_st), Paragraph("CENTRE", bold_st)],
        ["1", Paragraph(form_data.get("Exp1_Year",""), norm_st), Paragraph(form_data.get("Exp1_Area_of_Expertise",""), norm_st), Paragraph(form_data.get("Exp1_Centre",""), norm_st)],
        ["2", Paragraph(form_data.get("Exp2_Year",""), norm_st), Paragraph(form_data.get("Exp2_Area_of_Expertise",""), norm_st), Paragraph(form_data.get("Exp2_Centre",""), norm_st)],
        ["3", Paragraph(form_data.get("Exp3_Year",""), norm_st), Paragraph(form_data.get("Exp3_Area_of_Expertise",""), norm_st), Paragraph(form_data.get("Exp3_Centre",""), norm_st)]
    ]
    t3 = Table(t3_data, colWidths=[usable_w*0.1, usable_w*0.2, usable_w*0.4, usable_w*0.3])
    t3.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('SPAN', (0,0), (3,0)),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (3,1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 2)
    ]))
    story.append(t3)
    story.append(Spacer(1, 4))
    
    # Table 4: Signature / Photo block
    photo_elem = ""
    photo_url = form_data.get("photo_url")
    if photo_url:
        try:
            img_buf = fetch_image_as_jpeg(photo_url, target_size=(300, 375))
            photo_elem = RLImage(img_buf, width=1.2*inch, height=1.5*inch)
        except Exception:
            photo_elem = "[Photo]"
            
    sign_elem = ""
    sign_url = form_data.get("sign_url")
    if sign_url:
        try:
            img_buf = fetch_image_as_jpeg(sign_url, target_size=(300, 100))
            sign_elem = RLImage(img_buf, width=1.5*inch, height=0.5*inch)
        except Exception:
            sign_elem = "[Signature]"
            
    t4_data = [
        [photo_elem, sign_elem],
        ["", Paragraph("Signature of the Official<br/>Recommended/Not Recommended<br/>(By the Head of the Institute)", right_st)],
        ["", Paragraph("<br/><br/><br/>(Signature of head of institution)<br/>Name & Designation with Seal", right_st)]
    ]
    
    t4 = Table(t4_data, colWidths=[usable_w*0.3, usable_w*0.7])
    t4.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('SPAN', (0,0), (0,-1))
    ]))
    story.append(t4)
    
    doc.build(story)
    buf.seek(0)
    return buf


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        f = request.form
        photo_url = upload_to_cloudinary(request.files.get("photo"), "photos")
        sign_url = upload_to_cloudinary(request.files.get("signature"), "signatures")
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
            "institute_address": f.get("Institute_Address"), "institute_contact": f.get("Institute_Contact"), "institute_email": f.get("Institute_Email"),
            "highest_qual": f.get("Highest_Qualification"),
            "edu1_year": f.get("Edu1_Year"), "edu1_degree": f.get("Edu1_Degree"), "edu1_university": f.get("Edu1_University"),
            "edu2_year": f.get("Edu2_Year"), "edu2_degree": f.get("Edu2_Degree"), "edu2_university": f.get("Edu2_University"),
            "edu3_year": f.get("Edu3_Year"), "edu3_degree": f.get("Edu3_Degree"), "edu3_university": f.get("Edu3_University"),
            "exp1_year": f.get("Exp1_Year"), "exp1_area": f.get("Exp1_Area_of_Expertise"), "exp1_centre": f.get("Exp1_Centre"),
            "exp2_year": f.get("Exp2_Year"), "exp2_area": f.get("Exp2_Area_of_Expertise"), "exp2_centre": f.get("Exp2_Centre"),
            "exp3_year": f.get("Exp3_Year"), "exp3_area": f.get("Exp3_Area_of_Expertise"), "exp3_centre": f.get("Exp3_Centre"),
            "prev_fsp": f.get("Previous_FSP_Program"), "prev_fsp_details": f.get("Previous_FSP_Details_1"),
            "course_start_date": f.get("Course_Start_Date"), "resource_centre": f.get("Resource_Centre_Name"),
            "photo_url": photo_url, "sign_url": sign_url
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



@app.route("/admin/delete_all", methods=["POST"])
def admin_delete_all():
    if not session.get("admin"):
        abort(403)
    db = get_db()
    db.delete_many({})
    flash("All nominations deleted successfully.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/zip/pdfs")
def admin_zip_pdfs():
    if not session.get("admin"):
        abort(403)
    db = get_db()
    rows = list(db.find())
    if not rows:
        flash("No submissions yet.", "warning")
        return redirect(url_for("admin"))
    
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

@app.route("/admin/zip/docxs")
def admin_zip_docxs():
    if not session.get("admin"):
        abort(403)
    db = get_db()
    rows = list(db.find())
    if not rows:
        flash("No submissions yet.", "warning")
        return redirect(url_for("admin"))
    
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
        db.delete_one({"_id": obj_id})
    flash("Entry deleted.", "success")
    return redirect(url_for("admin"))


# ── Init & run ────────────────────────────────────────────────────────────────

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
