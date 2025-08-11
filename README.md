# scavenger.LandmarkProcessor

## Module Objective

This module provides end-to-end processing of urban Points of Interest (POIs) for use in an LLM-assisted landmark exploration and riddle-generation system. It is divided into two independent submodules with clearly defined responsibilities:

---

### 1. **Landmark Preprocessor**

**Purpose:**
Extracts and filters geospatial POI data from OpenStreetMap (OSM) using Overpass API. It computes location centroids and stores clean landmark entries in MongoDB.

**Key Features:**

* Query-based extraction of candidate landmarks from OSM (e.g., buildings, galleries, parks)

* Filters out non-relevant categories (e.g., parking lots)

* Computes centroid coordinates from polygon geometries

* Normalizes and structures the result into:

  ```json
  {
    "name": "Boole Library",
    "latitude": 51.89,
    "longitude": -8.49,
    "tags": { ... }
  }
  ```

* Writes directly to the `landmarks` collection in MongoDB for use by the game backend

---

### 2. **Landmark Metadata Generator**

**Purpose:**
Enriches raw landmarks with structured semantic metadata by retrieving supplementary content from external sources and summarizing them using LLMs.

**Key Features:**

* Attempts to locate open textual information for each landmark:

  * Wikipedia summaries
  * Official institutional descriptions
  * Cultural and architectural context

* Uses LLMs (e.g., GPT-4 or local models) to process and summarize the retrieved data

* Produces structured metadata fields for each landmark:

  ```json
  {
    "landmarkId": "abc123",
    "metadata": {
      "history": "...",
      "architecture": "...",
      "functions": "...",
      "keywords": ["library", "UCC", "modernism"]
    }
  }
  ```

* Stores results into a new `landmark_metadata` collection or as an embedded `meta` field in the `landmarks` collection

---

### 3. Live Integration with Game Backend (As of Aug. 7, 2025)

**Purpose:**
Automatically initializes city-specific landmark data for any given GPS coordinate at runtime, ensuring data completeness and backend compatibility.

**Workflow:**

* A Java SpringBoot controller receives lat/lng via `/api/game/init-game`
* It delegates to `GameDataRepository.initLandmarkDataFromPosition(lat, lng)`, which sends a POST request to Flask endpoint `/fetch-landmark`
* The Flask service performs reverse geocoding via Nominatim to resolve the city
* It checks if landmarks for that city already exist in MongoDB. If the number of entries is above a defined threshold (e.g., 20), it skips fetching
* Otherwise, it triggers a full Overpass query + landmark extraction + MongoDB insert
* Only after completion does it return the resolved city name back to the Java backend, allowing the game controller to proceed safely

**Advantages:**

* Ensures consistent runtime support for any playable city
* Avoids redundant fetches by checking existing entry counts
* Eliminates race conditions or partial data loads through strict blocking behavior

---

### 4. Environment & Dependencies

* Python 3.10+
* Overpass API (OSM)
* OpenAI API / Local LLM APIs
* PyMongo (MongoDB)
* Geopy for reverse geocoding
* Optional: Wikipedia API, BeautifulSoup (web scraping)

---

## Dev Log

### Aug. 7, 2025 – Backend-triggered Landmark Initialization via Flask

A synchronous cross-service pipeline has been implemented:

1. Java backend receives coordinates from front-end client
2. Coordinates are sent to Python microservice (`/fetch-landmark`)
3. Python service:

   * Reverse geocodes location into city name
   * Checks if landmark data is already populated
   * If not, uses `LandmarkPreprocessor` to pull fresh data from OSM
   * Saves cleaned data to MongoDB
4. City name is returned only after MongoDB writes complete, ensuring consistency

This enables per-location initialization of any city without pre-loading the database manually.

---

### Retrieval Layer – Wikipedia and Fallback Search

* For each landmark in the `landmarks` collection, the module attempts to fetch a Wikipedia page via `wikipedia.page()` using `auto_suggest=True`
* Handles disambiguation errors and page absence with fallback search via `wikipedia.search()` and a re-ranking loop
* All retrieved content is passed through a GPT-based semantic verification step

```python
def _aiInspection(landmark_name, city, wiki_text):
    prompt = f"""
    You are verifying if a Wikipedia article is about a specific landmark.
    Target Landmark: "{landmark_name}"
    City: "{city}"
    Text:
    \"\"\"
    {wiki_text}
    \"\"\"
    If this page is clearly about the target landmark, respond with only: `true`. Otherwise, respond with `false`.
    """
    # Submit to GPT (gpt-4, temperature=0.2)
    return gpt_response.strip().lower().startswith("true")
```

