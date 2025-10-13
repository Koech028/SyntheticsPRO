# backend/middleware/auth.py
import jwt
from flask import request, jsonify
import os

JWT_SECRET = os.getenv("SECRET_KEY", "fallback-secret-key")

def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            request.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    
    decorated.__name__ = f.__name__
    return decorated