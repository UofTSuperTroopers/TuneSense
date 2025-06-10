
from PyQt6.QtCore import QThread, pyqtSignal
import pandas as pd
import joblib

class RecommendationWorker(QThread):
    recommendations_ready = pyqtSignal(list)

    def __init__(self, input_row):
        super().__init__()
        self.input_row = input_row  # expects a dict-like row of features

    def run(self):
        try:
            # Load model bundle
            bundle = joblib.load('widgets/tunesense_knn_model_FIXED.joblib')

            model = bundle["model"]
            feature_names = bundle["feature_names"]
            metadata = bundle["metadata"]

            t, art_name = metadata['title'], metadata['artist_name']
            print(f'[LOGGER] t = {t}, art_name = {art_name}')

            
            # Clean the input row
            row = self.input_row.copy()
            for feat in feature_names:
                val = row.get(feat, 0)
                if isinstance(val, str) and val.startswith("[") and val.endswith("]"):
                    try:
                        row[feat] = float(val.strip("[]"))
                    except ValueError:
                        row[feat] = 0.0

            # Prepare input for prediction
# Ensure all expected features are present
            input_values = []
            for f in feature_names:
                val = row.get(f, 0)  # fallback to 0 if missing
                input_values.append(val)

            X_input = pd.DataFrame([input_values], columns=feature_names).astype(float)

            # Get neighbors
            distances, indices = model.kneighbors(X_input)
            recommended_rows = metadata.iloc[indices[0]].to_dict("records")
            print(f'[LOGGER]: recommended_rows = {recommended_rows}')
            self.recommendations_ready.emit(recommended_rows)

        except Exception as e:
            print(f"❌ RecommendationWorker error: {e}")
            self.recommendations_ready.emit([])
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
import joblib

def print_model_metrics():
    # Load model bundle and data
    bundle = joblib.load(r"widgets/tunesense_knn_model_FIXED.joblib")
    model = bundle["model"]
    feature_names = bundle["feature_names"]
    
    df = pd.read_csv("final_merged_with_extras.csv")

    # Clean tempo if it's stringified
    if "tempo" in df.columns and df["tempo"].dtype == object:
        df["tempo"] = df["tempo"].apply(lambda x: float(x.strip("[]")) if isinstance(x, str) and x.startswith("[") else x)

    # Select X and mock labels y for demo (e.g. real valence, energy, danceability if they exist)
    X = df[feature_names].copy().fillna(0)
    
    # Since it's a KNN recommender, we’ll measure **reconstruction MSE**
    distances, indices = model.kneighbors(X)
    reconstructed = X.iloc[indices[:, 1:]].mean(axis=1)
    
    mse = mean_squared_error(X.mean(axis=1), reconstructed)
    r2 = r2_score(X.mean(axis=1), reconstructed)
    
    print("📊 KNN Reconstruction Metrics")
    print(f"🧠 Mean Squared Error (MSE): {mse:.4f}")
    print(f"🎯 R² Score: {r2:.4f}")
