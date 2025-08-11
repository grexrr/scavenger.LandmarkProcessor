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

# meta_collection = db["landmark_metadata"]
# lmids = []
# for doc in meta_collection.find({}, {"landmarkId": 1, "_id": 0}):
#     lmids.append(doc["landmarkId"])

# print(f"Found {len(lmids)} valid landmark IDs")
# print(f"Valid IDs: {lmids}")

# # 获取有效ID对应的地标名称
# valid_landmarks = {}  # {name: valid_id}

# for lm_id in lmids:
#     # 确保 lm_id 是 ObjectId 类型
#     if isinstance(lm_id, str):
#         lm_id = ObjectId(lm_id)
    
#     doc = landmark_collection.find_one({"_id": lm_id}, {"name": 1})
#     if doc:
#         valid_landmarks[doc["name"]] = lm_id
#         print(f"Valid: {doc['name']} -> {lm_id}")
#     else:
#         print(f"WARNING: No landmark found for ID {lm_id}")

# print(f"\nValid landmarks: {list(valid_landmarks.keys())}")

# # 检查每个名称的所有条目
# print("\n=== Checking for duplicates ===")
# for name in valid_landmarks.keys():
#     all_with_name = list(landmark_collection.find({"name": name}, {"_id": 1, "name": 1}))
#     print(f"\nName: '{name}' has {len(all_with_name)} entries:")
    
#     valid_id = valid_landmarks[name]
#     for entry in all_with_name:
#         if entry["_id"] == valid_id:
#             print(f"  ✓ KEEP: {entry['_id']} (valid)")
#         else:
#             print(f"  ✗ DELETE: {entry['_id']} (duplicate)")

# # 找到需要删除的重复条目
# duplicate_ids = []
# for name in valid_landmarks.keys():
#     valid_id = valid_landmarks[name]
#     duplicates = landmark_collection.find({
#         "name": name,
#         "_id": {"$ne": valid_id}
#     }, {"_id": 1})
    
#     for dup in duplicates:
#         duplicate_ids.append(dup["_id"])

# print(f"\nFound {len(duplicate_ids)} duplicate entries to delete")
# print(f"Duplicate IDs: {duplicate_ids}")

# # 删除重复条目
# if duplicate_ids:
#     result = landmark_collection.delete_many({"_id": {"$in": duplicate_ids}})
#     print(f"Deleted {result.deleted_count} duplicate landmarks")
# else:
#     print("No duplicates found to delete")

client.close()

