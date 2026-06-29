import threading
import logging
from io import BytesIO
import zipfile
import re
import os
import tempfile
import glob
from datetime import datetime
import cloudinary.uploader
from flask import current_app
from models.database import get_db, get_config_col
from services.document import generate_pdf, generate_docx, row_to_form_data

def trigger_background_zip(doc_type, completed_only):
    """
    Spawns a background thread to generate a ZIP file and upload to Cloudinary.
    doc_type: 'pdf' or 'docx'
    completed_only: boolean
    """
    thread = threading.Thread(
        target=_generate_and_upload_zip,
        args=(doc_type, completed_only)
    )
    thread.daemon = True
    thread.start()

def _generate_and_upload_zip(doc_type, completed_only):
    try:
        logging.info(f"Starting background ZIP generation for {doc_type} (completed_only={completed_only})...")
        db = get_db()
        config_col = get_config_col()
        
        if completed_only:
            query = {
                "$or": [
                    {"level": {"$regex": "^bootcamp$", "$options": "i"}, "sign_url": {"$nin": [None, ""]}},
                    {"level": {"$not": {"$regex": "^bootcamp$", "$options": "i"}}, "photo_url": {"$nin": [None, ""]}, "sign_url": {"$nin": [None, ""]}}
                ]
            }
            rows = list(db.find(query))
            status_key = f"latest_{doc_type}_completed_zip"
        else:
            rows = list(db.find())
            status_key = f"latest_{doc_type}_all_zip"
            
        if not rows:
            logging.info("No rows found for ZIP generation.")
            return
            
        # Ensure exports directory exists
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        exports_dir = os.path.join(base_dir, "static", "exports")
        os.makedirs(exports_dir, exist_ok=True)
        
        # Clean up old zips to save disk space
        for old_zip in glob.glob(os.path.join(exports_dir, "*.zip")):
            try:
                os.remove(old_zip)
            except Exception:
                pass
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{doc_type}_export_{'completed' if completed_only else 'all'}_{ts}.zip"
        filepath = os.path.join(exports_dir, filename)
        
        logging.info(f"Generating ZIP at {filepath} sequentially to save memory...")
        try:
            with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zf:
                for row in rows:
                    form_data = row_to_form_data(row)
                    safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", row.get("name") or "Nomination")
                    token_short = row.get("token", "")[:6]
                    try:
                        if doc_type == "pdf":
                            buf = generate_pdf(form_data)
                            zf.writestr(f"Nomination_{safe_name}_{token_short}.pdf", buf.getvalue())
                        else:
                            buf = generate_docx(form_data)
                            zf.writestr(f"Nomination_{safe_name}_{token_short}.docx", buf.getvalue())
                    except Exception as doc_e:
                        logging.error(f"Failed to generate {doc_type} for token {token_short}: {doc_e}")
        except Exception as e:
            logging.error(f"Failed to write ZIP: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return
            
        secure_url = f"/static/exports/{filename}"
        
        # Save link to MongoDB config
        config_col.update_one(
            {"_id": "export_links"},
            {"$set": {
                status_key: secure_url,
                f"{status_key}_time": datetime.now().strftime("%Y-%m-%d %H:%M")
            }},
            upsert=True
        )
        
        logging.info(f"Successfully generated and uploaded {status_key} to {secure_url}")
        
    except Exception as e:
        logging.error(f"Failed to generate background zip: {e}")
