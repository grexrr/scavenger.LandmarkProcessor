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
                
                if "meta" not in self.metaInfo[lm_id]:
                    self.metaInfo[lm_id]["meta"] = {}
                self.metaInfo[lm_id]["meta"]["url"] = page.url
                self.metaInfo[lm_id]["meta"]["summary"] = page.summary
                self.metaInfo[lm_id]["meta"]["images"] = [img for img in page.images if img.lower().endswith((".jpg", ".jpeg", ".png"))]
                
                ### APPLY AI INSPECTION
                if self._aiInsepection(lm, city, page.summary) == True:
                    # if wiki is found, replace summary with detail
                    self.metaInfo[lm_id]["meta"]["wikipedia"] = page.content
                    self.metaInfo[lm_id]["meta"].pop("summary")
                else:
                    # found wiki is falsed. remove from library
                    self.metaInfo[lm_id].pop("meta")

            except wikipedia.exceptions.DisambiguationError as e:
                print(f"[!] {lm} disambiguation: {e.options[:3]}")

            except wikipedia.exceptions.PageError:
                print(f"[!] {lm} page not found.")
        return self

    
    def fetchOpenAI(self):

        for lm_id in self.metaInfo:
            lm_name = self.metaInfo[lm_id]["name"]
            lm_city = self.metaInfo[lm_id]["city"]

            content = self.metaInfo[lm_id].get("meta", {}).get("wikipedia", None)
            image_urls = self.metaInfo[lm_id].get("meta", {}).get("images", None)

            result = self._aiSummarizeLandmark(lm_name, lm_city, content, image_urls)
            
            if "meta" not in self.metaInfo[lm_id]:
                self.metaInfo[lm_id]["meta"] = {}
            
            self.metaInfo[lm_id]["meta"]["description"] = result.get("metadata", {})

        return self
            

    def _aiSummarizeLandmark(self, lm_name, lm_city, content=None, image_urls=None):
        client = OpenAI(api_key=self.api_key)
        
        if not content:
            content = "None"

        image_urls = image_urls[:5] if image_urls else []
        
        prompt = f"""
        Provide structured information about a real-world landmark called "{lm_name}" located in "{lm_city}".
        Additional information: {content}

        If you recognize this place, summarize its:
        - history
        - architecture
        - functions
        Each in 5~10 keywords.

        Respond with expected JSON format:
        {{
        "history": [...],
        "architecture": [...],
        "functions": [...]
        }}
        
        Do not include any explanation or commentary.
        If you're unsure about this landmark, clearly and reply only the following text: "This landmark is not recognized with enough confidence."
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    # {"role": "system", "content": "You are a precise document verifier."},
                    {"role": "user", 
                     "content": 
                     [{"type": "text", "text": prompt}] + 
                     [{"type": "image_url", "image_url": { "url": url, "detail": "high" }} for url in image_urls]
                     }
                ],
                temperature=0.5,
                max_tokens=500
            )
            text = response.choices[0].message.content

            if "not recognized" in text.lower():
                return {
                "source": "openai",
                "confidence": False,
                "message": "LLM could not confirm landmark identity."
            }
            try:
                metadata = json.loads(text)
                return {
                    "source": "openai",
                    "confidence": True,
                    "metadata": metadata
                }
            except json.JSONDecodeError:
                print(f"[x] GPT output for {lm_name} could not be parsed as JSON:\n{text}")
                return {
                    "source": "openai",
                    "confidence": False,
                    "message": "Malformed JSON returned by GPT."
                }
        except Exception as e:
            print(f"[x] Fallback GPT error for {lm_name}: {e}")
            return {
                "source": "openai", 
                "confidence": False, 
                "message": "Error during fallback."
            }
    
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
            

    def saveToFile(self, filename="meta_output.json"):
        os.makedirs("outputfiles", exist_ok=True)
        path = os.path.join("outputfiles", filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.metaInfo, f, ensure_ascii=False, indent=4)

    def storeToDB(self, collection_name="landmark_metadata", overwrite=True):
        client = MongoClient(self.mongo_url)
        db = client[self.db_name]
        collection = db[collection_name]

        if overwrite:
            collection.delete_many({})
            print(f"[!] Cleared existing collection: {collection_name}")

        entries = []

        for lm_id, info in self.metaInfo.items():
            entry = {
                "landmarkId": lm_id,
                "name": info["name"],
                "city": info.get("city", ""),
                "meta": info.get("meta", {})
            }
            entries.append(entry)

        if entries:
            collection.insert_many(entries)
            print(f"[✓] Inserted {len(entries)} documents into {collection_name}")
        else:
            print("[!] No entries to insert.")


if __name__ == "__main__":

    load_dotenv(override=True)
    api_key = os.getenv('OPENAI_API_KEY')

    generator = (
        LandmarkMetaGenerator(api_key)
        .loadLandmarksFromDB()
        .fetchWiki()
        .fetchOpenAI()
    )

    generator.saveToFile("final-meta.json")
    generator.storeToDB()
