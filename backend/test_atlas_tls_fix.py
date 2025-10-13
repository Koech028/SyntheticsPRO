import certifi
from pymongo import MongoClient

uri = "mongodb+srv://tituskipkoech737_db_user:OegHGMdAexqzKVI9@cluster0.fxyiniz.mongodb.net/savanna?retryWrites=true&w=majority"

try:
    # ✅ Use TLS with official CA certificates (certifi)
    client = MongoClient(
        uri,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=20000,
    )

    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB Atlas using TLS and certifi!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
