import threading
import logging
from io import BytesIO
import zipfile
import re
from datetime import datetime
import cloudinary.uploader
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
            rows = list(db.find({"photo_url": {"$nin": [None, ""]}, "sign_url": {"$nin": [None, ""]}}))
            status_key = f"latest_{doc_type}_completed_zip"
        else:
            rows = list(db.find())
            status_key = f"latest_{doc_type}_all_zip"
            
        if not rows:
            logging.info("No rows found for ZIP generation.")
            return
            
        zip_buf = BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
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
                    
        zip_buf.seek(0)
        
        # Upload to Cloudinary
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        public_id = f"exports/{doc_type}_export_{'completed' if completed_only else 'all'}_{ts}.zip"
        
        logging.info("Uploading ZIP to Cloudinary...")
        upload_result = cloudinary.uploader.upload(
            zip_buf.getvalue(),
            resource_type="raw",
            public_id=public_id,
            invalidate=True
        )
        
        secure_url = upload_result.get("secure_url", "")
        
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
