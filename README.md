# scavenger.LandmarkProcessor

## Module Objective

This module provides end-to-end processing of urban Points of Interest (POIs) for use in an LLM-assisted landmark exploration and riddle-generation system. It is divided into two independent submodules with clearly defined responsibilities:

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

### 3. Environment & Dependencies

* Python 3.10+
* Overpass API (OSM)
* OpenAI API / Local LLM APIs
* PyMongo (MongoDB)
* Optional: Wikipedia API, BeautifulSoup (web scraping)

### 4. Future Extensions

* Multilingual metadata summarization
* Visual metadata extraction (image → caption or tags)
* Named Entity Recognition (NER) to tag historical figures, periods, or architectural styles
* Integration with graph-based landmark relationship modeling


---

## Dev Log