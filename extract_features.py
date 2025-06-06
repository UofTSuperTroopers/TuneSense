from pathlib import Path
import librosa
import numpy as np
import pandas as pd
from tqdm import tqdm
import os

# Use pathlib for all paths
AUDIO_DIR = Path("data") / "fma small" / "fma_small_root" / "fma_small"
OUTPUT_FILE = Path("outputs/merged_features.csv")

def extract_features(filepath):
    try:
        y, sr = librosa.load(str(filepath), sr=22050, mono=True, duration=30)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        spec_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

        return {
            "mfcc": mfcc.mean(axis=1).tolist(),
            "chroma": chroma.mean(axis=1).tolist(),
            "spec_contrast": spec_contrast.mean(axis=1).tolist(),
            "tempo": tempo
        }
    except Exception as e:
        print(f"❌ Error with {filepath.name}: {e}")
        return None

def process_audio_files(limit=50):
    all_features = []
    count = 0

    for mp3_file in AUDIO_DIR.rglob("*.mp3"):
        print(f"🔍 Processing: {mp3_file.name}")
        features = extract_features(mp3_file)
        if features:
            features["filename"] = mp3_file.name
            all_features.append(features)
            count += 1
            if count >= limit:
                break

    return pd.DataFrame(all_features)

if __name__ == "__main__":
    df = process_audio_files(limit=50)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Saved features for {len(df)} tracks to {OUTPUT_FILE}")
