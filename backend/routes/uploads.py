from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os

uploads_bp = Blueprint("uploads", __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@uploads_bp.route("/api/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        file_url = f"https://syntheticspro-haw3.onrender.com/{UPLOAD_FOLDER}/{filename}"
        return jsonify({"url": file_url}), 200
    return jsonify({"error": "Invalid file type"}), 400
