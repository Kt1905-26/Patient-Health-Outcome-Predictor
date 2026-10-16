from flask import Flask, request, jsonify
from flask_cors import CORS

import os
import pandas as pd

from backend.model import predict_health_risk
from backend.dashboard.analytics import get_dashboard_data


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

# Allow React frontend to communicate with Flask
CORS(app)


# ============================================================
# HOME / HEALTH CHECK
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "Patient Health Outcome Prediction Flask API is running"
    })


# ============================================================
# CSV UPLOAD
# ============================================================

@app.route("/upload-csv", methods=["POST"])
def upload_csv():

    # Check whether a file was sent
    if "file" not in request.files:

        return jsonify({
            "error": "No CSV file was uploaded."
        }), 400

    file = request.files["file"]

    # Check filename
    if file.filename == "":

        return jsonify({
            "error": "No file selected."
        }), 400

    # Check CSV extension
    if not file.filename.lower().endswith(".csv"):

        return jsonify({
            "error": "Only CSV files are allowed."
        }), 400

    try:

        # ----------------------------------------------------
        # Create upload folder
        # ----------------------------------------------------

        upload_folder = os.path.join(
            os.path.dirname(__file__),
            "uploaded_data"
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        # ----------------------------------------------------
        # Save uploaded CSV
        # ----------------------------------------------------

        file_path = os.path.join(
            upload_folder,
            "uploaded_patient_data.csv"
        )

        file.save(file_path)

        # ----------------------------------------------------
        # Read CSV
        # ----------------------------------------------------

        df = pd.read_csv(file_path)

        # ----------------------------------------------------
        # Validate CSV
        # ----------------------------------------------------

        if df.empty:

            return jsonify({
                "error": "The uploaded CSV is empty."
            }), 400

        # ----------------------------------------------------
        # Return information to React
        # ----------------------------------------------------

        return jsonify({

            "message": "CSV uploaded and analyzed successfully.",

            "filename": file.filename,

            "rows": len(df),

            "columns": len(df.columns),

            "column_names": list(df.columns)

        })

    except Exception as e:

        return jsonify({
            "error": f"Could not process CSV: {str(e)}"
        }), 500


# ============================================================
# PATIENT HEALTH PREDICTION
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json()

        result = predict_health_risk(data)

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard", methods=["GET"])
def dashboard():

    try:

        result = get_dashboard_data()

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# START FLASK SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )