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

#### May 5, 2025

## Objective

Implement POI fetcher and preprocessor module, and begin work on riddle generation module for the dynamic landmark generator service.

---

## POI Fetcher and Preprocessor

### Implementation

* Added `Preprocessor` class to handle OpenStreetMap queries and POI data processing.

* Implemented `fetchRaw`:

  * Sends POST request to Overpass API.
  * Saves raw POI data to `raw.json` in `outputfiles` directory.

* Implemented `saveAsFile`:

  * Supports saving raw OSM data to disk with automatic `.json` extension.

* Implemented `findRawLandmarks`:

  * If no landmark list is provided, selects all POIs with a `name` tag.
  * If a landmark list is provided, matches POIs against the list and logs missing entries.
  * Uses `for-else` syntax for cleaner missing landmark detection.

* Implemented `processRawLandmark`:

  * Calculates centroid coordinates from `geometry` data.
  * Extracts OSM `tags` (including metadata like `amenity`, `tourism`, `wikidata`, `wikipedia`).
  * Packs processed landmark data into simplified format for consumption.

### Test and Validation

* Fetched and processed Cork POI dataset using composite Overpass query:

  * Included categories: `amenity`, `tourism`, `historic`, `leisure`, `building` (with `name`).
  * Excluded irrelevant categories (`parking`, `waste_disposal`, `pitch`).

* Verified that key landmarks were correctly processed:

  * Glucksman Gallery
  * Boole Library
  * The Quad / Aula Maxima

* Generated `pre-processed.json` containing processed landmarks with centroids and metadata.

### Design Notes

* Used `out geom` to ensure way-type POIs have geometry data.
* Supported both "fetch all" and "fetch selected" landmark modes.
* Simple average used for centroid calculation.
* Skipped POIs without `name` tags.
* Future: Support metadata enrichment with `wikidata` and `wikipedia`.

---

## Riddle Generator

### Implementation

* Added `RiddleGenerator` class to automate riddle generation via GPT API.

* Integrated OpenAI `gpt-4o` model:

  * Configured prompt structure using `_get_template` method.
  * Prompt incorporates landmark name and style, and requests riddles reflecting architecture, history, and significance.

* Implemented `fetchRiddle`:

  * For each landmark and style combination, sends API request.
  * Stores responses in nested dictionary (`landmark -> style -> response`).
  * Logs and skips failed requests.

* Implemented `saveAsFile`:

  * Saves generated riddles as `sample_riddle.json`.
  * Uses nested dictionary format for easy lookup.

### Test and Validation

* Successfully generated riddles for Cork landmarks:

  * Glucksman Gallery
  * Cork Greyhound Track
  * Honan Collegiate Chapel
  * Boole Library
  * The Quad / Aula Maxima

* Generated riddles reflected medieval style and included contextual elements:

  * Materials and architecture
  * Usage and cultural significance
  * Historical and local references

#### Example (medieval style)

```
In yon grand hall of storied stone and lore,
Where students and scholars gather to explore.
A noble square, its heart beats true,
In hues of ancient grey and steadfast blue.
What mighty court holds wisdom’s gleaming core?
```

### Design Notes

* Used nested dictionary for result storage.
* Supported multiple riddle styles via `styles` parameter.
* Prompt templating ensures flexibility and context awareness.
* Future: Clean up response content and store processed riddles alongside raw responses.

---

## Summary

* POI Preprocessor module is complete and generating standardized landmark data.
* Riddle Generator module is functional, supports batch generation, and produces context-aware riddles.
* Future work will focus on refining riddle formatting and enriching prompts with additional metadata.

---
