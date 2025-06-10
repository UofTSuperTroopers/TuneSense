
import joblib
import pandas as pd
import plotly.graph_objects as go
from sklearn.neighbors import NearestNeighbors

# Load model
model_bundle = joblib.load("models/tunesense_knn_model_FIXED.joblib")
knn = model_bundle['model']
feature_names = model_bundle['feature_names']
metadata = model_bundle['metadata']

# Load your feature data
df = pd.read_csv("outputs/final_merged_with_extras.csv")

# Select only numeric features used during training
X = df[feature_names].copy()

# Predict recommendations for the first track
input_index = 0
input_vector = X.iloc[[input_index]]
distances, indices = knn.kneighbors(input_vector)

# Get the top recommendation (excluding the track itself)
recommended_index = indices[0][1]
radar_features = ['danceability', 'energy', 'valence', 'rms', 'zcr', 'centroid']
input_track = df.iloc[input_index]
recommended_track = df.iloc[recommended_index]

input_vals = [input_track.get(f, 0) for f in radar_features]
rec_vals = [recommended_track.get(f, 0) for f in radar_features]

# Plot radar chart
fig = go.Figure()
fig.add_trace(go.Scatterpolar(r=input_vals, theta=radar_features, fill='toself', name='Selected Song'))
fig.add_trace(go.Scatterpolar(r=rec_vals, theta=radar_features, fill='toself', name='Recommended Song'))
fig.update_layout(title='🎵 Feature Comparison: Selected vs Recommended', polar=dict(radialaxis=dict(visible=True)))
fig.show()