* Entries failing verification are excluded from downstream processing

---

### Visual Context – Image Support for LLM Reasoning

* Extracts the top 5 `.jpg`, `.jpeg`, or `.png` image URLs from the Wikipedia page
* These image links are embedded into a `gpt-4-turbo` prompt using OpenAI’s vision input format
* Visual data assists GPT in architectural or contextual reasoning

---

### Generation Layer – LLM-Based Structured Summarization

* GPT receives a prompt asking for structured metadata including:

  * `history`: 5–10 keywords
  * `architecture`: 5–10 keywords
  * `functions`: 5–10 keywords

* The result is expected in strict JSON format

* If GPT indicates uncertainty, the result is discarded and recorded with a fallback marker

---

### Output Format – Unified Metadata Schema

All processed metadata is written to the `landmark_metadata` collection in MongoDB:

```json
{
  "landmarkId": "<_id>",
  "name": "Boole Library",
  "city": "Cork",
  "meta": {
    "url": "...",
    "images": [...],
    "wikipedia": "...",
    "description": {
      "history": [...],
      "architecture": [...],
      "functions": [...]
    }
  }
}
```

---

### Design Notes: Retrieval-Augmented Generation (RAG)

This module implements a lightweight RAG pipeline with the following stages:

* **Retrieve**: External information (Wikipedia page + image URLs)
* **Verify**: GPT-based semantic alignment check
* **Generate**: Vision-enabled GPT-based summarization

Benefits:

* Higher-quality semantic metadata
* Traceability and debuggability of source data
* A reusable structure suitable for adaptive riddle generation

---

## Next Steps

* Integrate `landmark_metadata` into the Java-side `PuzzleManager` as the primary input for riddle generation
* Use `description` fields to support difficulty estimation or thematic puzzle selection
* Add caching or retry logic for GPT requests to reduce cost and prevent data loss
* Extend support for multilingual metadata output
* Introduce a scheduler to backfill metadata for any newly inserted landmarks on demand

---

Let me know when you're ready to wire `landmark_metadata` into the actual puzzle logic.
Here's the updated `scavenger.LandmarkProcessor` module documentation with today’s full pipeline incorporated:

---

# scavenger.LandmarkProcessor

## Module Objective

This module provides end-to-end processing of urban Points of Interest (POIs) for use in an LLM-assisted landmark exploration and riddle-generation system. It is divided into two independent submodules with clearly defined responsibilities:

---

### 1. **Landmark Preprocessor**

**Purpose:**
Extracts and filters geospatial POI data from OpenStreetMap (OSM) using Overpass API. It computes location centroids and stores clean landmark entries in MongoDB.

**Key Features:**

* Query-based extraction of candidate landmarks from OSM (e.g., buildings, galleries, parks)

* Filters out non-relevant categories (e.g., parking lots)

* Computes centroid coordinates from polygon geometries

* Normalizes and structures the result into:

  ```json
  {
    "name": "Boole Library",
    "latitude": 51.89,
    "longitude": -8.49,
    "tags": { ... }
  }
  ```

* Writes directly to the `landmarks` collection in MongoDB for use by the game backend

---

### 2. **Landmark Metadata Generator**

**Purpose:**
Enriches raw landmarks with structured semantic metadata by retrieving supplementary content from external sources and summarizing them using LLMs.

**Key Features:**

* Attempts to locate open textual information for each landmark:

  * Wikipedia summaries
  * Official institutional descriptions
  * Cultural and architectural context

* Uses LLMs (e.g., GPT-4 or local models) to process and summarize the retrieved data

* Produces structured metadata fields for each landmark:

  ```json
  {
    "landmarkId": "abc123",
    "metadata": {
      "history": "...",
      "architecture": "...",
      "functions": "...",
      "keywords": ["library", "UCC", "modernism"]
    }
  }
  ```

* Stores results into a new `landmark_metadata` collection or as an embedded `meta` field in the `landmarks` collection

---

### 3. Live Integration with Game Backend (As of Aug. 7, 2025)

**Purpose:**
Automatically initializes city-specific landmark data for any given GPS coordinate at runtime, ensuring data completeness and backend compatibility.

**Workflow:**

* A Java SpringBoot controller receives lat/lng via `/api/game/init-game`
* It delegates to `GameDataRepository.initLandmarkDataFromPosition(lat, lng)`, which sends a POST request to Flask endpoint `/fetch-landmark`
* The Flask service performs reverse geocoding via Nominatim to resolve the city
* It checks if landmarks for that city already exist in MongoDB. If the number of entries is above a defined threshold (e.g., 20), it skips fetching
* Otherwise, it triggers a full Overpass query + landmark extraction + MongoDB insert
* Only after completion does it return the resolved city name back to the Java backend, allowing the game controller to proceed safely

