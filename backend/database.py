# backend/database.py
from flask_pymongo import PyMongo
from pymongo import MongoClient
import certifi, ssl, os

mongo = PyMongo()

def init_mongo(app):
    """Initialize MongoDB with TLS 1.2 (compatible with new PyMongo)."""
    uri = os.getenv("MONGO_URI")
    try:
        # Force TLS 1.2 handshake
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_verify_locations(certifi.where())

        # ✅ The new pymongo expects tls=True, tlsCAFile, and ssl options — NOT ssl_context
        client = MongoClient(
            uri,
            tls=True,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=False,
            tlsAllowInvalidHostnames=False,
            ssl=True,
        )

        # Verify connectivity
        client.admin.command("ping")
        print("✅ Connected to MongoDB Atlas (TLS 1.2 verified)")

        # Pass verified connection to Flask
        app.config["MONGO_URI"] = uri
        mongo.init_app(app)
        return mongo
    except Exception as e:
        print(f"❌ MongoDB TLS connection failed: {e}")
        raise e

def get_db():
    return mongo.db

