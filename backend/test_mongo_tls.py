# test_mongo_tls.py
import pymongo, certifi

uri = "mongodb+srv://tituskipkoech737_db_user:OegHGMdAexqzKVI9@cluster0.fxyiniz.mongodb.net/savanna?retryWrites=true&w=majority&tls=true"

try:
    client = pymongo.MongoClient(uri, tlsCAFile=certifi.where())
    print("✅ Connected:", client.server_info())
except Exception as e:
    print("❌ Connection failed:", e)
