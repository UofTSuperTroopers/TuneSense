from pathlib import Path
import pandas as pd

# Define file paths
DATA_DIR = Path("data/fma_large/fma_large_root/fma_metadata")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TRACKS_CSV = DATA_DIR / "tracks.csv"
CLEANED_CSV = OUTPUT_DIR / "cleaned_tracks_metadata.csv"

def clean_metadata():
    # Read multi-level header
    metadata = pd.read_csv(TRACKS_CSV, header=[0, 1], index_col=0, low_memory=False)

    # Flatten the multi-index columns (e.g., track_title, artist_name)
    metadata.columns = ['_'.join(col).strip() for col in metadata.columns.values]
    metadata.reset_index(inplace=True)  # bring track_id into a column

    # Select the relevant metadata columns
    keep_cols = ["track_id", "track_title", "artist_name", "track_genre_top"]
    cleaned = metadata[keep_cols].copy()
    #cleaned['track_id'] = cleaned['track_id'].astype(float)  # Ensure track_id is float


    
    # Save to CSV
    cleaned.to_csv(CLEANED_CSV, index=False)
    print(f"✅ Cleaned metadata saved to {CLEANED_CSV}")
    print(cleaned.dtypes)

if __name__ == "__main__":
    clean_metadata()
