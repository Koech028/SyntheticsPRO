# backend/routes/upload.py
from flask import Blueprint, request, jsonify, send_file
from gridfs import GridFS
from bson import ObjectId
from io import BytesIO
from ..database import mongo

upload_bp = Blueprint("upload", __name__)
fs = GridFS(mongo.db)

@upload_bp.route("/", methods=["POST", "OPTIONS"])
def upload_image():
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    if "image" not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400

    file = request.files["image"]

    if not file.mimetype.startswith("image/"):
        return jsonify({"error": "Invalid file type"}), 400

    try:
        # Save the image to MongoDB GridFS
        file_id = fs.put(file.read(), filename=file.filename, content_type=file.mimetype)

        # Build a full absolute URL (works in Render and local dev)
        image_url = f"/api/upload/{file_id}"
      print(f"✅ Image uploaded successfully: {file.filename} -> {image_url}")
       return jsonify({"url": image_url}), 201

    except Exception as e:
        print("❌ Upload error:", e)
        return jsonify({"error": str(e)}), 500


@upload_bp.route("/<file_id>", methods=["GET"])
def get_image(file_id):
    try:
        gridout = fs.get(ObjectId(file_id))
        return send_file(BytesIO(gridout.read()), mimetype=gridout.content_type)
    except Exception as e:
        print("❌ Image fetch error:", e)
        return jsonify({"error": "Image not found"}), 404



