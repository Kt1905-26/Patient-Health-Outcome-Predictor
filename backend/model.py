import joblib
import os


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "model",
    "health_model.pkl"
)


model = joblib.load(MODEL_PATH)


FEATURES = [
    "age",
    "gender",
    "systolic_bp",
    "heart_rate",
    "glucose",
    "bmi",
    "oxygen_saturation",
    "temperature",
    "previous_conditions",
    "smoking",
    "hospital_visits"
]


import pandas as pd


def predict_health_risk(data):

    df_input = pd.DataFrame([{
        feature: data[feature]
        for feature in FEATURES
    }])

    prediction = model.predict(df_input)[0]

    probabilities = model.predict_proba(df_input)[0]

    labels = {
        0: "Low Risk",
        1: "Moderate Risk",
        2: "High Risk"
    }

    return {
        "risk": labels[int(prediction)],
        "confidence": round(
            float(max(probabilities)) * 100,
            2
        )
    }