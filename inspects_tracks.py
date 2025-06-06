import pandas as pd

# Update this path if needed
TRACKS_CSV = "data/fma small/fma_small_root/fma_metadata/tracks.csv"

# Load CSV safely
metadata = pd.read_csv(TRACKS_CSV, low_memory=False)

# Show all columns
print("🧠 Metadata columns:")
print(metadata.columns.tolist())
