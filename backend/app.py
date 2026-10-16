from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

import os
import io
import pandas as pd
import numpy as np

from backend.analytics_core import (
    load_dataset_file,
    get_dataset_overview,
    detect_data_issues,
    perform_clean_dataset,
    get_comprehensive_statistics,
    calculate_healthcare_kpis,
    generate_15_healthcare_visualizations,
    apply_dataset_filters,
    get_detailed_disease_analysis,
    generate_smart_healthcare_insights,
    execute_patient_prediction,
    generate_pdf_healthcare_report,
    detect_and_map_columns,
    get_disease_breakdown
)


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)
CORS(app)


# ============================================================
# PATHS & DEFAULT DATA INITIALIZATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploaded_data"
)

RAW_FILE = os.path.join(
    UPLOAD_FOLDER,
    "uploaded_patient_data.csv"
)

CLEANED_FILE = os.path.join(
    UPLOAD_FOLDER,
    "cleaned_patient_data.csv"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Seed default dataset from dataset/patient_health_dataset.csv if present
DEFAULT_DATASET = os.path.join(os.path.dirname(BASE_DIR), "dataset", "patient_health_dataset.csv")
if not os.path.exists(RAW_FILE) and os.path.exists(DEFAULT_DATASET):
    try:
        import shutil
        shutil.copyfile(DEFAULT_DATASET, RAW_FILE)
    except Exception as e:
        print(f"Notice: Could not copy initial default dataset: {e}")


def get_active_dataframe(use_cleaned_if_available: bool = True) -> tuple[pd.DataFrame, bool]:
    """
    Returns (active_df, is_cleaned)
    """
    if use_cleaned_if_available and os.path.exists(CLEANED_FILE):
        return pd.read_csv(CLEANED_FILE), True
    elif os.path.exists(RAW_FILE):
        return pd.read_csv(RAW_FILE), False
    elif os.path.exists(DEFAULT_DATASET):
        return pd.read_csv(DEFAULT_DATASET), False
    return pd.DataFrame(), False


# ============================================================
# HOME / HEALTH CHECK
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "success",
        "message": "Patient Health Outcome Predictor - Power BI Healthcare Analytics API is running",
        "endpoints": [
            "/upload-csv",
            "/clean-data",
            "/analysis",
            "/predict",
            "/healthcare-analytics",
            "/disease-analysis",
            "/smart-insights",
            "/dataset-overview",
            "/detect-issues",
            "/download-cleaned",
            "/export-pdf"
        ]
    })


# ============================================================
# UPLOAD DATASET (CSV or Excel)
# ============================================================

@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file was uploaded."}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file was selected."}), 400

        allowed_extensions = (".csv", ".xlsx", ".xls")
        if not file.filename.lower().endswith(allowed_extensions):
            return jsonify({"error": "Only CSV or Excel (.xlsx, .xls) files are supported."}), 400

        df, err = load_dataset_file(file, file.filename)
        if err:
            return jsonify({"error": err}), 400

        # Save to RAW_FILE as CSV
        df.to_csv(RAW_FILE, index=False)

        # Clear previous cleaned file on new raw upload
        if os.path.exists(CLEANED_FILE):
            try:
                os.remove(CLEANED_FILE)
            except Exception:
                pass

        mapping = detect_and_map_columns(df)
        total_cells = df.shape[0] * df.shape[1]
        missing_total = int(df.isna().sum().sum())
        missing_pct = round((missing_total / total_cells * 100), 2) if total_cells > 0 else 0.0
        dup_count = int(df.duplicated().sum())

        return jsonify({
            "success": True,
            "message": f"Dataset '{file.filename}' uploaded successfully.",
            "filename": file.filename,
            "raw_patients": int(len(df)),
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_names": list(df.columns),
            "missing_total": missing_total,
            "missing_pct": missing_pct,
            "duplicate_rows": dup_count,
            "detected_mapping": mapping
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"Upload error: {str(e)}"}), 500


# ============================================================
# DATASET OVERVIEW & PREVIEW
# ============================================================

