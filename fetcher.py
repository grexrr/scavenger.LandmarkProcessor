import requests

class Fetcher:
    def __init__(self, query) -> None:
        self.query = query
        self.osmUrl = "https://overpass-api.de/api/interpreter"

    def fetchRaw(self):
        res = requests.post(self.osmUrl, data={"data": query})
        with open('outputfiles/raw.json', 'w') as f:
            f.write(res.text)


if __name__ == "__main__":
    
    query = """
    [out:json];
    area["name"="Cork"]["boundary"="administrative"]->.searchArea;

    (
        way["amenity"]["amenity"!="parking"]["amenity"!="parking_space"]["amenity"!="bicycle_parking"]["amenity"!="waste_disposal"](area.searchArea);
        way["tourism"]["tourism"!="guest_house"](area.searchArea);
        way["historic"](area.searchArea);
        way["leisure"]["leisure"!="pitch"](area.searchArea);
        way["building"]["name"](area.searchArea);
    );
    out geom;
    """

    fetcher = Fetcher(query)
    fetcher.fetchRaw()