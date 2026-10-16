import os
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

import joblib


# -----------------------------
# Generate demo patient data
# -----------------------------

np.random.seed(42)

N = 2000

data = pd.DataFrame({
    "age": np.random.randint(18, 90, N),

    "gender": np.random.randint(0, 2, N),

    "systolic_bp": np.random.randint(90, 190, N),

    "heart_rate": np.random.randint(50, 140, N),

    "glucose": np.random.randint(60, 250, N),

    "bmi": np.round(
        np.random.uniform(16, 42, N),
        1
    ),

    "oxygen_saturation": np.round(
        np.random.uniform(88, 100, N),
        1
    ),

    "temperature": np.round(
        np.random.uniform(36, 40, N),
        1
    ),

    "previous_conditions": np.random.randint(
        0, 6, N
    ),

    "smoking": np.random.randint(
        0, 2, N
    ),

    "hospital_visits": np.random.randint(
        0, 10, N
    )
})


# -----------------------------
# Create demo risk score
# -----------------------------

score = (
    data["age"] * 0.15
    + np.maximum(
        data["systolic_bp"] - 120,
        0
    ) * 0.30
    + np.maximum(
        data["glucose"] - 100,
        0
    ) * 0.20
    + np.maximum(
        data["bmi"] - 25,
        0
    ) * 1.2
    + np.maximum(
        95 - data["oxygen_saturation"],
        0
    ) * 5
    + np.maximum(
        data["heart_rate"] - 100,
        0
    ) * 0.25
    + data["previous_conditions"] * 6
    + data["smoking"] * 5
    + data["hospital_visits"] * 2
)


# -----------------------------
# Create target
# -----------------------------

data["risk"] = pd.cut(
    score,
    bins=[-np.inf, 35, 65, np.inf],
    labels=[0, 1, 2]
).astype(int)


# -----------------------------
# Features
# -----------------------------

features = [
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

X = data[features]

y = data["risk"]


# -----------------------------
# Train/test
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# -----------------------------
# Random Forest
# -----------------------------

model = RandomForestClassifier(
    n_estimators=150,
    random_state=42
)

model.fit(
    X_train,
    y_train
)


# -----------------------------
# Accuracy
# -----------------------------

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)

print(
    f"Model Accuracy: {accuracy * 100:.2f}%"
)


# -----------------------------
# Save model
# -----------------------------

os.makedirs(
    "model",
    exist_ok=True
)

joblib.dump(
    model,
    "model/health_model.pkl"
)

print(
    "Model saved to model/health_model.pkl"
)