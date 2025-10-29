# backend/routes/blog.py
from flask import Blueprint, request, jsonify
from bson import ObjectId
from bson.errors import InvalidId
from ..database import mongo
import datetime
import re

blog_bp = Blueprint("blog", __name__)

# ---------- Get All Blogs ----------
@blog_bp.route("/", methods=["GET", "OPTIONS"])
def get_blogs():
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    try:
        blogs = list(mongo.db.blogs.find().sort("_id", -1))
        for b in blogs:
            b["_id"] = str(b["_id"])
        return jsonify(blogs), 200
    except Exception as e:
        print("❌ Error fetching blogs:", e)
        return jsonify({"error": str(e)}), 500


# ---------- Get Single Blog ----------
@blog_bp.route("/<identifier>", methods=["GET", "OPTIONS"])
def get_single_blog(identifier):
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    try:
        # Try slug first
        blog = mongo.db.blogs.find_one({"slug": identifier})
        if not blog:
            try:
                blog = mongo.db.blogs.find_one({"_id": ObjectId(identifier)})
            except InvalidId:
                pass

        if not blog:
            return jsonify({"error": "Blog not found"}), 404

        blog["_id"] = str(blog["_id"])
        return jsonify(blog), 200

    except Exception as e:
        print("❌ Error fetching blog:", e)
        return jsonify({"error": str(e)}), 500


# ---------- Create Blog ----------
@blog_bp.route("/", methods=["POST", "OPTIONS"])
def create_blog():
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    try:
        data = request.get_json(force=True)
        if not data.get("title") or not data.get("content"):
            return jsonify({"error": "Title and content are required"}), 400

        # Generate slug
        slug_base = re.sub(r'[^a-zA-Z0-9]+', '-', data["title"].lower()).strip('-')
        existing = mongo.db.blogs.find_one({"slug": slug_base})
        if existing:
            slug_base += f"-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        data["slug"] = slug_base
        data["created_at"] = datetime.datetime.utcnow()
        data["updated_at"] = datetime.datetime.utcnow()

        result = mongo.db.blogs.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return jsonify(data), 201

    except Exception as e:
        print("❌ Error creating blog:", e)
        return jsonify({"error": str(e)}), 500

# Add this to your blog.py or create a new uploads.py

@blog_bp.route("/upload-image", methods=["POST"])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        # Save file to your storage (local, S3, etc.)
        filename = secure_filename(file.filename)
        # For now, save locally - in production use cloud storage
        file.save(os.path.join('uploads', filename))
        
        # Return the URL where the image can be accessed
        image_url = f"/uploads/{filename}"
        return jsonify({"url": image_url}), 200
    
    return jsonify({"error": "Invalid file type"}), 400

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


# ---------- Update Blog ----------
@blog_bp.route("/<id>", methods=["PUT", "OPTIONS"])
def update_blog(id):
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # ✅ Clean _id from payload
        if "_id" in data:
            del data["_id"]

        # ✅ Ensure both title & content remain
        existing = mongo.db.blogs.find_one({"_id": ObjectId(id)})
        if not existing:
            return jsonify({"error": "Blog not found"}), 404

        title = data.get("title", existing.get("title"))
        content = data.get("content", existing.get("content"))

        # ✅ Prevent accidental overwriting with empty fields
        if not title or not content:
            return jsonify({"error": "Title and content cannot be empty"}), 400

        # ✅ Regenerate slug ONLY if title actually changed
        if title != existing.get("title"):
            slug_base = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
            existing_slug = mongo.db.blogs.find_one({"slug": slug_base})
            if existing_slug and str(existing_slug["_id"]) != id:
                slug_base += f"-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            data["slug"] = slug_base

        data["updated_at"] = datetime.datetime.utcnow()
        data["title"] = title
        data["content"] = content

        mongo.db.blogs.update_one({"_id": ObjectId(id)}, {"$set": data})

        updated = mongo.db.blogs.find_one({"_id": ObjectId(id)})
        updated["_id"] = str(updated["_id"])
        return jsonify(updated), 200

    except InvalidId:
        return jsonify({"error": "Invalid blog ID"}), 400
    except Exception as e:
        print("❌ Error updating blog:", e)
        return jsonify({"error": str(e)}), 500


# ---------- Delete Blog ----------
@blog_bp.route("/<id>", methods=["DELETE", "OPTIONS"])
def delete_blog(id):
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    try:
        result = mongo.db.blogs.delete_one({"_id": ObjectId(id)})
        if result.deleted_count:
            return jsonify({"message": "Blog deleted successfully"}), 200
        return jsonify({"error": "Blog not found"}), 404

    except InvalidId:
        return jsonify({"error": "Invalid blog ID"}), 400
    except Exception as e:
        print("❌ Error deleting blog:", e)
        return jsonify({"error": str(e)}), 500
