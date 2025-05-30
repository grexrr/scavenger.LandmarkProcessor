import requests
import json
import os

import wikipedia
from openai import OpenAI

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
        docs = collection.find({}, {"_id": 1, "name": 1, "city": 1})
        self.landmarks = [(str(doc["_id"]), doc["name"], doc.get("city", "")) for doc in docs]
        print(f"[✓] Loaded {len(self.landmarks)} landmarks from DB.")
        return self
    
    def fetchWiki(self):
        for lm_id, lm, city in self.landmarks:
            if lm_id not in self.metaInfo:
                    self.metaInfo[lm_id] = {}
                    self.metaInfo[lm_id]["name"] = lm
                    self.metaInfo[lm_id]["city"] = city
            try:
                page = wikipedia.page(lm, auto_suggest=True)
                print(f"[✓] Processing Wiki Page: {lm}")
                
                if "wikipedia" not in self.metaInfo[lm_id]:
                    self.metaInfo[lm_id]["wikipedia"] = {}
                self.metaInfo[lm_id]["wikipedia"]["url"] = page.url
                self.metaInfo[lm_id]["wikipedia"]["summary"] = page.summary
                self.metaInfo[lm_id]["wikipedia"]["details"] = page.content

                if self._aiInsepection(lm, city, page.summary) == True:
                    # if wiki is found, replace summary with detail
                    self.metaInfo[lm_id]["wikipedia"]["details"] = page.content
                    self.metaInfo[lm_id]["wikipedia"].pop("summary")
                else:
                    # found wiki is falsed. remove from library
                    self.metaInfo[lm_id].pop("wikipedia")

            except wikipedia.exceptions.DisambiguationError as e:
                print(f"[!] {lm} disambiguation: {e.options[:3]}")

            except wikipedia.exceptions.PageError:
                print(f"[!] {lm} page not found.")
        return self

    def _aiInsepection(self, lm_name, lm_city, content):
        
        client = OpenAI(api_key=self.api_key)
        
        prompt = f"""
        You are verifying if a Wikipedia article is about a specific landmark.
        Target Landmark: "{lm_name}"
        City: "{lm_city}"
        Text:
        \"\"\"
        {content}
        \"\"\"
        If this page is clearly about the target landmark, respond with **only** the word: `true`. Otherwise, respond with `false`.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a precise document verifier."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=5
            )
            reply = response.choices[0].message.content.strip().lower()
            return reply.startswith("true")

        except Exception as e:
            print(f"[x] GPT error during verification for {lm_name}: {e}")
    
    def saveToFile(self, dir="test.json"):
        with open(dir, 'w', encoding='utf-8') as f:
            json.dump(self.metaInfo, f, ensure_ascii=False, indent=4)
  

if __name__ == "__main__":

        
    load_dotenv(override=True)
    api_key = os.getenv('OPENAI_API_KEY')

    generator = LandmarkMetaGenerator(api_key).loadLandmarksFromDB().fetchWiki()
    generator.saveToFile()