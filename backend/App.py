#backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import timedelta
import os
from dotenv import load_dotenv

# Import blueprints
from database import init_mongo
from routes.auth import auth_bp
from routes.blog import blog_bp
from routes.contacts import contacts_bp
from routes.admin import admin_bp

# -------------------- LOAD ENV --------------------
load_dotenv()

app = Flask(__name__)

# -------------------- SECURITY CONFIG --------------------
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")

# For session cookies (so login persists)
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = False  # set True if using HTTPS (Render)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

# -------------------- CORS --------------------
# Allow your local and deployed frontends
CORS(app,
     supports_credentials=True,
     origins=[
         "http://localhost:8080",  # your React dev server
         "http://localhost:5173",
         "http://127.0.0.1:8080",
         "https://syntheticspro.vercel.app",  # production frontend
     ])

# -------------------- ROUTES --------------------
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(blog_bp, url_prefix="/api/blogs")
app.register_blueprint(contacts_bp, url_prefix="/api/contacts")
app.register_blueprint(admin_bp, url_prefix="/api/admin")

# -------------------- DATABASE --------------------
init_mongo(app)

# -------------------- ROOT --------------------
@app.route("/")
def home():
    return jsonify({"message": "SyntheticsPRO backend running"})

# -------------------- MAIN --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
