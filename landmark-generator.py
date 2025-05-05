import requests

class LandmarkGenerator:

    def __init__(self, query) -> None:
        self.query = query
        self.osmUrl = "https://overpass-api.de/api/interpreter"
        self.rawFileName = "raw.json"
        self.rawData = None

    def fetchRaw(self):
        res = requests.post(self.osmUrl, data={"data": self.query})
        self.rawData = res.text
        return self

    def findRawLandmarks(self, landmarks=None):
        import json
        if self.rawData:
            rawData = json.loads(self.rawData) 
        else: 
            with open('outputfiles/' + self.rawFileName, 'r') as f:
                rawData = json.load(f) 
        
        res = {}

        if not landmarks:
            for entry in rawData["elements"]:
                info = entry.get("tags", None)
                if info and "name" in info:
                    res[info["name"]] = entry
            return res
    
        for landmark in landmarks:
            for entry in rawData["elements"]:
                info = entry.get("tags", None)
                if info and "name" in info and info["name"] == landmark:
                    res[landmark] = entry
                    break
            else:
                print(landmark + " Not Found!")

        return res
    
    def processRawLandmark(self, rawLandmarks, debug=False):
        processed_landmarks = rawLandmarks
        if debug == True:
            return processed_landmarks
        
        for name, info in rawLandmarks.items():
            package = {}
            
            # centroid
            centroid_lat = 0
            centroid_lon = 0
            count = 0
            for geometry in info["geometry"]:
                centroid_lat += geometry["lat"]
                centroid_lon += geometry["lon"]
                count += 1
            package["centroid"] = {
                "lat": centroid_lat, 
                "lon": centroid_lon
                }
            
            # tags
            info["tags"].pop("name", None)
            package["tags"] = info["tags"]
            processed_landmarks[name] = package
            
        return processed_landmarks
    
    def saveAsFile(self, filename=None):
        if not filename:
            filename = self.rawFileName
        if not filename.endswith(".json"):
            filename += '.json'
        if self.rawData is not None:
            with open('outputfiles/' + filename, 'w') as f:
                f.write(self.rawData)
            print("Raw File Written")
        else:
            print("No data to write. Please fetch data first.")


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
    query_landmarks = [
        "Glucksman Gallery", 
        "Cork Greyhound Track", 
        "Honan Collegiate Chapel",
        "the President's Garden",
        "Boole Library",
        "The Quad / Aula Maxima",
        "UCC Memorial",
        "Brookfield Health Sciences Complex"
        "Western Gateway Building"
        ]

    processor = LandmarkGenerator(query)
    processor.fetchRaw().saveAsFile('raw.json')
    
    landmarks = processor.findRawLandmarks()
    landmarks = processor.findRawLandmarks(query_landmarks)
    
    processed_landmarks = processor.processRawLandmark(landmarks)

    ## save
    import json
    with open('outputfiles/' + "pre-processed.json", 'w') as f:
        json.dump(processed_landmarks, f, indent=4)
    print("Landmarks saved to file.")

   