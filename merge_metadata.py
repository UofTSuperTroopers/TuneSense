from pathlib import Path
import pandas as pd

# === File Paths ===
FEATURES_FILE = Path("outputs/features_sample.csv")  # ⬅️ Your features file
TRACKS_CSV = Path("data/fma_metadata/tracks.csv")    # ⬅️ Adjust path if needed
OUTPUT_FILE = Path("outputs/merged_features.csv")

def load_and_merge():
    # Load extracted features from CSV
    features_df = pd.read_csv(FEATURES_FILE)
    features_df["track_id"] = features_df["filename"].str.replace(".mp3", "", regex=False)

    # Load metadata, skipping first 2 rows (header is on line 3)
    metadata = pd.read_csv(TRACKS_CSV, skiprows=2, low_memory=False)

    print("🧠 Metadata columns:")
    print(metadata.columns.tolist())  # See what columns are re
