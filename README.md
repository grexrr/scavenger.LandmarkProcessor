# 🎯 Module Objective

This module aims to provide **dynamic generation and supplementation of landmark content** for the city scavenger hunt game as a microservice.
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

## API (To be defined later)

(Interfaces will be defined according to future implementation needs)

---

## Notes

* **GPT Integration** will be handled internally (sync or async optional).
* **Riddle quality control and deduplication** can be added in future versions.
* **Loose coupling with the game service** — the game simply requests and consumes landmark data.
* **Shared MongoDB storage** — no need for duplicate databases.

---

## Future Enhancements

* Support for riddles of different styles and difficulty levels (e.g. child-friendly or challenge modes).
* Full API specification for admin and game-side operations.
* Integration with OpenStreetMap API for real-time POI data ingestion.
* Narrative Arcs: support for riddle continuity and storyline.
* Versioning and history tracking for data iteration.

---

#### May. 5 2025

**Goal: Implement POI fetcher and preprocessor module for OpenStreetMap to generate standardized Landmark data for the dynamic landmark generator service.**

---

* **Initial implementation of `Preprocessor` module:**

  * Created `Preprocessor` class to manage OpenStreetMap queries and POI data processing.
  * Implemented `fetchRaw`:

    * Sends a POST request to Overpass API with the defined query.
    * Retrieves raw POI data and saves to `raw.json` in the `outputfiles` directory.
  * Implemented `saveAsFile`:

    * Allows saving raw OSM data to disk.
    * Automatically adds `.json` extension if necessary.

* **Landmark identification and extraction:**

  * Implemented `findRawLandmarks`:

    * If no landmark list is provided, selects all POIs with a `name` tag.
    * If a landmark list is provided, matches POIs against the list and logs missing entries.
    * Used `for-else` syntax to cleanly identify missing landmarks without boolean flags.

* **Landmark processing and standardization:**

  * Implemented `processRawLandmark`:

    * Processes each raw landmark to calculate centroid coordinates based on the `geometry` field.
    * Extracts and attaches OSM `tags` for metadata (such as `amenity`, `tourism`, `wikidata`, and `wikipedia` when available).
    * Packaged processed landmark data into a simplified format for easy consumption.
    * Added `debug` option to return raw landmark data for debugging purposes.

* **Test run and validation:**

  * Successfully fetched and processed Cork POI dataset using a composite Overpass query:

    * Included categories: `amenity`, `tourism`, `historic`, `leisure`, `building` with `name`.
    * Excluded irrelevant categories such as `parking`, `waste_disposal`, and `pitch`.
  * Confirmed that key landmarks such as Glucksman Gallery, Boole Library, and The Quad were included and correctly processed.
  * Generated `pre-processed.json` containing processed landmark data with centroid coordinates and tags.

---

##### Design Notes

* Applied Overpass API `out geom` query style to ensure all way-type POIs include geometry data for centroid calculation.
* Introduced dynamic landmark fetching mode:

  * If landmark list is empty, all POIs with `name` are included.
  * If landmark list is provided, only exact matches are processed.
* Used simple average method for calculating centroids, suitable for most building and POI geometries.
* Automatically skipped POIs without a `name` to maintain landmark quality.
* Future support planned for metadata enrichment using `wikidata` and `wikipedia` fields for each landmark.

---
