from pathlib import Path
import pandas as pd

# File paths
TRACKS_FILE = Path("outputs") / "cleaned_tracks_metadata.csv"
FEATURES_FILE = Path("outputs") / "flattened_features.csv"
OUTPUT_FILE = Path("outputs") / "final_merged.csv"

def pick_column(df, keyword):
    """Pick the first column name containing a keyword."""
    return next((col for col in df.columns if keyword in col), None)

def load_and_merge():
    # Load metadata CSV with 3-level header
    print(f"📂 Loading metadata from {TRACKS_FILE}")
    metadata_df = pd.read_csv(TRACKS_FILE, header=[0, 1, 2], index_col=0, low_memory=False)

    # Flatten multi-index column names
    metadata_df.columns = ['_'.join([str(x) for x in col if x]) for col in metadata_df.columns]

    # Rename index and reset so track_id becomes a column
    metadata_df.index.name = "track_id"
    metadata_df = metadata_df.reset_index()

    # Convert track_id to int
    metadata_df["track_id"] = pd.to_numeric(metadata_df["track_id"], errors="coerce")
    metadata_df = metadata_df.dropna(subset=["track_id"])
    metadata_df["track_id"] = metadata_df["track_id"].astype(int)

    # Fuzzy match key columns
    title_col = pick_column(metadata_df, "track_title")
    artist_col = pick_column(metadata_df, "artist_name")
    genre_col = pick_column(metadata_df, "track_genre_top")

    if not all([title_col, artist_col, genre_col]):
        print("❌ Failed to find required metadata columns.")
        print("Available columns:", metadata_df.columns.tolist())
        return None

    # Select and rename
    metadata_df = metadata_df[["track_id", title_col, artist_col, genre_col]]
    metadata_df.columns = ["track_id", "title", "artist_name", "genre_top"]

    # Load features
    print(f"📂 Loading features from {FEATURES_FILE}")
    features_df = pd.read_csv(FEATURES_FILE)

    # Convert track_id to int
    features_df["track_id"] = pd.to_numeric(features_df["track_id"], errors="coerce")
    features_df = features_df.dropna(subset=["track_id"])
    features_df["track_id"] = features_df["track_id"].astype(int)

    # Merge
    print("🔗 Merging features with metadata...")
    merged = pd.merge(features_df, metadata_df, on="track_id", how="left")

    print("✅ Merge complete. Final DataFrame shape:", merged.shape)
    return merged

if __name__ == "__main__":
    df = load_and_merge()
    if df is not None:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"✅ Saved merged dataset with metadata to {OUTPUT_FILE}")
