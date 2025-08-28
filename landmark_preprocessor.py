import requests
from pymongo import MongoClient, GEOSPHERE
import json
import os

from landmark_meta_generator import LandmarkMetaGenerator
from dotenv import load_dotenv

load_dotenv()

class LandmarkPreprocessor:

    def __init__(self, query, city="Cork") -> None:
        self.query = query
        self.city = city
        self.osmUrl = "https://overpass-api.de/api/interpreter"
        self.rawFileName = "raw.json"
        self.rawData = None
        self.rawLandmarks = None
        self.processedLandmarks = None

    def fetchRaw(self):
        res = requests.post(self.osmUrl, data={"data": self.query})
        self.rawData = res.text
        return self

    def findRawLandmarks(self, landmarks=None):
        if self.rawData:
            rawData = json.loads(self.rawData)
        else:
            raise ValueError("No raw data. Please run fetchRaw() first.")

        res = {}
        if not landmarks:
            for entry in rawData["elements"]:
                info = entry.get("tags", None)
                if info and "name" in info:
                    res[info["name"]] = entry
        else:
            for landmark in landmarks:
                for entry in rawData["elements"]:
                    info = entry.get("tags", None)
                    if info and "name" in info and info["name"] == landmark:
                        res[landmark] = entry
                        break
                else:
                    print(f"[Warn] {landmark} Not Found!")

        self.rawLandmarks = res
        return self

    def processRawLandmark(self):
        if not self.rawLandmarks:
            raise ValueError("No raw landmarks. Please run findRawLandmarks() first.")

        res = {}
        for name, info in self.rawLandmarks.items():
            package = {}

            # centroids
            centroid_lat = sum(pt["lat"] for pt in info["geometry"]) / len(info["geometry"])
            centroid_lon = sum(pt["lon"] for pt in info["geometry"]) / len(info["geometry"])

            package["latitude"] = centroid_lat
            package["longitude"] = centroid_lon

            # Keep all geometry points
            geometry_points = []
            for pt in info["geometry"]:
                geometry_points.append({
                    "lat": pt["lat"],
                    "lon": pt["lon"]
                })

            package["geometry"] = geometry_points

            info["tags"].pop("name", None)
            package["tags"] = info["tags"]
            res[name] = package

        self.processedLandmarks = res
        return self

    def storeToDB(self, overwrite=True):
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGO_DB", "scavengerhunt")

        client = MongoClient(mongo_url)
        db = client[db_name]
        landmark_collection = db.landmarks

        if overwrite:
            landmark_collection.delete_many({"city": self.city})

        # check (name, city) turple storing in sets
        existing_names = {
            doc["name"] for doc in landmark_collection.find({"city": self.city}, {"name": 1})
        }

        entries = []
        for name, info in self.processedLandmarks.items():
            if name in existing_names:
                print(f"[!] Skipping duplicate landmark: {name} ({self.city})")
                continue

            coordinates = [[point["lon"], point["lat"]] for point in info["geometry"]]
            if coordinates[0] != coordinates[-1]:
                coordinates.append(coordinates[0])  # close polygon

            geojson_polygon = {
                "type": "Polygon",
                "coordinates": [coordinates]
            }

            entries.append({
                "name": name,
                "city": self.city,
                "centroid": {
                    "latitude": info["latitude"],
                    "longitude": info["longitude"]
                },
                "geometry": geojson_polygon,
                "riddle": None
            })

        if entries:
            landmark_collection.insert_many(entries)
            print(f"[✓] Inserted {len(entries)} new landmarks into MongoDB (city: {self.city}).")
        else:
            print(f"[✓] No new landmarks to insert for {self.city}.")

        landmark_collection.create_index([("geometry", GEOSPHERE)])
        return self


    def saveAsFile(self, filename="processed.json"):
        if not self.processedLandmarks:
            raise ValueError("No processed landmarks to save. Run processRawLandmark() first.")

        os.makedirs("outputfiles", exist_ok=True)
        path = os.path.join("outputfiles", filename)

        with open(path, 'w', encoding='utf-8') as f:  # 添加 encoding='utf-8'
            json.dump(self.processedLandmarks, f, indent=2, ensure_ascii=False)  # 添加 ensure_ascii=False

        print(f"Processed landmarks saved to {path}")
        return self

    def saveRawOSMAsFile(self, filename="raw.json"):
        if not self.rawData:
            raise ValueError("No raw OSM data. Run fetchRaw() first.")

        os.makedirs("outputfiles", exist_ok=True)
        path = os.path.join("outputfiles", filename)

        with open(path, 'w') as f:
            f.write(self.rawData)

        print(f"[✓] Raw OSM data saved to {path}")
        return self


