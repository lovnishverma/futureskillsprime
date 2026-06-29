from app import app
from services.zip_generator import _generate_and_upload_zip
import logging
logging.basicConfig(level=logging.DEBUG)

with app.app_context():
    _generate_and_upload_zip('docx', True)
