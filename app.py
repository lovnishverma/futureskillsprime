import os
import logging
from flask import Flask
from dotenv import load_dotenv
import cloudinary

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask App
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "nielit_dev_secret_2026")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "static", "uploads")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD")

# Configure Cloudinary
cloudinary.config(
    cloud_name="dyq802zwa",
    api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", "")
)

# Initialize Database
from models.database import init_db
init_db(app)

# Register Blueprints
from routes.public import public_bp
from routes.admin import admin_bp

app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
