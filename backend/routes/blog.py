# backend/routes/blog.py
from flask import Blueprint, request, jsonify, session
from bson import ObjectId
from bson.errors import InvalidId
from ..database import mongo  # <-- relative import
import datetime
from functools import wraps

blog_bp = Blueprint("blog", __name__)

# ---------- Authentication decorator ----------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function


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
        # Try to find by slug first
        blog = mongo.db.blogs.find_one({"slug": identifier})

        # If not found by slug, try ObjectId
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

# ---------- Create Blog ---------
@blog_bp.route("/", methods=["POST", "OPTIONS"])
@admin_required
def create_blog():
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    try:
        data = request.json
        if not data.get("title") or not data.get("content"):
            return jsonify({"error": "Title and content are required"}), 400

        data["created_at"] = datetime.datetime.utcnow()
        data["updated_at"] = datetime.datetime.utcnow()

        # ---------- Slug Generation ----------
        import re
        slug_base = re.sub(r'[^a-zA-Z0-9]+', '-', data["title"].lower()).strip('-')

        existing = mongo.db.blogs.find_one({"slug": slug_base})
        if existing:
            slug_base += f"-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        data["slug"] = slug_base
        # --------------------------------------

        result = mongo.db.blogs.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return jsonify(data), 201

    except Exception as e:
        print("❌ Error creating blog:", e)
        return jsonify({"error": str(e)}), 500


# ---------- Update Blog ----------
@blog_bp.route("/<id>", methods=["PUT", "OPTIONS"])
@admin_required
def update_blog(id):
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    try:
        data = request.json
        data["updated_at"] = datetime.datetime.utcnow()

        result = mongo.db.blogs.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )

        if result.matched_count:
            return jsonify({"message": "Blog updated successfully"}), 200
        return jsonify({"error": "Blog not found"}), 404

    except InvalidId:
        return jsonify({"error": "Invalid blog ID"}), 400
    except Exception as e:
        print("❌ Error updating blog:", e)
        return jsonify({"error": str(e)}), 500


# ---------- Delete Blog ----------
@blog_bp.route("/<id>", methods=["DELETE", "OPTIONS"])
@admin_required
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
