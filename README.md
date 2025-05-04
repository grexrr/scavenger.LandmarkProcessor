# 🎯 Module Objective

This module aims to provide **dynamic generation and supplementation of landmark content** for the city scavenger hunt game.
Its responsibilities include:

1. Automatically generating new landmarks and riddles based on external data (e.g. OpenStreetMap POIs) or game requests.
2. Managing landmark and riddle data and storing them in MongoDB for use by the main game service.
3. Ensuring continuous and rich gameplay by generating content in real-time when landmarks/riddles are running low.

---

## 🧱 Architecture

### 🎲 Core Functions

#### 1️⃣ Landmark Generation

* Accept POI data (name, latitude, longitude) from OSM or other external sources.
* Generate riddles for landmarks using GPT API.
* Format as standardized Landmark data and save to MongoDB.

#### 2️⃣ Riddle Supplementation

* Dynamically generate new riddles when all riddles for an existing landmark are exhausted.
* Append new riddles to the landmark’s riddle list for future use.

#### 3️⃣ On-Demand Landmark Request (Triggered by Game)

* Allow the game to request new landmarks when local landmark data is insufficient.
* Automatically determine whether the requested landmark exists; if not, generate and return a new one.

#### 4️⃣ Admin & Batch Import

* Support bulk import of POI data.
* Automatically generate riddles and store them in MongoDB.

---

### 🗺️ Data Model

#### Landmark (MongoDB Collection: `landmarks`)

```json
{
  "_id": "auto-generated",
  "name": "Honan Chapel",
  "latitude": 51.8935,
  "longitude": -8.4900,
  // (optional) other OSM-related metadata
}
```

#### Riddle (MongoDB Collection: `riddles`)

```json
{
  "_id": "auto-generated",
  "landmark_id": "landmark-uuid",
  "style": "historic",
  "content": "Echoes of vows and silent prayer linger here",
  "created_at": "2025-05-04T13:00:00Z"
}
```

---

## 🔌 API (To be defined later)

(Interfaces will be defined according to future implementation needs)

---

## 🧹 Notes

* **GPT Integration** will be handled internally (sync or async optional).
* **Riddle quality control and deduplication** can be added in future versions.
* **Loose coupling with the game service** — the game simply requests and consumes landmark data.
* **Shared MongoDB storage** — no need for duplicate databases.

---

## 🚦 Future Enhancements

* Support for riddles of different styles and difficulty levels (e.g. child-friendly or challenge modes).
* Full API specification for admin and game-side operations.
* Integration with OpenStreetMap API for real-time POI data ingestion.
* Narrative Arcs: support for riddle continuity and storyline.
* Versioning and history tracking for data iteration.

---

## ✅ Conclusion

The Landmark Generator Microservice will serve as the **dynamic content production hub** for the scavenger hunt game.
By decoupling from the game logic and integrating with MongoDB via standardized APIs, it ensures a continuously engaging gameplay experience with real-time landmark and riddle generation.