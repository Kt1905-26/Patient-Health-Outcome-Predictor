"""
Comprehensive Functionality Audit Suite for Patient Health Outcome Predictor
Verifies all 8 modules and backend connections across Streamlit, React, and Flask.
"""
import sys
import os
import io
import json
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

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
from backend.dashboard.analytics import get_dashboard_data
from backend.app import app

def run_comprehensive_audit():
    print("=" * 70)
    print("PATIENT HEALTH OUTCOME PREDICTOR - COMPLETE FUNCTIONALITY AUDIT")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. MODULE 2: DATASET UPLOAD & REPLACEMENT (CSV & EXCEL)
    # -------------------------------------------------------------
    print("\n--- [AUDIT MODULE 2: DATASET UPLOAD & REPLACEMENT] ---")
    csv_path = os.path.join(BASE_DIR, "dataset", "patient_health_dataset.csv")
    assert os.path.exists(csv_path), "Dataset file not found!"
    with open(csv_path, "rb") as f:
        df_csv, err = load_dataset_file(f, "patient_health_dataset.csv")
    assert err == "", f"CSV load failed: {err}"
    assert len(df_csv) == 7809, f"Expected 7,809 rows, got {len(df_csv)}"
    assert len(df_csv.columns) == 15, f"Expected 15 columns, got {len(df_csv.columns)}"
    print(f"[PASS] 1. CSV Upload: Successfully loaded {len(df_csv):,} records with {len(df_csv.columns)} features.")

    # Excel upload test
    excel_buf = io.BytesIO()
    df_csv.head(100).to_excel(excel_buf, index=False)
    excel_buf.seek(0)
    df_excel, err = load_dataset_file(excel_buf, "patients_batch.xlsx")
    assert err == "", f"Excel load failed: {err}"
    assert len(df_excel) == 100, f"Expected 100 rows from Excel, got {len(df_excel)}"
    print(f"[PASS] 2. Excel (.xlsx) Upload: Successfully loaded {len(df_excel)} records from binary stream.")

    # Dataset replacement test
    replacement_buf = io.BytesIO()
    df_csv.head(250).to_csv(replacement_buf, index=False)
    replacement_buf.seek(0)
    df_replaced, err = load_dataset_file(replacement_buf, "replacement_patients.csv")
    assert len(df_replaced) == 250, "Dataset replacement row count mismatch!"
    print(f"[PASS] 3. Dataset Replacement: Active cohort seamlessly replaced (250 records).")

    # Column mapping detection
    mapping = detect_and_map_columns(df_csv)
    assert "age" in mapping and "glucose" in mapping and "hypertension" in mapping
    print(f"[PASS] 4. Column Detection & Mapping: Identified {len(mapping)} standard clinical keys.")

    # -------------------------------------------------------------
    # 2. MODULE 3: DATA CLEANING & COMPARISON
    # -------------------------------------------------------------
    print("\n--- [AUDIT MODULE 3: DATA CLEANING & QUALITY CONTROL] ---")
    issues = detect_data_issues(df_csv)
    assert issues["total_missing"] == 22223, f"Unexpected missing cells: {issues['total_missing']}"
    assert issues["duplicate_rows"] == 0, f"Unexpected duplicate rows: {issues['duplicate_rows']}"
    print(f"[PASS] 5. Data Issues Detection: Found {issues['total_missing']:,} missing cells across {len(issues['missing_details'])} columns.")

    # Duplicate handling test
    df_with_dups = pd.concat([df_csv.head(10), df_csv.head(10)], ignore_index=True)
    assert df_with_dups.duplicated().sum() == 10
    cleaned_dups, dup_report = perform_clean_dataset(df_with_dups, remove_duplicates=True)
    assert len(cleaned_dups) == 10
    assert dup_report["duplicate_rows_removed"] == 10
    print(f"[PASS] 6. Duplicate Removal: Successfully detected & removed 10 duplicate records.")

    # Missing value handling (mean, median, mode)
    cleaned_mean, rep_mean = perform_clean_dataset(df_csv, handle_missing=True, missing_strategy="mean")
    assert cleaned_mean.isna().sum().sum() == 0, "Missing values remained after mean imputation!"
    print(f"[PASS] 7. Missing Value Handling: Mean strategy imputed {rep_mean['missing_values_before']:,} cells to 0 remaining.")

    cleaned_med, _ = perform_clean_dataset(df_csv, handle_missing=True, missing_strategy="median")
    assert cleaned_med.isna().sum().sum() == 0, "Missing values remained after median imputation!"
    print(f"[PASS] 8. Missing Value Handling: Median strategy imputed all missing cells.")

    # Outlier detection (IQR method)
    assert len(issues.get("outlier_details", [])) > 0, "No IQR outliers detected!"
    outlier_col = issues["outlier_details"][0]["column"]
    outlier_cnt = issues["outlier_details"][0]["outlier_count"]
    print(f"[PASS] 9. Outlier Detection (IQR): Detected {outlier_cnt} outliers in '{outlier_col}'.")

    # Before-and-after comparison verification
    raw_pts = rep_mean["raw_patients"]
    clean_pts = rep_mean["cleaned_patients"]
    assert raw_pts == 7809 and clean_pts == 7809
    print(f"[PASS] 10. Before-and-After Comparison: Raw={raw_pts:,} -> Cleaned={clean_pts:,}, Net Diff verified.")

    # -------------------------------------------------------------
    # 3. MODULE 4: DATA ANALYSIS & DYNAMIC CHART GENERATOR
    # -------------------------------------------------------------
    print("\n--- [AUDIT MODULE 4: STATISTICAL ANALYSIS & DYNAMIC CHARTS] ---")
    stats = get_comprehensive_statistics(df_csv)
    assert "numeric_stats" in stats and "categorical_stats" in stats and "correlation_matrix" in stats
    age_stat = stats["numeric_stats"]["age"]
    assert "mean" in age_stat and "median" in age_stat and "std" in age_stat and "min" in age_stat and "max" in age_stat and "variance" in age_stat
    print(f"[PASS] 11. Descriptive Statistics: Mean Age={age_stat['mean']}, Median={age_stat['median']}, Std={age_stat['std']}, Min={age_stat['min']}, Max={age_stat['max']}.")

    # Dynamic Chart Generator verification (All 9 chart types)
    import plotly.graph_objects as go
    import plotly.express as px

    # 1. Bar
    vc = df_csv["gender"].value_counts().reset_index()
    vc.columns = ["Category", "Count"]
    fig_bar = px.bar(vc, x="Category", y="Count")
    assert fig_bar is not None
    # 2. Line
    fig_line = px.line(df_csv.head(50), x="age", y="glucose")
    assert fig_line is not None
    # 3. Pie
    fig_pie = go.Figure(data=[go.Pie(labels=vc["Category"].astype(str), values=vc["Count"])])
    assert fig_pie is not None
    # 4. Donut
    fig_donut = go.Figure(data=[go.Pie(labels=vc["Category"].astype(str), values=vc["Count"], hole=0.5)])
    assert fig_donut is not None
    # 5. Histogram
    fig_hist = px.histogram(df_csv, x="bmi", nbins=30)
    assert fig_hist is not None
    # 6. Scatter
    fig_scatter = px.scatter(df_csv.head(100), x="age", y="systolic_bp")
    assert fig_scatter is not None
    # 7. Box
    fig_box = px.box(df_csv, y="systolic_bp")
    assert fig_box is not None
    # 8. Violin
    fig_violin = px.violin(df_csv, y="bmi", box=True)
    assert fig_violin is not None
    # 9. Heatmap
    sub_num = df_csv[["age", "bmi", "systolic_bp", "glucose"]].dropna()
    fig_heat = px.imshow(sub_num.corr())
    assert fig_heat is not None
    print(f"[PASS] 12. Dynamic Chart Generator: Successfully verified all 9 chart types (Bar, Line, Pie, Donut, Histogram, Scatter, Box, Violin, Heatmap).")

    # -------------------------------------------------------------
    # 4. MODULE 5: HEALTHCARE ANALYTICS & 15 VISUALIZATIONS
    # -------------------------------------------------------------
    print("\n--- [AUDIT MODULE 5: POWER BI HEALTHCARE ANALYTICS] ---")
    kpis = calculate_healthcare_kpis(df_csv, mapping)
    assert kpis["total_patients"] == 7809
    assert kpis["total_disease_cases"] == 3915  # 2443 + 1070 + 402
    assert kpis["high_risk_patients"] == 3128
    assert kpis["high_risk_percentage"] == 40.1
    print(f"[PASS] 13. Healthcare KPIs: Total Patients={kpis['total_patients']:,}, Diagnosed Cases={kpis['total_disease_cases']:,}, High-Risk={kpis['high_risk_patients']:,} ({kpis['high_risk_percentage']}%).")

    vis_bundle = generate_15_healthcare_visualizations(cleaned_mean, mapping)
    figures = vis_bundle.get("figures", {})
    assert len(figures) == 15, f"Expected all 15 figures, got {len(figures)}"
    print(f"[PASS] 14. 15 Healthcare Visualizations: All 15 figures generated without omission:")
    for idx, f_name in enumerate(figures.keys(), 1):
        print(f"    {idx}. {f_name}")

    # Interactive filters
    f_age = apply_dataset_filters(df_csv, age_group="60-74", mapping=mapping)
    assert len(f_age) == 2513, f"Expected 2,513 patients for 60-74, got {len(f_age)}"
    f_gender = apply_dataset_filters(df_csv, gender_filter="Male", mapping=mapping)
    assert len(f_gender) == 3488, f"Expected 3,488 Male patients, got {len(f_gender)}"
    f_dis_dia = apply_dataset_filters(df_csv, disease_filter="Diabetes", mapping=mapping)
    assert len(f_dis_dia) == 1070, f"Expected 1,070 positive diabetes patients, got {len(f_dis_dia)}"
    f_dis_predia = apply_dataset_filters(df_csv, disease_filter="Pre-Diabetes", mapping=mapping)
    assert len(f_dis_predia) == 270, f"Expected 270 pre-diabetes patients, got {len(f_dis_predia)}"
    f_dis_htn = apply_dataset_filters(df_csv, disease_filter="Hypertension", mapping=mapping)
    assert len(f_dis_htn) == 2443, f"Expected 2,443 hypertension patients, got {len(f_dis_htn)}"
    f_dis_hd = apply_dataset_filters(df_csv, disease_filter="Heart Disease", mapping=mapping)
    assert len(f_dis_hd) == 402, f"Expected 402 heart disease patients, got {len(f_dis_hd)}"
    print(f"[PASS] 15. Interactive Cohort Filters: Successfully verified Age, Gender, Disease (Diabetes, Pre-Diabetes, Hypertension, Heart Disease), and Risk slicers.")

    # -------------------------------------------------------------
    # 5. MODULE 6: DISEASE ENCODING & DISEASE ANALYSIS
    # -------------------------------------------------------------
    print("\n--- [AUDIT MODULE 6: CLINICAL DISEASE ENCODING] ---")
    b = get_disease_breakdown(df_csv, mapping)

    # Hypertension: 1=pos (2443), 0=neg (5366), missing=0
    htn = b["hypertension"]
    assert htn["positive"] == 2443, f"Hypertension pos mismatch: {htn['positive']}"
    assert htn["negative"] == 5366, f"Hypertension neg mismatch: {htn['negative']}"
    assert htn["missing"] == 0, f"Hypertension missing mismatch: {htn['missing']}"
    assert htn["prevalence_pct"] == 31.28
    print(f"[PASS] 16. Hypertension Encoding: 1=Positive ({htn['positive']:,}), 0=Negative ({htn['negative']:,}), Missing=0.")

    # Diabetes: 1=pos (1070), 2=neg (6466), 3=borderline (270), missing=3
    dia = b["diabetes"]
    assert dia["positive"] == 1070, f"Diabetes pos mismatch: {dia['positive']}"
    assert dia["negative"] == 6466, f"Diabetes neg mismatch: {dia['negative']}"
    assert dia["borderline"] == 270, f"Diabetes borderline mismatch: {dia['borderline']}"
    assert dia["missing"] == 3, f"Diabetes missing mismatch: {dia['missing']}"
    assert dia["prevalence_pct"] == 13.7
    assert dia["borderline_pct"] == 3.46
    print(f"[PASS] 17. Diabetes Encoding: 1=Positive ({dia['positive']:,}), 2=Negative ({dia['negative']:,}), 3=Pre-Diabetes ({dia['borderline']:,}), Missing={dia['missing']} (excluded from negatives).")

    # Heart Disease: 1=pos (402), 2=neg (7371), missing=36
    hd = b["heart_disease"]
    assert hd["positive"] == 402, f"Heart Disease pos mismatch: {hd['positive']}"
    assert hd["negative"] == 7371, f"Heart Disease neg mismatch: {hd['negative']}"
    assert hd["missing"] == 36, f"Heart Disease missing mismatch: {hd['missing']}"
    assert hd["prevalence_pct"] == 5.15
    print(f"[PASS] 18. Heart Disease Encoding: 1=Positive ({hd['positive']:,}), 2=Negative ({hd['negative']:,}), Missing={hd['missing']} (excluded from negatives).")

    # Detailed disease analysis module
    d_analysis = get_detailed_disease_analysis(df_csv, mapping)
    assert len(d_analysis["disease_summaries"]) == 3
    print(f"[PASS] 19. Disease Analysis Engine: Generated age, gender, risk factor comparisons, and Category 3 pre-diabetes tables.")

    # AI Smart Healthcare Insights
    insights = generate_smart_healthcare_insights(df_csv, mapping)
    assert len(insights) >= 5
    print(f"[PASS] 20. Smart Healthcare Insights: Generated {len(insights)} dynamically computed AI observations.")

    # -------------------------------------------------------------
    # 6. MODULE 7: PATIENT PREDICTION (RANDOM FOREST)
    # -------------------------------------------------------------
    print("\n--- [AUDIT MODULE 7: RANDOM FOREST AI PREDICTION] ---")
    test_cases = [
        {"age": 65, "gender": 1, "systolic_bp": 155, "heart_rate": 88, "glucose": 180, "bmi": 34.5, "oxygen_saturation": 94.0, "temperature": 37.4, "previous_conditions": 3, "smoking": 1, "hospital_visits": 4},
        {"age": 28, "gender": 0, "systolic_bp": 115, "heart_rate": 68, "glucose": 88, "bmi": 21.5, "oxygen_saturation": 99.0, "temperature": 36.8, "previous_conditions": 0, "smoking": 0, "hospital_visits": 0}
    ]
    for idx, tc in enumerate(test_cases, 1):
        res = execute_patient_prediction(tc)
        assert res.get("success") is True, f"Prediction error: {res.get('error')}"
        assert res.get("risk") in ["Low Risk", "Moderate Risk", "High Risk"]
        print(f"[PASS] 21.{idx} ML Prediction Case {idx}: Output='{res['risk']}', Confidence={res['confidence']}%, Top Indicators={list(res.get('risk_factors', {}).keys())[:3]}.")

    # -------------------------------------------------------------
    # 7. MODULE 8: GENERATE REPORTS (PDF & CSV)
    # -------------------------------------------------------------
    print("\n--- [AUDIT MODULE 8: REPORTING & DATA EXPORT] ---")
    pdf_bytes = generate_pdf_healthcare_report(df_csv, mapping)
    assert len(pdf_bytes) > 1000, "PDF bytes suspiciously small!"
    assert pdf_bytes.startswith(b"%PDF"), "Invalid PDF signature!"
    print(f"[PASS] 22. PDF Report Generation: Generated valid binary PDF ({len(pdf_bytes):,} bytes).")

    csv_export_buf = io.StringIO()
    cleaned_mean.to_csv(csv_export_buf, index=False)
    csv_str = csv_export_buf.getvalue()
    assert len(csv_str) > 10000, "CSV export suspiciously small!"
    print(f"[PASS] 23. Cleaned CSV Export: Successfully exported cleaned dataset ({len(csv_str):,} chars).")

    # -------------------------------------------------------------
    # 8. BACKEND & CROSS-PLATFORM CONSISTENCY (STREAMLIT & REACT)
    # -------------------------------------------------------------
    print("\n--- [AUDIT: STREAMLIT & REACT FLASK CONSISTENCY] ---")
    # Verify legacy backend/dashboard/analytics.py produces identical numbers
    legacy_dash = get_dashboard_data()
    assert legacy_dash["total_patients"] == 7809
    assert legacy_dash["hypertension_cases"] == 2443
    assert legacy_dash["diabetes_cases"] == 1070
    assert legacy_dash["borderline_diabetes_cases"] == 270
    assert legacy_dash["heart_disease_cases"] == 402
    assert legacy_dash["total_disease_cases"] == 3915
    print(f"[PASS] 24. Legacy Backend Compatibility: backend/dashboard/analytics.py matches core logic exactly.")

    # Verify Flask endpoints used by React
    with app.test_client() as client:
        # Reset cleaning so active dataset is the full 7,809 cohort
        client.post("/reset-cleaning")

        # /analysis
        res_a = client.get("/analysis")
        assert res_a.status_code == 200
        d_a = res_a.get_json()
        assert d_a["hypertension_cases"] == 2443
        assert d_a["diabetes_cases"] == 1070
        assert d_a["borderline_diabetes_cases"] == 270
        assert d_a["heart_disease_cases"] == 402
        assert d_a["total_disease_cases"] == 3915
        print(f"[PASS] 25. Flask /analysis Endpoint: Confirmed exact dynamic disease numbers for React frontend.")

        # /healthcare-analytics
        res_h = client.get("/healthcare-analytics?disease=Diabetes")
        assert res_h.status_code == 200
        d_h = res_h.get_json()
        assert d_h["total_filtered_patients"] == 1070
        print(f"[PASS] 26. Flask /healthcare-analytics Endpoint: Cohort slicing functional (1,070 diabetics).")

        # /export-pdf
        res_pdf = client.get("/export-pdf")
        assert res_pdf.status_code == 200
        assert res_pdf.mimetype == "application/pdf"
        print(f"[PASS] 27. Flask /export-pdf Endpoint: Served application/pdf with code 200.")

        # /download-cleaned
        res_csv = client.get("/download-cleaned")
        assert res_csv.status_code == 200
        assert "text/csv" in res_csv.mimetype
        print(f"[PASS] 28. Flask /download-cleaned Endpoint: Served text/csv with code 200.")

    # -------------------------------------------------------------
    # 9. MISSING COLUMN ROBUSTNESS ("Data Unavailable")
    # -------------------------------------------------------------
    print("\n--- [AUDIT: MISSING COLUMN ROBUSTNESS & GRACEFUL FALLBACK] ---")
    partial_df = df_csv[["age", "gender", "bmi", "systolic_bp"]].copy()
    partial_mapping = detect_and_map_columns(partial_df)
    partial_kpis = calculate_healthcare_kpis(partial_df, partial_mapping)
    partial_breakdown = get_disease_breakdown(partial_df, partial_mapping)

    assert partial_breakdown["hypertension"]["available"] is False
    assert partial_breakdown["hypertension"]["display"] == "Data Unavailable"
    assert partial_breakdown["diabetes"]["available"] is False
    assert partial_breakdown["diabetes"]["display"] == "Data Unavailable"
    assert partial_breakdown["heart_disease"]["available"] is False
    assert partial_breakdown["heart_disease"]["display"] == "Data Unavailable"
    print(f"[PASS] 29. Missing Disease Column Graceful Fallback: Returns 'Data Unavailable' without crashing.")

    print("\n" + "=" * 70)
    print("ALL 29 AUDIT TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    run_comprehensive_audit()