@app.route("/dataset-overview", methods=["GET"])
def dataset_overview():
    try:
        df, is_cleaned = get_active_dataframe(use_cleaned_if_available=False)
        if df.empty:
            return jsonify({"error": "No dataset found. Please upload a dataset first."}), 400

        overview = get_dataset_overview(df, filename="active_patient_data.csv")
        overview["is_cleaned"] = is_cleaned
        return jsonify(overview)
    except Exception as e:
        return jsonify({"error": f"Failed to get dataset overview: {str(e)}"}), 500


# ============================================================
# DETECT DATA ISSUES
# ============================================================

@app.route("/detect-issues", methods=["GET", "POST"])
def detect_issues():
    try:
        df, _ = get_active_dataframe(use_cleaned_if_available=False)
        if df.empty:
            return jsonify({"error": "No dataset found. Please upload a dataset first."}), 400

        issues = detect_data_issues(df)
        return jsonify({"success": True, "issues": issues})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
# CLEAN DATA
# ============================================================

@app.route("/clean-data", methods=["POST"])
def clean_data():
    try:
        if not os.path.exists(RAW_FILE):
            return jsonify({"error": "No uploaded dataset found. Please upload a dataset first."}), 400

        df_raw = pd.read_csv(RAW_FILE)
        raw_patients = len(df_raw)

        # Parse optional parameters from request JSON
        req_data = request.get_json(silent=True) or {}
        missing_strategy = req_data.get("missing_strategy", "mean")
        target_missing_cols = req_data.get("target_missing_cols", None)
        remove_duplicates = req_data.get("remove_duplicates", True)
        remove_outliers = req_data.get("remove_outliers", False)
        outlier_cols = req_data.get("outlier_cols", None)

        # Perform cleaning
        df_cleaned, report = perform_clean_dataset(
            df_raw,
            handle_missing=True,
            missing_strategy=missing_strategy,
            target_missing_cols=target_missing_cols,
            remove_duplicates=remove_duplicates,
            remove_outliers=remove_outliers,
            outlier_cols=outlier_cols,
            convert_numeric=True,
            remove_empty=True,
            handle_nhanes_codes=True
        )

        # Save cleaned file
        df_cleaned.to_csv(CLEANED_FILE, index=False)

        # Format backwards-compatible response for existing frontend
        response = {
            "success": True,
            "message": "Data cleaning completed successfully.",
            "raw_patients": int(raw_patients),
            "cleaned_patients": int(len(df_cleaned)),
            "rows_removed": int(raw_patients - len(df_cleaned)),
            "duplicate_rows": int(report.get("duplicate_rows_removed", 0)),
            "missing_values_before": int(report.get("missing_values_before", 0)),
            "missing_values_after": int(report.get("missing_values_after", 0)),
            "missing_patient_id": 0,
            "missing_age_rows": 0,
            "age_filtered_rows": 0,
            "empty_rows": int(report.get("empty_rows_removed", 0)),
            "empty_columns_removed": report.get("empty_cols_removed", []),
            "original_columns": list(df_raw.columns),
            "cleaned_columns": list(df_cleaned.columns),
            "operations": report.get("operations", []),
            "preview": df_cleaned.head(10).replace({np.nan: None}).to_dict(orient="records")
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"success": False, "error": f"Data cleaning error: {str(e)}"}), 500


# ============================================================
# RESET CLEANING
# ============================================================

