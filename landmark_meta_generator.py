import requests
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os

class LandmarkMetaGenerator:
    def __init__(self, api_key, styles, prompt_template, mongo_url="mongodb://localhost:27017", db_name="scavengerhunt", mode="openai"):
        self.api_key = api_key
        self.styles = styles
        self.prompt_template = prompt_template
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.mode = mode  # "openai" or "local"
        self.rawRiddle = {}
        self.landmarks = []

    def loadLandmarksFromDB(self):
        client = MongoClient(self.mongo_url)
        db = client[self.db_name]
        collection = db.landmarks
        docs = collection.find({}, {"_id": 1, "name": 1})
        self.landmarks = [(str(doc["_id"]), doc["name"]) for doc in docs]
        print(f"[✓] Loaded {len(self.landmarks)} landmarks from DB.")
        return self

    def generate(self):
        for lid, name in self.landmarks:
            if lid not in self.rawRiddle:
                self.rawRiddle[lid] = {}

            for style in self.styles:
                prompt = self.prompt_template.format(style=style, landmark=name)
                if self.mode == "openai":
                    result = self._call_openai(prompt)
                elif self.mode == "local":
                    result = self._call_local_model(prompt)
                else:
                    raise ValueError("Unknown mode: " + self.mode)

                if result:
                    self.rawRiddle[lid][style] = result
                else:
                    print(f"[!] Failed to generate for {name} ({style})")
                    self.rawRiddle[lid][style] = None
        return self


    def storeToDB(self, overwrite=True):
        id_to_name = dict(self.landmarks)
        client = MongoClient(self.mongo_url)
        db = client[self.db_name]
        riddle_collection = db.riddles

        if overwrite:
            riddle_collection.delete_many({})  # Optional clearing step

        entries = []
        for lid, styles in self.rawRiddle.items():
            for style, result in styles.items():
                if not result:
                    continue
                try:
                    content = result["choices"][0]["message"]["content"]
                except Exception as e:
                    print(f"[!] Failed to parse content for {lid} ({style}): {e}")
                    continue
                entry = {
                    "landmarkId": lid,
                    "name": id_to_name.get(lid, "Unknown"),
                    "style": style,
                    "source": "gpt-4o",
                    "content": content,
                    "metadata": {
                        "model": result.get("model", ""),
                        "created": result.get("created", ""),
                        "openai_id": result.get("id", "")
                    }
                }
                entries.append(entry)

        if entries:
            riddle_collection.insert_many(entries)
            print(f"[✓] Inserted {len(entries)} riddles into DB.")
        else:
            print("[!] No riddles to insert.")
        return self

    def saveRawToFile(self, filename="riddles.json"):
        os.makedirs("outputfiles", exist_ok=True)
        path = os.path.join("outputfiles", filename)
        with open(path, "w") as f:
            json.dump(self.rawRiddle, f, indent=2)
        print(f"[✓] Raw LLM responses saved to {path}")
        return self
    
    def _call_openai(self, prompt):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are a creative riddle generator."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 1.0
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def _call_local_model(self, prompt):
        print(f"[Local Mode] Simulating LLM output for:\n{prompt}\n")
        return {
            "choices": [{
                "message": {
                    "content": f"[Simulated LLaMA output for prompt: {prompt[:40]}...]"
                }
            }],
            "model": "llama-3.2-1b",
            "created": 9999999999,
            "id": "local-test-id"
        }

if __name__ == "__main__":
    # with open('openaiAPI.txt', 'r') as f:
    #     api_key = f.readline().strip()

    load_dotenv(override=True)
    api_key = os.getenv('OPENAI_API_KEY')


    styles = ["medieval", "mysterious"]

    PROMPT_TEMPLATE = """Create a {style} riddle about {landmark}. Use the following details:
    - History (if available)
    - Architecture and color
    - Significance
    Keep the riddle concise (max 5 lines) and in a {style} tone."""

    LandmarkMetaGenerator(
        api_key=api_key,
        styles=styles,
        prompt_template=PROMPT_TEMPLATE,
        mode="openai"  # "local"
    ).loadLandmarksFromDB().generate().storeToDB(overwrite=True).saveRawToFile("unprocessed_riddles.json")

