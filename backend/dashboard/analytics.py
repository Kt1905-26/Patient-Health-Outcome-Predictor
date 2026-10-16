import os
import sys
import pandas as pd

# Ensure backend root is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(backend_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from backend.analytics_core import get_disease_breakdown, detect_and_map_columns
except ImportError:
    from analytics_core import get_disease_breakdown, detect_and_map_columns


# ============================================================
# GET UPLOADED DATASET PATH
# ============================================================

def get_dataset_path():
    # 1. Check backend/uploaded_data/uploaded_patient_data.csv
    p1 = os.path.join(backend_dir, "uploaded_data", "uploaded_patient_data.csv")
    if os.path.exists(p1):
        return p1

    # 2. Check backend/dashboard/uploaded_data/uploaded_patient_data.csv
    p2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploaded_data", "uploaded_patient_data.csv")
    if os.path.exists(p2):
        return p2

    # 3. Check cleaned dataset
    p_clean = os.path.join(backend_dir, "uploaded_data", "cleaned_patient_data.csv")
    if os.path.exists(p_clean):
        return p_clean

    # 4. Fallback to default patient health dataset
    p_default = os.path.join(root_dir, "dataset", "patient_health_dataset.csv")
    if os.path.exists(p_default):
        return p_default

    return p1


# ============================================================
# DASHBOARD ANALYTICS (POWER BI COMPATIBLE)
# ============================================================

def get_dashboard_data():
    file_path = get_dataset_path()

    if not os.path.exists(file_path):
        return {
            "dataset_uploaded": False,
            "total_patients": 0,
            "average_age": 0,
            "diabetes_cases": 0,
            "borderline_diabetes_cases": 0,
            "heart_disease_cases": 0,
            "hypertension_cases": 0,
            "total_disease_cases": 0,
            "disease_distribution": [],
            "patient_statistics": [],
            "disease_breakdown": {}
        }

    df = pd.read_csv(file_path)
    total_patients = len(df)
    mapping = detect_and_map_columns(df)

    # Average age
    if "age" in mapping and mapping["age"] in df.columns:
        age_col = pd.to_numeric(df[mapping["age"]], errors="coerce")
        average_age = round(float(age_col.dropna().mean()), 2) if not age_col.dropna().empty else 0.0
    else:
        average_age = 0.0

    # Calculate dynamic disease breakdown using centralized logic
    breakdown = get_disease_breakdown(df, mapping)

    diabetes_data = breakdown.get("diabetes", {})
    htn_data = breakdown.get("hypertension", {})
    heart_data = breakdown.get("heart_disease", {})

    diabetes_cases = diabetes_data.get("positive")
    borderline_diabetes_cases = diabetes_data.get("borderline", 0)
    heart_disease_cases = heart_data.get("positive")
    hypertension_cases = htn_data.get("positive")

    # Diagnosed positive cases
    total_disease_cases = 0
    for d_info in [htn_data, diabetes_data, heart_data]:
        if d_info.get("available") and d_info.get("positive") is not None:
            total_disease_cases += d_info["positive"]

    # Disease distribution (donut chart)
    disease_distribution = []
    if htn_data.get("available") and hypertension_cases is not None:
        disease_distribution.append({
            "name": "Hypertension",
            "value": hypertension_cases
        })
    if diabetes_data.get("available") and diabetes_cases is not None:
        disease_distribution.append({
            "name": "Diabetes",
            "value": diabetes_cases
        })
    if diabetes_data.get("available") and borderline_diabetes_cases > 0:
        disease_distribution.append({
            "name": "Pre-Diabetes (Borderline)",
            "value": borderline_diabetes_cases
        })
    if heart_data.get("available") and heart_disease_cases is not None:
        disease_distribution.append({
            "name": "Heart Disease",
            "value": heart_disease_cases
        })

    # Patient statistics (bar chart)
    patient_statistics = [
        {"name": "Total Patients", "value": total_patients}
    ]
    if htn_data.get("available") and hypertension_cases is not None:
        patient_statistics.append({"name": "Hypertension", "value": hypertension_cases})
    if diabetes_data.get("available") and diabetes_cases is not None:
        patient_statistics.append({"name": "Diabetes", "value": diabetes_cases})
    if diabetes_data.get("available") and borderline_diabetes_cases > 0:
        patient_statistics.append({"name": "Pre-Diabetes", "value": borderline_diabetes_cases})
    if heart_data.get("available") and heart_disease_cases is not None:
        patient_statistics.append({"name": "Heart Disease", "value": heart_disease_cases})

    # Serializable breakdown dictionary
    serializable_breakdown = {
        k: {
            "name": v["name"],
            "available": v["available"],
            "positive": v["positive"],
            "negative": v["negative"],
            "borderline": v.get("borderline", 0),
            "missing": v["missing"],
            "prevalence_pct": v["prevalence_pct"],
            "total_valid": v.get("total_valid", (v.get("positive") or 0) + (v.get("negative") or 0))
        }
        for k, v in breakdown.items()
    }

    return {
        "dataset_uploaded": True,
        "total_patients": total_patients,
        "average_age": average_age,
        "diabetes_cases": diabetes_cases,
        "borderline_diabetes_cases": borderline_diabetes_cases,
        "heart_disease_cases": heart_disease_cases,
        "hypertension_cases": hypertension_cases,
        "total_disease_cases": total_disease_cases,
        "disease_distribution": disease_distribution,
        "patient_statistics": patient_statistics,
        "disease_breakdown": serializable_breakdown
    }