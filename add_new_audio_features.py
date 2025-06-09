import pandas as pd
import numpy as np
import librosa
from pathlib import Path
from tqdm import tqdm

# Load the original flattened features
df = pd.read_csv("outputs/flattened_features.csv")

# Setup audio directory
AUDIO_DIR = Path("data/fma_large/fma_large_root/fma_large")

# Prepare new columns
df['centroid'] = np.nan
df['rms'] = np.nan
df['zcr'] = np.nan

for i, row in tqdm(df.iterrows(), total=len(df)):
    track_id = row['track_id']
    filename = row['filename']
    subfolder = f"{int(track_id):06d}"[:3]
    filepath = AUDIO_DIR / subfolder / filename
    if not filepath.exists():
        continue
    try:
        y, sr = librosa.load(filepath, sr=22050, mono=True, duration=30)
        df.at[i, 'centroid'] = librosa.feature.spectral_centroid(y=y, sr=sr).mean()
        df.at[i, 'rms'] = librosa.feature.rms(y=y).mean()
        df.at[i, 'zcr'] = librosa.feature.zero_crossing_rate(y=y).mean()
    except Exception as e:
        print(f"❌ {filename}: {e}")

# Save updated CSV
df.to_csv("outputs/flattened_features_with_extras.csv", index=False)
print("✅ New features added and file saved.")
