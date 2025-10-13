# backend/routes/contacts.py
from flask import Blueprint, request, jsonify
from ..database import mongo  # <-- relative import
from bson import ObjectId

contacts_bp = Blueprint("contacts", __name__)

@contacts_bp.route("/", methods=["GET", "OPTIONS"])
def get_contacts():
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200
        
    try:
        contacts = list(mongo.db.contacts.find())
        for contact in contacts:
            contact["_id"] = str(contact["_id"])
        return jsonify(contacts)
    except Exception as e:
        print("Error fetching contacts:", e)
        return jsonify({"error": str(e)}), 500

@contacts_bp.route("/", methods=["POST", "OPTIONS"])
def create_contact():
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200
        
    try:
        data = request.json
        if not data.get("name") or not data.get("email") or not data.get("message"):
            return jsonify({"error": "Name, email, and message are required"}), 400
        
        result = mongo.db.contacts.insert_one(data)
        return jsonify({"_id": str(result.inserted_id), "message": "Contact created successfully"}), 201
    except Exception as e:
        print("Error creating contact:", e)
        return jsonify({"error": str(e)}), 500

@contacts_bp.route("/<id>", methods=["DELETE", "OPTIONS"])
def delete_contact(id):
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200
        
    try:
        result = mongo.db.contacts.delete_one({"_id": ObjectId(id)})
        if result.deleted_count:
            return jsonify({"message": "Contact deleted successfully"})
        return jsonify({"error": "Contact not found"}), 404
    except Exception as e:
        print("Error deleting contact:", e)
        return jsonify({"error": str(e)}), 500

@contacts_bp.route("/<id>/reply", methods=["POST", "OPTIONS"])
def reply_to_contact(id):
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200
        
    try:
        data = request.json
        # Here you would typically send an email with the reply
        # For now, we'll just log it and return success
        print(f"Replying to contact {id}: {data.get('content')}")
        return jsonify({"message": "Reply sent successfully"})
    except Exception as e:
        print("Error replying to contact:", e)
        return jsonify({"error": str(e)}), 500


