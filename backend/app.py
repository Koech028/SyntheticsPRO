# backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import timedelta
import os
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
mongo = init_mongo(app)

# -------------------- IMPORT BLUEPRINTS --------------------
from .routes.auth import auth_bp
from .routes.blog import blog_bp
from .routes.contacts import contacts_bp
from .routes.admin import admin_bp
from .routes.upload import upload_bp   # ✅ NEW: GridFS-based upload route

# -------------------- REGISTER BLUEPRINTS --------------------
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(blog_bp, url_prefix="/api/blogs")
app.register_blueprint(contacts_bp, url_prefix="/api/contacts")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(upload_bp, url_prefix="/api/upload")  # ✅ Handles upload & serve from MongoDB

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
    print(f"🌐 Allowed origins: {CORS(app).origins}")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