@app.route("/reset-cleaning", methods=["POST"])
def reset_cleaning():
    try:
        if os.path.exists(CLEANED_FILE):
            os.remove(CLEANED_FILE)
        return jsonify({"success": True, "message": "Cleaned dataset reset. Using raw dataset."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
# DATA ANALYSIS
# ============================================================

@app.route("/analysis", methods=["GET"])
def analysis():
    try:
        df, is_cleaned = get_active_dataframe(use_cleaned_if_available=True)
        if df.empty:
            return jsonify({"error": "No dataset found. Please upload or clean a dataset first."}), 400

        mapping = detect_and_map_columns(df)
        total_patients = len(df)

        def _safe_mean(key):
            s = df[mapping[key]] if key in mapping and mapping[key] in df.columns else None
            return round(float(s.dropna().mean()), 2) if s is not None and not s.dropna().empty else 0.0

        disease_metrics = get_disease_breakdown(df, mapping)

        diabetes_cases = disease_metrics.get("diabetes", {}).get("positive")
        borderline_diabetes_cases = disease_metrics.get("diabetes", {}).get("borderline")
        heart_disease_cases = disease_metrics.get("heart_disease", {}).get("positive")
        hypertension_cases = disease_metrics.get("hypertension", {}).get("positive")
        smokers = disease_metrics.get("smoking", {}).get("positive")

        male_patients = 0
        female_patients = 0
        if "gender" in mapping and mapping["gender"] in df.columns:
            g_col = df[mapping["gender"]]
            if pd.api.types.is_numeric_dtype(g_col):
                male_patients = int((g_col == 1).sum())
                female_patients = int((g_col == 2).sum())
            else:
                lower_g = g_col.astype(str).str.lower()
                male_patients = int(lower_g.isin(["male", "m", "1"]).sum())
                female_patients = int(lower_g.isin(["female", "f", "2"]).sum())

        # Dynamic disease distribution for donut chart
        disease_distribution = []
        if disease_metrics.get("hypertension", {}).get("available"):
            disease_distribution.append({"name": "Hypertension", "value": disease_metrics["hypertension"]["positive"]})
        if disease_metrics.get("diabetes", {}).get("available"):
            disease_distribution.append({"name": "Diabetes", "value": disease_metrics["diabetes"]["positive"]})
        if disease_metrics.get("diabetes", {}).get("available") and disease_metrics["diabetes"].get("borderline", 0) > 0:
            disease_distribution.append({"name": "Pre-Diabetes (Borderline)", "value": disease_metrics["diabetes"]["borderline"]})
        if disease_metrics.get("heart_disease", {}).get("available"):
            disease_distribution.append({"name": "Heart Disease", "value": disease_metrics["heart_disease"]["positive"]})

        # Dynamic patient statistics for bar chart
        patient_statistics = []
        if disease_metrics.get("hypertension", {}).get("available"):
            patient_statistics.append({"name": "Hypertension", "cases": disease_metrics["hypertension"]["positive"]})
        if disease_metrics.get("diabetes", {}).get("available"):
            patient_statistics.append({"name": "Diabetes", "cases": disease_metrics["diabetes"]["positive"]})
        if disease_metrics.get("diabetes", {}).get("available") and disease_metrics["diabetes"].get("borderline", 0) > 0:
            patient_statistics.append({"name": "Pre-Diabetes", "cases": disease_metrics["diabetes"]["borderline"]})
        if disease_metrics.get("heart_disease", {}).get("available"):
            patient_statistics.append({"name": "Heart Disease", "cases": disease_metrics["heart_disease"]["positive"]})
        if disease_metrics.get("smoking", {}).get("available"):
            patient_statistics.append({"name": "Smokers", "cases": disease_metrics["smoking"]["positive"]})

        # Extended statistics
        full_stats = get_comprehensive_statistics(df)

        # Serializable disease breakdown
        serializable_breakdown = {
            k: {
                "name": v["name"],
                "available": v["available"],
                "positive": v["positive"],
                "negative": v["negative"],
                "borderline": v.get("borderline", 0),
                "missing": v["missing"],
                "prevalence_pct": v["prevalence_pct"],
                "status": v["status"],
                "display": v["display"]
            }
            for k, v in disease_metrics.items()
        }

        total_disease_cases = sum(
            d["positive"] for d in [disease_metrics.get("hypertension", {}), disease_metrics.get("diabetes", {}), disease_metrics.get("heart_disease", {})]
            if d.get("available") and d.get("positive") is not None
        )

        return jsonify({
            "success": True,
            "is_cleaned": is_cleaned,
            "total_patients": int(total_patients),
            "total_disease_cases": int(total_disease_cases),
            "average_age": _safe_mean("age"),
            "average_bmi": _safe_mean("bmi"),
            "average_glucose": _safe_mean("glucose"),
            "average_hba1c": _safe_mean("hba1c"),
            "average_cholesterol": _safe_mean("cholesterol"),
            "diabetes_cases": diabetes_cases,
            "borderline_diabetes_cases": borderline_diabetes_cases,
            "heart_disease_cases": heart_disease_cases,
            "hypertension_cases": hypertension_cases,
            "smokers": smokers,
            "male_patients": male_patients,
            "female_patients": female_patients,
            "disease_distribution": disease_distribution,
            "patient_statistics": patient_statistics,
            "disease_breakdown": serializable_breakdown,
            "numeric_columns": full_stats.get("numeric_columns", []),
            "categorical_columns": full_stats.get("categorical_columns", []),
            "numeric_stats": full_stats.get("numeric_stats", {}),
            "correlation_matrix": full_stats.get("correlation_matrix", {})
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"Analysis error: {str(e)}"}), 500


# ============================================================
# HEALTHCARE ANALYTICS (KPIs & 15 Visualizations)
# ============================================================

@app.route("/healthcare-analytics", methods=["GET", "POST"])
def healthcare_analytics():
    try:
        df, _ = get_active_dataframe(use_cleaned_if_available=True)
        if df.empty:
            return jsonify({"error": "No dataset found."}), 400

        mapping = detect_and_map_columns(df)

        # Check for filter query parameters or JSON body
        age_group = request.args.get("age_group", "All")
        gender_filter = request.args.get("gender", "All")
        disease_filter = request.args.get("disease", "All")
        risk_filter = request.args.get("risk", "All")

        filtered_df = apply_dataset_filters(
            df,
            age_group=age_group,
            gender_filter=gender_filter,
            disease_filter=disease_filter,
            risk_filter=risk_filter,
            mapping=mapping
        )

        kpis = calculate_healthcare_kpis(filtered_df, mapping)
        vis_bundle = generate_15_healthcare_visualizations(filtered_df, mapping)

        return jsonify({
            "success": True,
            "kpis": kpis,
            "chart_data": vis_bundle.get("chart_data", {}),
            "active_filters": {
                "age_group": age_group,
                "gender": gender_filter,
                "disease": disease_filter,
                "risk": risk_filter
            },
            "total_unfiltered_patients": len(df),
            "total_filtered_patients": len(filtered_df)
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"Healthcare analytics error: {str(e)}"}), 500


# ============================================================
# DISEASE ANALYSIS
# ============================================================

@app.route("/disease-analysis", methods=["GET"])
def disease_analysis():
    try:
        df, _ = get_active_dataframe(use_cleaned_if_available=True)
        if df.empty:
            return jsonify({"error": "No dataset found."}), 400

        mapping = detect_and_map_columns(df)
        analysis_data = get_detailed_disease_analysis(df, mapping)
        return jsonify({"success": True, "data": analysis_data})
    except Exception as e:
        return jsonify({"success": False, "error": f"Disease analysis error: {str(e)}"}), 500


# ============================================================
# SMART HEALTHCARE INSIGHTS (AI)
# ============================================================

@app.route("/smart-insights", methods=["GET"])
def smart_insights():
    try:
        df, _ = get_active_dataframe(use_cleaned_if_available=True)
        if df.empty:
            return jsonify({"error": "No dataset found."}), 400

        mapping = detect_and_map_columns(df)
        insights = generate_smart_healthcare_insights(df, mapping)
        return jsonify({"success": True, "insights": insights})
    except Exception as e:
        return jsonify({"success": False, "error": f"Insights error: {str(e)}"}), 500


# ============================================================
# PATIENT PREDICTION (RANDOM FOREST ML)
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided."}), 400

        result = execute_patient_prediction(data)
        if not result.get("success", False):
            return jsonify(result), 400

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Prediction server error: {str(e)}"}), 500


# ============================================================
# DOWNLOAD CLEANED DATASET
# ============================================================

@app.route("/download-cleaned", methods=["GET"])
def download_cleaned():
    try:
        file_to_send = CLEANED_FILE if os.path.exists(CLEANED_FILE) else RAW_FILE
        if not os.path.exists(file_to_send):
            return jsonify({"error": "No dataset available for download."}), 404

        return send_file(
            file_to_send,
            mimetype="text/csv",
            as_attachment=True,
            download_name="cleaned_patient_data.csv"
        )
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500


# ============================================================
# EXPORT PDF REPORT
# ============================================================

@app.route("/export-pdf", methods=["GET"])
def export_pdf():
    try:
        df, _ = get_active_dataframe(use_cleaned_if_available=True)
        if df.empty:
            return jsonify({"error": "No dataset available to generate report."}), 400

        mapping = detect_and_map_columns(df)
        pdf_bytes = generate_pdf_healthcare_report(df, mapping)

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="Healthcare_Intelligence_Report.pdf"
        )
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


# ============================================================
# RUN FLASK
# ============================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )