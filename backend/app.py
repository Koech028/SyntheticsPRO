# backend/app.py
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from datetime import timedelta
import os
import uuid
from dotenv import load_dotenv

# -------------------- LOAD ENV --------------------
load_dotenv()

# -------------------- APP INIT --------------------
app = Flask(__name__)

# -------------------- SECURITY CONFIG --------------------
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")
app.config["SESSION_COOKIE_NAME"] = "session"
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_DOMAIN"] = ".onrender.com"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

# -------------------- CORS --------------------
CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "http://127.0.0.1:8080",
        "https://syntheticindicesreview.com",
        "https://syntheticspro.vercel.app"
    ]
)

# -------------------- DATABASE --------------------
from .database import init_mongo
init_mongo(app)

# -------------------- IMPORT BLUEPRINTS --------------------
from .routes.auth import auth_bp
from .routes.blog import blog_bp
from .routes.contacts import contacts_bp
from .routes.admin import admin_bp

# -------------------- IMAGE UPLOAD CONFIG --------------------
from werkzeug.utils import secure_filename
from flask import Blueprint

upload_bp = Blueprint("upload", __name__)

# Use Render-safe temp dir (normal folders get wiped on deploy)
UPLOAD_FOLDER = "/tmp/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route("/", methods=["POST"])
def upload_image():
    """Handle image uploads from Tiptap editor."""
    if "image" not in request.files:
        return jsonify({"error": "No image file found"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Generate unique filename to avoid collisions
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        # Build absolute public URL
        base_url = request.host_url.rstrip("/")
        file_url = f"{base_url}/uploads/{filename}"
        
        print(f"✅ Image uploaded successfully: {filename}")
        return jsonify({"url": file_url}), 200

    return jsonify({"error": "Invalid file type. Allowed types: png, jpg, jpeg, gif, webp"}), 400

# -------------------- REGISTER BLUEPRINTS --------------------
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(blog_bp, url_prefix="/api/blogs")
app.register_blueprint(contacts_bp, url_prefix="/api/contacts")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(upload_bp, url_prefix="/api/upload")

# -------------------- SERVE UPLOADED IMAGES --------------------
@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    """Serve uploaded images (for Render this reads from /tmp/uploads)."""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"error": "Image not found"}), 404

# -------------------- HEALTH CHECK --------------------
@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "message": "SyntheticsPRO backend running 🚀"})

# -------------------- ROOT ROUTE --------------------
@app.route("/")
def home():
    return jsonify({"message": "SyntheticsPRO backend running 🚀"})

# -------------------- MAIN --------------------
if __name__ == "__main__":
    print("🚀 Starting SyntheticsPRO backend...")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🌐 Allowed origins: {CORS(app).origins}")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

