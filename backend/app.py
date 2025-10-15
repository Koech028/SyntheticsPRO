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
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True 
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

# -------------------- CORS --------------------
CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "http://127.0.0.1:8080",
        "https://clients.savannadesignsagency.com",
        "https://syntheticspro.vercel.app"
    ]
)

# -------------------- IMPORT BLUEPRINTS --------------------
from .database import init_mongo
from .routes.auth import auth_bp
from .routes.blog import blog_bp
from .routes.contacts import contacts_bp
from .routes.admin import admin_bp

# -------------------- REGISTER BLUEPRINTS --------------------
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(blog_bp, url_prefix="/api/blogs")
app.register_blueprint(contacts_bp, url_prefix="/api/contacts")
app.register_blueprint(admin_bp, url_prefix="/api/admin")

# -------------------- DATABASE --------------------
init_mongo(app)

# -------------------- ROOT ROUTE --------------------
@app.route("/")
def home():
    return jsonify({"message": "SyntheticsPRO backend running"})

# -------------------- MAIN --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
