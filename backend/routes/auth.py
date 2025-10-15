#backend/routes/auth.py
# backend/routes/auth.py
from flask import Blueprint, request, jsonify, session
import os
import logging
from dotenv import load_dotenv

# -------------------- LOAD ENV --------------------
load_dotenv()

auth_bp = Blueprint("auth", __name__)

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

logging.basicConfig(level=logging.INFO)
logging.info(f"Admin email loaded: {ADMIN_EMAIL}")

# -------------------- ROUTES --------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        session["admin_logged_in"] = True
        return jsonify({"message": "Login successful"}), 200

    return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("admin_logged_in", None)
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/verify", methods=["GET"])
def verify_login():
    """✅ Check if admin is logged in"""
    if session.get("admin_logged_in"):
        return jsonify({"authenticated": True}), 200
    return jsonify({"authenticated": False}), 401
