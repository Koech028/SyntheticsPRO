# routes/admin.py
from flask import Blueprint, jsonify, request
from database import mongo

admin_bp = Blueprint("admin", __name__)

# ✅ Admin Dashboard Summary Route
@admin_bp.route("/dashboard", methods=["GET"])
def admin_dashboard():
    blogs_count = mongo.db.blogs.count_documents({})
    messages_count = mongo.db.contacts.count_documents({})
    return jsonify({
        "blogs_total": blogs_count,
        "messages_total": messages_count
    })

# ✅ Fetch all contact messages
@admin_bp.route("/messages", methods=["GET"])
def get_messages():
    messages = list(mongo.db.contacts.find())
    for msg in messages:
        msg["_id"] = str(msg["_id"])
    return jsonify(messages)

# ✅ Delete a contact message
@admin_bp.route("/messages/<id>", methods=["DELETE"])
def delete_message(id):
    result = mongo.db.contacts.delete_one({"_id": id})
    if result.deleted_count:
        return jsonify({"message": "Message deleted successfully"})
    return jsonify({"error": "Message not found"}), 404