**Advantages:**

* Ensures consistent runtime support for any playable city
* Avoids redundant fetches by checking existing entry counts
* Eliminates race conditions or partial data loads through strict blocking behavior

---

### 4. Environment & Dependencies

* Python 3.10+
* Overpass API (OSM)
* OpenAI API / Local LLM APIs
* PyMongo (MongoDB)
* Geopy for reverse geocoding
* Optional: Wikipedia API, BeautifulSoup (web scraping)

---

## Dev Log

### Aug. 7, 2025 – Backend-triggered Landmark Initialization via Flask

A synchronous cross-service pipeline has been implemented:

1. Java backend receives coordinates from front-end client
2. Coordinates are sent to Python microservice (`/fetch-landmark`)
3. Python service:

   * Reverse geocodes location into city name
   * Checks if landmark data is already populated
   * If not, uses `LandmarkPreprocessor` to pull fresh data from OSM
   * Saves cleaned data to MongoDB
4. City name is returned only after MongoDB writes complete, ensuring consistency

This enables per-location initialization of any city without pre-loading the database manually.

---

### Retrieval Layer – Wikipedia and Fallback Search

* For each landmark in the `landmarks` collection, the module attempts to fetch a Wikipedia page via `wikipedia.page()` using `auto_suggest=True`
* Handles disambiguation errors and page absence with fallback search via `wikipedia.search()` and a re-ranking loop
* All retrieved content is passed through a GPT-based semantic verification step

```python
def _aiInspection(landmark_name, city, wiki_text):
    prompt = f"""
    You are verifying if a Wikipedia article is about a specific landmark.
    Target Landmark: "{landmark_name}"
    City: "{city}"
    Text:
    \"\"\"
    {wiki_text}
    \"\"\"
    If this page is clearly about the target landmark, respond with only: `true`. Otherwise, respond with `false`.
    """
    # Submit to GPT (gpt-4, temperature=0.2)
    return gpt_response.strip().lower().startswith("true")
```

* Entries failing verification are excluded from downstream processing

---

### Visual Context – Image Support for LLM Reasoning

* Extracts the top 5 `.jpg`, `.jpeg`, or `.png` image URLs from the Wikipedia page
* These image links are embedded into a `gpt-4-turbo` prompt using OpenAI’s vision input format
* Visual data assists GPT in architectural or contextual reasoning

---

### Generation Layer – LLM-Based Structured Summarization

* GPT receives a prompt asking for structured metadata including:

  * `history`: 5–10 keywords
  * `architecture`: 5–10 keywords
  * `functions`: 5–10 keywords

* The result is expected in strict JSON format

* If GPT indicates uncertainty, the result is discarded and recorded with a fallback marker

---

### Output Format – Unified Metadata Schema

All processed metadata is written to the `landmark_metadata` collection in MongoDB:

```json
{
  "landmarkId": "<_id>",
  "name": "Boole Library",
  "city": "Cork",
  "meta": {
    "url": "...",
    "images": [...],
    "wikipedia": "...",
    "description": {
      "history": [...],
      "architecture": [...],
      "functions": [...]
    }
  }
}
```

---

### Design Notes: Retrieval-Augmented Generation (RAG)

This module implements a lightweight RAG pipeline with the following stages:

* **Retrieve**: External information (Wikipedia page + image URLs)
* **Verify**: GPT-based semantic alignment check
* **Generate**: Vision-enabled GPT-based summarization

Benefits:

* Higher-quality semantic metadata
* Traceability and debuggability of source data
* A reusable structure suitable for adaptive riddle generation

---

## Next Steps

## Next Steps

* Integrate `landmark_metadata` into the Java-side `PuzzleManager` as the primary input for riddle generation
* Use `description` fields to support difficulty estimation or thematic puzzle selection
* Add caching or retry logic for GPT requests to reduce cost and prevent data loss
* Extend support for multilingual metadata output
* Introduce a scheduler to backfill metadata for any newly inserted landmarks on demand

### Critical Issues to Address

* **Duplicate Landmark Prevention**: The system currently performs multiple scans of the same target, causing database duplicates. Implement duplicate detection logic based on landmark name and city before inserting new entries to avoid redundant data storage.

* **Geographic Region Matching**: Address city name mismatches where reverse geocoding returns district names (e.g., "天河区") that don't match with broader city names in the database (e.g., "广州市"). Implement a hierarchical location mapping system to normalize district-level results to their parent city for consistent database queries.
