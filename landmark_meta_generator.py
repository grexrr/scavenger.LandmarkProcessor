import requests
import json
import os

import wikipedia

from pymongo import MongoClient
from dotenv import load_dotenv

class LandmarkMetaGenerator:
    def __init__(self, api_key, mongo_url="mongodb://localhost:27017", db_name="scavengerhunt", mode="openai"):
        self.api_key = api_key
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.mode = mode  
        self.metaInfo = {}
        self.landmarks = []

    def loadLandmarksFromDB(self):
        client = MongoClient(self.mongo_url)
        db = client[self.db_name]
        collection = db.landmarks
        docs = collection.find({}, {"_id": 1, "name": 1})
        self.landmarks = [(str(doc["_id"]), doc["name"]) for doc in docs]
        print(f"[✓] Loaded {len(self.landmarks)} landmarks from DB.")
        return self
    
    def fetchSummary(self):
        for lm_id, lm in self.landmarks:
            try:
                content = wikipedia.summary(lm)
                print(f"[✓] Processing: {lm}")
                if lm_id not in self.metaInfo:
                    self.metaInfo[lm_id] = {}
                self.metaInfo[lm_id]["name"] = lm
                self.metaInfo[lm_id]["wikipedia"] = content
            except wikipedia.exceptions.DisambiguationError as e:
                print(f"[!] {lm} disambiguation: {e.options[:3]}")
            except wikipedia.exceptions.PageError:
                print(f"[!] {lm} page not found.")
        return self
    
    def saveToFile(self):
        pass
  

if __name__ == "__main__":

        
    load_dotenv(override=True)
    api_key = os.getenv('OPENAI_API_KEY')
    content = LandmarkMetaGenerator(api_key).loadLandmarksFromDB().fetchSummary().metaInfo
    
    with open ("test.json", 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

        