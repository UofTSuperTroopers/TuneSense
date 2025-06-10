# Searchworker Refactor Notes

This document summarizes the changes made starting from the refactor of `searchworker.py` into separate functional modules, and details updates made across the PyQt frontend, backend, and MongoDB interaction for the TuneSense project.

---

## 📂 Refactor Summary

### `searchworker.py` split and simplification

* Removed unnecessary yt-dlp download steps (like tv client config, ios API, m3u8 info) to speed up YouTube search.
* Results now include:

  * `title`
  * `duration`
  * `thumbnails` (list of dicts with `url`)
  * `id`, `webpage_url`, `channel`, etc.
* Returns a list of clean dictionaries suitable for UI display.

---

## 🔄 UI Integration (downloader\_ui.py)

### Added Functionality

* Connects with `SearchWorker` to populate YouTube search results.
* Displays thumbnail images using `ThumbnailWorker` via `ThumbnailSignalEmitter` (asynchronous).
* On item click:

  * Extracts audio features using `get_audio_features()` (via yt-dlp + librosa).
  * Uses KNN model to return 3 similar songs (`get_recommendations()`).
  * Metadata fetched from MongoDB (`fetch_metadata()`).
  * Radar chart displayed using `RadarChartCanvas`.

---

## 🧠 Model Details

* Model stored locally as `models/tunesense_knn_model.joblib`.
* Trained using 10 audio features:

  * `mfcc_0`, `mfcc_1`, `mfcc_2`, `mfcc_3`
  * `chroma_0`, `chroma_1`
  * `tempo`, `centroid`, `rms`, `zcr`
* Accuracy:

  * Cosine @3: 0.742
  * Cosine + Weighted @5: 0.820

---

## 📊 Feature Extraction

### `get_audio_features(title)`

* Uses `yt_dlp` to search YouTube Music and extract the top match.
* Downloads `.wav`, extracts features with librosa.
* Returns dict used for KNN input and radar chart.

---

## 🔍 Recommendation Flow

1. Search with `SearchWorker` (no video download).
2. Results displayed in `QListWidget`.
3. When clicked:

   * `get_audio_features()` → downloads & extracts features.
   * `get_recommendations()` → KNN lookup.
   * `fetch_metadata()` → MongoDB retrieval.
   * UI updates recommendation list and radar chart.

---

## 🗄️ MongoDB Atlas

Using cluster:

```
mongodb+srv://supertrooper:UofT1234@musiccluster.ix1va8y.mongodb.net/?retryWrites=true&w=majority&appName=musiccluster
```

Collection: `tunesense.tracks`

---

## ✅ Outstanding Fixes Made

* Fixed ValueError on duration formatting (`int(duration)`).
* Addressed `None` from `get_audio_features()` by falling back to YouTube search.
* Added radar chart integration.
* Ensured recommendations displayed as soon as valid vectors returned.

---

## 📁 Files Involved

* `widgets/searchworker.py`  → Search YouTube
* `widgets/thumbnailthread.py` → Feature extraction, KNN, radar chart
* `widgets/downloader_ui.py` → Main PyQt interface
* `models/tunesense_knn_model.joblib` → Trained KNN model

---

