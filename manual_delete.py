from pymongo import MongoClient
from bson import ObjectId

mongo_url = "mongodb://localhost:27017"
client = MongoClient(mongo_url)
db = client["scavengerhunt"]
landmark_collection = db["landmarks"]

landmark_names = [
    "University College Cork Main Campus",
    "Bon Secours Hospital",
    "University College Cork Western Campus",
    "University College Cork North Mall Campus",
    "UCC Lee Maltings Complex",
    "North Monastery"
]


query = {"name": {"$in": landmark_names}}
result = landmark_collection.delete_many(query)

print(f"Deleted {result.deleted_count} landmarks")


client.close()

