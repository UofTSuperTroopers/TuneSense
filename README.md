<h1 align="center"> <img src="Images/TuneSenseIcon.png" width="45" style="vertical-align: middle; margin-right: 10px;"> TuneSense: Content-Based Music Recommendation System <img src="Images/TuneSenseIcon.png" width="45" style="vertical-align: middle; margin-right: 10px;">

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white" /> <!-- Python -->
  <img src="https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white" /> <!-- Pandas -->
  <img src="https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white" /> <!-- Numpy -->
  <img src="https://img.shields.io/badge/scikit--learn-ML-orange?style=for-the-badge&logo=scikit-learn&logoColor=white" /> <!-- Scikit -->
  <img src="https://img.shields.io/badge/Librosa-Audio_Features-yellowgreen?style=for-the-badge" /> <!-- Librosa -->
  <img src="https://img.shields.io/badge/MongoDB-Atlas-green?style=for-the-badge&logo=mongodb&logoColor=white" /> <!-- MongoDB -->
  <img src="https://img.shields.io/badge/PyMongo-Connector-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white" /> <!-- PyMongo -->
  <img src="https://img.shields.io/badge/Colab-Google_Notebooks-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=black" /> <!-- Google Colab -->
  <img src="https://img.shields.io/badge/TQDM-Progress_Bars-blueviolet?style=for-the-badge" /> <!-- TQDM -->
  <img src="https://img.shields.io/badge/YouTube_Music-FF0000?style=for-the-badge&logo=youtube-music&logoColor=white" /> <!-- YouTube Music -->
  <img src="https://img.shields.io/badge/PyQt-UI_Toolkit-41CD52?style=for-the-badge&logo=qt&logoColor=white" /> <!-- PyQT -->
</p>

