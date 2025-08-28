from pymongo import MongoClient
from bson import ObjectId
import pprint

# ====== MongoDB Connection ======
MONGO_URL = "mongodb://localhost:27017"
DB_NAME   = "scavengerhunt"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# ====== 查询 landmark ======
def get_landmark_by_name(name="Glucksman Gallery"):
    landmark = db.landmarks.find_one({"name": name})
    print("\n=== Landmark ===")
    if landmark:
        pprint.pprint(landmark)
    else:
        print(f"Landmark '{name}' not found.")
    return landmark


# ====== 查询 landmark_metadata ======
def get_metadata_for_landmark(name="Glucksman Gallery"):
    lm = db.landmarks.find_one({"name": name}, {"_id": 1})
    if not lm:
        print(f"No landmark found with name '{name}', cannot fetch metadata.")
        return None
    
    lmid = str(lm["_id"])
    metadata = db.landmark_metadata.find_one({"landmarkId": lmid})
    
    print("\n=== Landmark Metadata ===")
    if metadata:
        pprint.pprint(metadata)
    else:
        print(f"No metadata found for landmarkId {lmid}.")
    return metadata


if __name__ == "__main__":
    # 查看 Glucksman Gallery
    get_landmark_by_name("Glucksman Gallery")
    get_metadata_for_landmark("Glucksman Gallery")
