from flask import Flask, request, jsonify  
from landmark_preprocessor import LandmarkPreprocessor 
from geopy.geocoders import Nominatim
from pymongo import MongoClient
app = Flask(__name__)

@app.route("/fetch-landmark", methods=["POST"])
def fetchLandmark():
    
    data = request.get_json()
    lat = data.get("latitude")
    lng = data.get("longitude") 
    if lat is None or lng is None:
        return jsonify({"status": "error", "message": "Missing lat/lng"}), 400

    geolocator = Nominatim(user_agent="scavenger-agent")
    location = geolocator.reverse(f"{lat}, {lng}", language='en')
    if not location:
        return jsonify({"status": "error", "message": "Geocode failed"}), 400

    city = location.raw.get("address", {}).get("city") \
        or location.raw.get("address", {}).get("town") \
        or location.raw.get("address", {}).get("village")

    if not city:
        return jsonify({"status": "error", "message": "City not found"}), 400

    print(f"[Landmark Processor]Detected city from lat/lng: {city}")

    mongo_url = "mongodb://localhost:27017"
    client = MongoClient(mongo_url)
    db = client["scavengerhunt"]
    collection = db["landmarks"]

    existing_count = collection.count_documents({"city": city})
    print(f"[Landmark Processor] Found {existing_count} landmarks for city {city} in DB")

    if existing_count > 20:
        print(f"[✓] Landmark data for {city} already initialized, skipping fetch.")
        return jsonify({"status": "ok", "city": city})
    else:
        print(f"[!] Landmark data for {city} appears incomplete ({existing_count}), proceeding with fetch.")

    query = """
    [out:json];
    area["name"={city}]["boundary"="administrative"]->.searchArea;

    (
        way["amenity"]["name"]["amenity"!="parking"]["amenity"!="parking_space"]["amenity"!="bicycle_parking"]["amenity"!="waste_disposal"](area.searchArea);
        way["tourism"]["name"]["tourism"!="guest_house"](area.searchArea);
        way["historic"]["name"](area.searchArea);
        way["leisure"]["name"]["leisure"!="pitch"](area.searchArea);
        way["building"]["name"](area.searchArea);
    );
    out geom;
    """.replace("{city}", city)

    try:
        processed_landmarks = (
        LandmarkPreprocessor(query, city=city)
            .fetchRaw()
            .findRawLandmarks()
            .processRawLandmark()
            .storeToDB(overwrite=False,mongo_url=mongo_url)     
        )
        return jsonify({"status": "ok", "city": city})

    except Exception as e:
        print("[Landmark Processor]Landmark processing failed:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

# @app.route("/preprocess-landmark-meta", methods=["POST"])
# def fetchLandmark():
#     return

if __name__ == "__main__":
    app.run(port=5002)