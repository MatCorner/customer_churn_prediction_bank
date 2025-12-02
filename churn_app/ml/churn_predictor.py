import joblib
import numpy as np

MODEL_PATH = "churnapp/ml/model.pkl"

model = joblib.load(MODEL_PATH)

def predict_churn(features: dict):
    X = np.array([[ 
        features["age"],
        features["balance"],
        features["tenure"],
        features["num_transactions"],
    ]])
    prob = model.predict_proba(X)[0][1]
    return float(prob)
