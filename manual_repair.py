from pymongo import MongoClient
from bson import ObjectId

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "scavengerhunt"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
meta_col = db["landmark_metadata"]
landmark_col = db["landmarks"]

meta_map = {}
for doc in meta_col.find({}, {"name": 1, "landmarkId": 1, "city": 1}):
    meta_map[(doc["name"], doc.get("city", ""))] = doc["landmarkId"]

changes = []
for (name, city), landmark_id in meta_map.items():
    match = landmark_col.find_one({"name": name, "city": city})
    if not match:
        print(f"[MISS] Landmark not found for meta: {name} ({city})")
        continue

    current_id = str(match["_id"])
    if current_id != landmark_id:
        changes.append((match, landmark_id))

# Step 3: Dry-run 打印
print(f"[INFO] 将更新 {len(changes)} 条记录：")
for match, new_id in changes:
    print(f"  {match['name']} ({match.get('city', '')})  {match['_id']} -> {new_id}")

confirm = input("确认更新这些记录吗？(y/N): ")
if confirm.lower() != "y":
    print("[ABORT] 操作已取消。")
    exit()

# Step 4: 更新（复制+插入+删除旧）
for match, new_id in changes:
    new_doc = dict(match)
    del new_doc["_id"]
    new_doc["_id"] = ObjectId(new_id)

    landmark_col.insert_one(new_doc)
    landmark_col.delete_one({"_id": match["_id"]})

print("[DONE] 更新完成。")

# Step 5: 验证
missing = []
for (name, city), landmark_id in meta_map.items():
    if not landmark_col.find_one({"_id": ObjectId(landmark_id)}):
        missing.append((name, city, landmark_id))

if missing:
    print(f"[VERIFY] 警告：有 {len(missing)} 条 meta 对应的 landmarks 仍然缺失：")
    for name, city, lid in missing:
        print(f"  {name} ({city}) -> {lid}")
else:
    print("[VERIFY] 验证通过：meta 中所有 landmarkId 均在 landmarks 表中找到。")
