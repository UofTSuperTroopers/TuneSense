from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
import pandas as pd
import joblib
from sklearn.metrics import mean_squared_error

df = pd.read_csv("features_with_heuristics.csv")

y = df[['danceability', 'energy', 'valence']]
X = df.drop(columns=['filename', 'danceability', 'energy', 'valence'])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# MultiOutputRegressor Model
base_model = RandomForestRegressor()
multi_model = MultiOutputRegressor(base_model)
multi_model.fit(X_train, y_train)

print("Training features:", X.columns.tolist())
print("Inference features:", y.columns.tolist())

joblib.dump(multi_model, "multi_audio_model.pkl")

y_pred = multi_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred, multioutput='raw_values')
print("MSE per target:", dict(zip(y.columns, mse)))

