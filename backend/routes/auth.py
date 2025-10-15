#backend/routes/auth.py
# backend/routes/auth.py
from flask import Blueprint, request, jsonify, session
import os

auth_bp = Blueprint("auth", __name__)

# Admin credentials from environment
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200
    
    try:
        data = request.json
        if not data or not data.get("email") or not data.get("password"):
            return jsonify({"error": "Email and password are required"}), 400

        if data["email"] == ADMIN_EMAIL and data["password"] == ADMIN_PASSWORD:
            # Set session
            session["admin_logged_in"] = True
            session["admin_email"] = data["email"]
            return jsonify({"message": "Login successful", "user": {"email": data["email"]}}), 200
        
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        print("Login error:", e)
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/logout", methods=["POST", "OPTIONS"])
def logout():
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@auth_bp.route("/verify", methods=["GET", "OPTIONS"])
def verify_session():
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    if session.get("admin_logged_in"):
        return jsonify({"valid": True, "user": {"email": session.get("admin_email")}}), 200
    return jsonify({"valid": False}), 401