## Table of Contents
<!-- TOC -->
1.  [ Project Overview](#project-overview)
2.  [ How to Run](#how-to-run)
3.  [ Key Features](#key-features)
4. [ Models & Techniques](#models--techniques)
5.  [ Performance Summary](#performance-summary)
6.  [ Data Pipeline](#data-pipeline)
7.  [ Features Extracted](#features-extracted)
8.  [ Tools & Libraries](#tools--libraries)
9.  [ Planned Front-End (Sketch)](#planned-front-end-sketch)
10.  [ Notes](#notes)
11.  [ Code Version Log](#code-version-log)
12.  [ Recommendations](#recommendations)
13.  [ Main Contributors](#main-contributors)
14.  [ License](#license)
15. [ Citations](#citations)

<!-- /TOC -->


## 📖 Project Overview

TuneSense is a machine learning-based song recommendation engine that suggests similar songs based on audio content. By analyzing features such as timbre, tempo, rhythm, and spectral properties, it offers intelligent content-based recommendations using FMA and Librosa, KNN model, MongoDB backend, and a PyQT frontend with YouTube Integration

---


### Option 1: Run as script:
```shell
# 1. clone repo
$ git clone https://github.com/UofTSuperTroopers/TuneSense.git 

# 2. run as script
$ python main.py
```
### 

---
## 🎯 Key Features

* 🎧 Song search + feature extraction
* 🔍 Top-3 recommendations using KNN
* 📊 Radar chart visualization
* 📺 Embedded YouTube search thumbnails
* ☁️ MongoDB for data persistence

---

## 🧪 Models & Techniques

* **K-Nearest Neighbors (KNN)** using `scikit-learn`
* Distance metrics: `cosine`, `euclidean`
* **Inverse Distance Weighting** as optional enhancement
* Genre match accuracy evaluation
* Support for playlist-aware centroid-based filtering

---

## 📈 Performance Summary

| Configuration | Top-K | Weighted | Distance Metric | Accuracy |
| ------------- | ----- | -------- | --------------- | -------- |
| Cosine        | 3     | No       | Cosine          | 0.735    |
| Cosine        | 3     | Yes      | Cosine          | 0.742    |
| Euclidean     | 3     | No       | Euclidean       | 0.730    |
| Euclidean     | 3     | Yes      | Euclidean       | \~0.728  |
| Cosine        | 5     | Yes      | Cosine          | 0.820    |

---

## 🧱 Data Pipeline

* **Dataset**: [FMA (Free Music Archive) — `fma_large`](https://github.com/mdeff/fma)
  * 📦 [Direct `.tar` download (93GB)](https://os.unil.cloud.switch.ch/fma/fma_large.tar.bz2) — *Only recommended if you need full access to raw audio files.*
* **Size**: ~106,000 total tracks in `fma_large`; ~5,000 used in this project after filtering and cleaning
* **Features Extracted**:

  * MFCC (Mel-frequency cepstral coefficients)
  * Chroma
  * Spectral contrast
  * Tempo
  * Centroid
  * RMS (Root Mean Square Energy)
  * Zero Crossing Rate (ZCR)
* **Storage**: MongoDB Atlas
* **Access**: Queried via `pymongo` from Colab

---
## 🔍 Features Extracted

| Feature               | Description                                                                                   | Typical Range                  |
|-----------------------|-----------------------------------------------------------------------------------------------|--------------------------------|
| **MFCC**              | Captures timbral texture (human perception of sound)                                          | ~ –500 to +200 (per coefficient) |
| **Chroma**            | Pitch class presence (C, C#, ..., B)                                                          | 0 to 1                         |
| **Spectral Contrast** | Difference between spectral peaks and valleys                                                 | ~10 to 50                      |
| **Tempo**             | Estimated beats per minute (BPM)                                                              | 30 to 240                      |
| **Spectral Centroid** | “Brightness” of a sound (weighted mean of frequencies)                                        | ~1,000 to 6,000 Hz             |
| **RMS Energy**        | Average power/loudness of audio                                                               | 0.0 to ~0.3 (for normalized audio) |
| **Zero Crossing Rate (ZCR)** | Frequency of waveform sign changes — useful for percussive sounds                        | 0.01 to 0.2                    |

---

## ⚙️ Tools & Libraries

* `pandas` – Powerful data manipulation and analysis library. Used to load, clean, and transform tabular data (e.g., CSVs and MongoDB query results).
* `numpy` – Core numerical computing package. Supports vectorized math and efficient processing of audio features.
* `scikit-learn` – Machine learning toolkit for modeling and evaluation. Used for KNN implementation, accuracy scoring, and feature scaling.
* `scipy` – Scientific computing library. Used for distance calculations and optional modeling utilities.
* `tqdm` – Progress bar utility. Provides visual feedback during long-running tasks like batch evaluation.
* `librosa` – Audio signal analysis library. Extracts MFCCs, chroma, spectral contrast, tempo, and more from .mp3 files.
* `pymongo` – MongoDB driver for Python. Interfaces with MongoDB Atlas to store and retrieve track data in real time.
* `MongoDB` Atlas – Cloud-based NoSQL database. Used to store the final preprocessed dataset and enable dynamic access from Colab.
* `MongoDB` Compass – GUI for MongoDB. Helps validate JSON imports and verify the structure of stored audio data.
* `Google` Colab – Cloud-hosted notebook platform. Used for collaborative model development, experimentation, and reproducibility.
* `PyQT` - A Python binding for the Qt GUI framework, used to build cross-platform desktop interfaces. Enables interactive dashboards, widgets, and media controls for TuneSense's future visual front-end.
* `YouTube Music (API/Conceptual Reference)` – Used as a conceptual reference point for audio similarity, playlist behavior, and user-centered design. While no direct API was used, the interface and recommendation logic inspired parts of the TuneSense UX.






## 📌 Notes

* MongoDB Atlas used as the main data source
* All model evaluations performed live in Colab
* Cosine distance with weighted KNN + Top-5 performed best
* Radar chart front-end to be developed in a future release

---

## 🧾 Code Version Log
* Content-based KNN recommender implemented
* Playlist-aware fallback added
* Accuracy@3 via genre match as proxy for relevance
* Tempo parsing bug fixed with `safe_parse_tempo()`
* Evaluation baseline (cosine distance): 0.735 accuracy
* Switched to Euclidean distance option (toggle with `metric` arg)
* Added 3 new audio features: centroid, RMS, zero-crossing rate (ZCR)
* Updated feature_cols to include the new features
* Using `final_merged_with_extras.csv` for updated feature set
* Latest cosine evaluation with extra features (15 neighbors): 0.742 accuracy (↑ from 0.735)
* Top-5 genre match accuracy using cosine (unweighted): 0.820
* Added optional weighted KNN recommendation support via inverse distance
* Example usage now defaults to cosine with weighted=True
---
## 💡 Recommendations
* Incorporate Collaborative Filtering - 
Enhance the system by blending content-based recommendations with user behavior data to improve personalization and diversity.

* Integrate YouTube or Last.fm APIs - 
Fetch real-time user preferences, listening history, or mood tags to make the recommender more dynamic and context-aware.

* Add Genre or Mood Clustering - 
Use clustering algorithms (e.g. K-Means, DBSCAN) to group songs by mood or style and support exploratory listening.

* Optimize with Dimensionality Reduction - 
Apply PCA or t-SNE to reduce feature dimensionality for faster model inference and better visualization.

---

## Main Contributors:

* [Gwen Seymour](https://github.com/Gwen1987) 
* [Peter Lin](https://github.com/bluejays101)
* [Rob Ranieri](https://github.com/ConstCorrectness) 

---
### 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


---
## 📚 Citations

#### *We gratefully acknowledge the use of the Free Music Archive (FMA) dataset:*

@inproceedings{fma_dataset,
  title = {{FMA}: A Dataset for Music Analysis},
  author = {Defferrard, Micha\"el and Benzi, Kirell and Vandergheynst, Pierre and Bresson, Xavier},
  booktitle = {18th International Society for Music Information Retrieval Conference (ISMIR)},
  year = {2017},
  archiveprefix = {arXiv},
  eprint = {1612.01840},
  url = {https://arxiv.org/abs/1612.01840},
}

@inproceedings{fma_challenge,
  title = {Learning to Recognize Musical Genre from Audio},
  subtitle = {Challenge Overview},
  author = {Defferrard, Micha\"el and Mohanty, Sharada P. and Carroll, Sean F. and Salath\'e, Marcel},
  booktitle = {The 2018 Web Conference Companion},
  year = {2018},
  publisher = {ACM Press},
  isbn = {9781450356404},
  doi = {10.1145/3184558.3192310},
  archiveprefix = {arXiv},
  eprint = {1803.05337},
  url = {https://arxiv.org/abs/1803.05337},
}
#### *We gratefully acknowledge the use of Librosa to analyze our music samples:*

<a class="reference external image-reference" href="https://zenodo.org/badge/latestdoi/6309729"><img alt="https://zenodo.org/badge/6309729.svg" src="https://zenodo.org/badge/6309729.svg"></a>

<aside class="footnote brackets" id="id2" role="doc-footnote">
<span class="label"><span class="fn-bracket">[</span><a role="doc-backlink" href="#id1">1</a><span class="fn-bracket">]</span></span>
<p>McFee, Brian, Colin Raffel, Dawen Liang, Daniel PW Ellis, Matt McVicar, Eric Battenberg, and Oriol Nieto.
“librosa: Audio and music signal analysis in python.”
In Proceedings of the 14th python in science conference, pp. 18-25. 2015.</p>
</aside>



**TuneSense** is a final data science capstone project developed as part of the University of Toronto SCS Data Analytics Certificate.

