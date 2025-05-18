# Module Objective

This module provides **dynamic generation and management of city landmark and riddle content** as a microservice, used by the scavenger hunt game system. It is divided into two fully decoupled components:

1. **Landmark Preprocessor**: fetches and processes POI data from OSM and stores clean landmarks into MongoDB.
2. **Riddle Generator**: loads landmarks from MongoDB and generates riddles using either OpenAI or local language models, saving them to a separate `riddles` collection.

Its responsibilities include:

* Automatically generating and saving structured landmark and riddle data to MongoDB.
* Decoupling game content generation from runtime gameplay, enabling offline batch generation or admin-triggered updates.
* Supporting future on-demand content requests through a clean and modular service interface.

---

## Architecture

### Core Functions

#### 1. Landmark Preprocessing (OSM to MongoDB)

* Fetch POI data from Overpass API using composite query.
* Extract named POIs with geometry data (ways only).
* Compute centroid coordinates and extract metadata tags.
* Save standardized landmark data to MongoDB `landmarks` collection.

#### 2. Riddle Generation (LLM to MongoDB)

* Load landmark names and IDs from the `landmarks` collection.
* For each (landmark × style) combination, send prompt to an LLM (OpenAI or local).
* Extract and structure riddle content and metadata.
* Store riddles in the `riddles` collection, linked by `landmarkId`.

#### 3. Batch or Offline Mode

* Supports local execution for batch processing.
* Admins can pre-generate riddles and landmarks before runtime.
* Game service may invoke this microservice when content is missing.

#### 4. Extensibility

* Supports both online (OpenAI) and offline (mocked/local) modes.
* Configurable styles through a list of predefined riddle styles.
* Future support for difficulty, feedback-based adaptation, and narrative coherence.

---

## Data Model

### Landmark (MongoDB Collection: `landmarks`)

```json
{
  "_id": "ObjectId",
  "name": "Honan Chapel",
  "latitude": 51.8935,
  "longitude": -8.4900,
  "riddle": null,
  "tags": {
    "building": "chapel",
    "historic": "yes",
    "tourism": "attraction"
  }
}
```

### Riddle (MongoDB Collection: `riddles`)

```json
{
  "_id": "ObjectId",
  "landmarkId": "682a25db03286f981e39c380",
  "name": "Cork Greyhound Track",
  "style": "medieval",
  "source": "gpt-4o",
  "content": "Where shadows chase beneath the moon’s decree...",
  "metadata": {
    "model": "gpt-4o-2024-08-06",
    "created": 1747313463,
    "openai_id": "chatcmpl-BXSLBnFvE0LLy1RbV3mz1ASeJnBsO"
  }
}
```

---

## API

The following endpoints are planned to support integration with the game service and administrative tools:

* `POST /generate-riddles?model=openai`
* `POST /insert-landmarks`
* `GET /riddles?landmarkId=xxx&style=yyy`

---

## Notes

* Landmarks and riddles are stored in separate collections and connected via `landmarkId`.
* The scavenger hunt game service does not generate content, it only queries MongoDB.
* Prompt structure, style selection, and LLM mode are controlled in `riddle_generator.py`.

---

## Future Enhancements

* Riddle difficulty classification and scoring.
* Player-adaptive riddle selection.
* Context-aware prompt enhancement using metadata (e.g., Wikipedia).
* Versioning and riddle history.
* Admin dashboard for content monitoring and override.

---

## Development Log

### May 5, 2025

#### POI Fetcher and Preprocessor

**Implementation**

* Created Overpass API query targeting named POIs in Cork across categories: tourism, historic, building, leisure.
* Implemented centroid calculation using geometric average.
* Stored processed landmarks with `name`, `latitude`, `longitude`, and `tags`.

**Validation**

* Selected known landmarks and verified output in `pre-processed.json`.

**Design Notes**

* Focused on geometry-based ways only.
* Skipped POIs without names.
* Tag cleanup ensures compatibility with downstream modules.

---

### May 18, 2025

#### Riddle Generator Microservice Integration

**Implementation**

* Refactored `riddle_generator.py` into a chainable Python class:

  * `loadLandmarksFromDB()` loads (id, name) from `landmarks`.
  * `generate()` prompts LLM (OpenAI or local) with formatted styles.
  * `storeToDB()` writes to `riddles` with style, content, and metadata.
  * `saveRawToFile()` saves raw responses to disk.

**Features**

* Supports multiple styles per landmark.
* Configurable prompt templates.
* Switchable backend: OpenAI or simulated local model.

**Validation**

* Inserted multiple riddles into MongoDB linked by `landmarkId`.
* Verified structure and content integrity.

**Design Notes**

* Output format matches future `Riddle.java` and `RiddleRepository`.
* Errors are logged per landmark-style pair.
* Supports clean overwrite or append logic.

