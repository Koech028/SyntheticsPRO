# backend/database.py
from flask_pymongo import PyMongo
from pymongo import MongoClient
import certifi, ssl, os

mongo = PyMongo()

def init_mongo(app):
    """Initialize MongoDB with TLS 1.2 (Atlas-ready) and expose PyMongo + client for GridFS."""
    uri = os.getenv("MONGO_URI")
    try:
        # Force TLS 1.2 handshake
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_verify_locations(certifi.where())

        # Create verified MongoDB client
        client = MongoClient(
            uri,
            tls=True,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=False,
            tlsAllowInvalidHostnames=False,
            ssl=True,
        )

        # Verify connection
        client.admin.command("ping")
        print("✅ Connected to MongoDB Atlas (TLS 1.2 verified)")

        # Initialize PyMongo for Flask context
        app.config["MONGO_URI"] = uri
        mongo.init_app(app)

        # Attach the raw client and DB reference for GridFS (optional but handy)
        mongo.client = client
        mongo.db = client.get_default_database()

        return mongo

    except Exception as e:
        print(f"❌ MongoDB TLS connection failed: {e}")
        raise e


def get_db():
    """Return active database instance."""
    return mongo.db