if __name__ == "__main__":
    query = """
    [out:json];
    area["name"="Cork"]["boundary"="administrative"]->.searchArea;

    (
        way["amenity"]["name"]["amenity"!="parking"]["amenity"!="parking_space"]["amenity"!="bicycle_parking"]["amenity"!="waste_disposal"](area.searchArea);
        way["tourism"]["name"]["tourism"!="guest_house"](area.searchArea);
        way["historic"]["name"](area.searchArea);
        way["leisure"]["name"]["leisure"!="pitch"](area.searchArea);
        way["building"]["name"](area.searchArea);
    );
    out geom;
    """

    query = """
    [out:json][timeout:180];
    (
    way["amenity"]["name"]["amenity"!="parking"]["amenity"!="parking_space"]["amenity"!="bicycle_parking"]["amenity"!="waste_disposal"]
        (poly:"23.09998 113.31101 23.10002 113.32784 23.12860 113.32719 23.13010 113.31097");
    way["tourism"]["name"]["tourism"!="guest_house"]
        (poly:"23.09998 113.31101 23.10002 113.32784 23.12860 113.32719 23.13010 113.31097");
    way["historic"]["name"]
        (poly:"23.09998 113.31101 23.10002 113.32784 23.12860 113.32719 23.13010 113.31097");
    way["leisure"]["name"]["leisure"!="pitch"]
        (poly:"23.09998 113.31101 23.10002 113.32784 23.12860 113.32719 23.13010 113.31097");
    way["building"]["name"]
        (poly:"23.09998 113.31101 23.10002 113.32784 23.12860 113.32719 23.13010 113.31097");
    node["historic"]["indoor"!="yes"]
        (poly:"23.09998 113.31101 23.10002 113.32784 23.12860 113.32719 23.13010 113.31097");
    );
    out tags geom;
    """


    # query_landmarks = [
    #     "Glucksman Gallery",
    #     "Cork Greyhound Track",
    #     "Honan Collegiate Chapel",
    #     "the President's Garden",
    #     "Boole Library",
    #     "The Quad / Aula Maxima",
    #     "Brookfield Health Sciences Complex",
    #     "Western Gateway Building"
    # ]

    query_landmarks = [
        "广州市第二少年宫",
        "广州图书馆",
        "广东省博物馆",
        "广州国际金融中心(广州西塔)",
        "海心沙亚运公园",
        "广州塔",
    ]

    processed_landmarks = (
    LandmarkPreprocessor(query)
        .fetchRaw()
        .findRawLandmarks(query_landmarks)
        .processRawLandmark()
        .storeToDB()
        .saveAsFile("guangzhou.json")
        # .saveAsFile("pre-processed.json")
        # .saveRawOSMAsFile("raw.json")
    )

    print("\n[!] Start generating Guangzhou metadata...")

    load_dotenv(override=True)
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("[x] OPENAI_API_KEY not found in environment variables!")
    else:
        meta_generator = LandmarkMetaGenerator(api_key)

        meta_generator.loadLandmarksFromDB()

        original_landmarks = meta_generator.landmarks.copy()
        meta_generator.landmarks = [
            (lm_id, lm_name, city) for lm_id, lm_name, city in original_landmarks
            if lm_name in query_landmarks
        ]

        print(f"[✓] Selected {len(meta_generator.landmarks)} Guangzhou Landmark for metadata generation")

        if len(meta_generator.landmarks) == 0:
            print("[!] Warning: No match landmark, please ensure landmars are stored in DB")
        else:

            meta_generator.fetchWiki().fetchOpenAI()
            meta_generator.saveToFile("guangzhou_metadata.json")
            meta_generator.storeToDB(collection_name="landmark_metadata", overwrite=False)

            print("[✓]Guangzhou landmark metadata generated!")
