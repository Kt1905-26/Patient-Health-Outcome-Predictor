"""
Patient Health Outcome Predictor - Power BI-Inspired Healthcare Analytics Dashboard
Engineered with Streamlit, Plotly, Pandas, NumPy, Scikit-Learn

8 Functional Pages:
1. Dashboard Overview
2. Upload Dataset
3. Data Cleaning
4. Data Analysis
5. Healthcare Analytics (15 Power BI Visualizations)
6. Disease Analysis
7. Patient Prediction (Random Forest AI)
8. Generate Reports
"""

import os
import sys
import io
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Add workspace to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

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
    POWER_BI_THEME
)

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Healthcare Intelligence | Power BI Analytics",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# POWER BI STYLING & CUSTOM CSS
# ==============================================================================
st.markdown("""
<style>
    /* Global Typography & Palette */
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    }
    
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Top Header Bar */
    .pbi-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 22px 28px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.12);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .pbi-header h1 {
        color: #ffffff;
        font-size: 26px;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .pbi-header p {
        color: #94a3b8;
        font-size: 13px;
        margin: 4px 0 0;
    }
    .pbi-badge {
        background-color: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    /* KPI Card Style */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        border: 1px solid #e2e8f0;
        border-top: 4px solid #0284c7;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.09);
    }
    .kpi-card.green { border-top-color: #10b981; }
    .kpi-card.amber { border-top-color: #f59e0b; }
    .kpi-card.red { border-top-color: #ef4444; }
    .kpi-card.purple { border-top-color: #8b5cf6; }
    
    .kpi-title {
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .kpi-sub {
        font-size: 12px;
        color: #94a3b8;
    }
    
    /* Power BI Panel Container */
    .pbi-panel {
        background: white;
        border-radius: 12px;
        padding: 22px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        margin-bottom: 20px;
    }
    .pbi-panel-title {
        font-size: 16px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Smart Insight Box */
    .insight-box {
        background: #ffffff;
        border-left: 4px solid #0284c7;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
        border-top: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
    }
    .insight-box.warning { border-left-color: #f59e0b; background-color: #fffbeb; }
    .insight-box.success { border-left-color: #10b981; background-color: #f0fdf4; }
    .insight-box.danger { border-left-color: #ef4444; background-color: #fef2f2; }
    
    /* Custom Sidebar Branding */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 0 20px;
        border-bottom: 1px solid #334155;
        margin-bottom: 20px;
    }
    .sidebar-brand-icon {
        width: 38px;
        height: 38px;
        background: #0284c7;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================
DEFAULT_CSV_PATH = os.path.join(BASE_DIR, "dataset", "patient_health_dataset.csv")

if "raw_df" not in st.session_state:
    if os.path.exists(DEFAULT_CSV_PATH):
        try:
            st.session_state["raw_df"] = pd.read_csv(DEFAULT_CSV_PATH)
            st.session_state["dataset_name"] = "patient_health_dataset.csv (NHANES Cohort)"
        except Exception:
            st.session_state["raw_df"] = pd.DataFrame()
            st.session_state["dataset_name"] = "No Dataset Loaded"
    else:
        st.session_state["raw_df"] = pd.DataFrame()
        st.session_state["dataset_name"] = "No Dataset Loaded"

if "cleaned_df" not in st.session_state:
    st.session_state["cleaned_df"] = None

if "cleaning_report" not in st.session_state:
    st.session_state["cleaning_report"] = None

if "active_nav" not in st.session_state:
    st.session_state["active_nav"] = "Dashboard Overview"

if "filter_age" not in st.session_state:
    st.session_state["filter_age"] = "All"

if "filter_gender" not in st.session_state:
    st.session_state["filter_gender"] = "All"

if "filter_disease" not in st.session_state:
    st.session_state["filter_disease"] = "All"

if "filter_risk" not in st.session_state:
    st.session_state["filter_risk"] = "All"


def get_current_df() -> tuple[pd.DataFrame, bool]:
    """
    Returns active working DataFrame: cleaned version if exists, else raw.
    """
    if st.session_state["cleaned_df"] is not None and not st.session_state["cleaned_df"].empty:
        return st.session_state["cleaned_df"], True
    return st.session_state["raw_df"], False


active_df, is_cleaned_active = get_current_df()
column_mapping = detect_and_map_columns(active_df) if not active_df.empty else {}


# ==============================================================================
# SIDEBAR NAVIGATION & POWER BI SLICERS
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">✚</div>
        <div>
            <div style="font-size: 16px; font-weight: 700; color: #0f172a;">HealthPulse BI</div>
            <div style="font-size: 11px; color: #64748b;">Clinical Analytics Suite</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.8px;'>NAVIGATION</p>", unsafe_allow_html=True)

    nav_options = [
        "1. Dashboard Overview",
        "2. Upload Dataset",
        "3. Data Cleaning",
        "4. Data Analysis",
        "5. Healthcare Analytics",
        "6. Disease Analysis",
        "7. Patient Prediction",
        "8. Generate Reports"
    ]

    selected_nav = st.radio(
        "Navigate to:",
        nav_options,
        index=0,
        label_visibility="collapsed"
    )
    # Strip leading numbering for clean matching
    page_name = selected_nav.split(". ", 1)[1] if ". " in selected_nav else selected_nav

    st.markdown("---")
    
    # Dataset Status Indicator
    st.markdown("<p style='font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.8px;'>DATASET STATE</p>", unsafe_allow_html=True)
    if not active_df.empty:
        status_color = "#10b981" if is_cleaned_active else "#0284c7"
        status_text = "Cleaned Active" if is_cleaned_active else "Raw Active"
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; padding: 12px; border: 1px solid #e2e8f0; font-size: 12px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                <span style="height: 8px; width: 8px; border-radius: 50%; background-color: {status_color}; display: inline-block;"></span>
                <strong style="color: #0f172a;">{status_text}</strong>
            </div>
            <div style="color: #64748b; word-break: break-all;">{st.session_state['dataset_name']}</div>
            <div style="color: #0f172a; margin-top: 4px; font-weight: 600;">{len(active_df):,} Rows | {len(active_df.columns)} Cols</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No dataset loaded.")

    # Power BI Filters / Slicers
    st.markdown("<p style='font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.8px;'>POWER BI SLICERS</p>", unsafe_allow_html=True)
    
    slicer_age = st.selectbox(
        "Age Bracket:",
        ["All", "< 30", "30-44", "45-59", "60-74", "75+"],
        index=["All", "< 30", "30-44", "45-59", "60-74", "75+"].index(st.session_state["filter_age"])
    )
    st.session_state["filter_age"] = slicer_age

    slicer_gender = st.selectbox(
        "Gender:",
        ["All", "Male", "Female"],
        index=["All", "Male", "Female"].index(st.session_state["filter_gender"])
    )
    st.session_state["filter_gender"] = slicer_gender

    slicer_disease = st.selectbox(
        "Chronic Condition:",
        ["All", "Diabetes", "Pre-Diabetes", "Heart Disease", "Hypertension", "Smokers"],
        index=["All", "Diabetes", "Pre-Diabetes", "Heart Disease", "Hypertension", "Smokers"].index(st.session_state["filter_disease"]) if st.session_state["filter_disease"] in ["All", "Diabetes", "Pre-Diabetes", "Heart Disease", "Hypertension", "Smokers"] else 0
    )
    st.session_state["filter_disease"] = slicer_disease

    slicer_risk = st.selectbox(
        "Health Risk Level:",
        ["All", "Low Risk", "Moderate Risk", "High Risk"],
        index=["All", "Low Risk", "Moderate Risk", "High Risk"].index(st.session_state["filter_risk"])
    )
    st.session_state["filter_risk"] = slicer_risk

    if st.button("↺ Reset Filters", use_container_width=True):
        st.session_state["filter_age"] = "All"
        st.session_state["filter_gender"] = "All"
        st.session_state["filter_disease"] = "All"
        st.session_state["filter_risk"] = "All"
        st.rerun()


# Apply global filters to working dataset for downstream display
filtered_active_df = apply_dataset_filters(
    active_df,
    age_group=st.session_state["filter_age"],
    gender_filter=st.session_state["filter_gender"],
    disease_filter=st.session_state["filter_disease"],
    risk_filter=st.session_state["filter_risk"],
    mapping=column_mapping
)


# ==============================================================================
# TOP BAR HEADER
# ==============================================================================
st.markdown(f"""
<div class="pbi-header">
    <div>
        <h1>{page_name}</h1>
        <p>Microsoft Power BI-Inspired Healthcare Intelligence & Outcome Predictor</p>
    </div>
    <div>
        <span class="pbi-badge">● Random Forest ML Online</span>
        <span class="pbi-badge" style="margin-left: 8px;">Filtered Cohort: {len(filtered_active_df):,} / {len(active_df):,}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# PAGE 1: DASHBOARD OVERVIEW
# ==============================================================================
if page_name == "Dashboard Overview":
    if filtered_active_df.empty:
        st.warning("⚠️ No data available matching active filters. Please reset filters or upload a dataset.")
    else:
        kpis = calculate_healthcare_kpis(filtered_active_df, column_mapping)

        # 4 Top Primary KPI Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Active Patients</div>
                <div class="kpi-value">{kpis['total_patients']:,}</div>
                <div class="kpi-sub">Cohort sample size</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="kpi-card green">
                <div class="kpi-title">Average Patient Age</div>
                <div class="kpi-value">{kpis['average_age']} <span style="font-size: 16px; font-weight: normal;">yrs</span></div>
                <div class="kpi-sub">Baseline demographic mean</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="kpi-card amber">
                <div class="kpi-title">Documented Disease Cases</div>
                <div class="kpi-value">{kpis['total_disease_cases']:,}</div>
                <div class="kpi-sub">Cumulative diagnosed cases</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="kpi-card red">
                <div class="kpi-title">High-Risk Patients</div>
                <div class="kpi-value">{kpis['high_risk_patients']:,} <span style="font-size: 14px; color: #ef4444;">({kpis['high_risk_percentage']}%)</span></div>
                <div class="kpi-sub">Multi-morbidity risk threshold</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Disease Condition KPIs (Dynamic & Data Unavailable Fallbacks)
        d_break = kpis.get("disease_breakdown", {})
        htn_info = d_break.get("hypertension", {})
        dia_info = d_break.get("diabetes", {})
        hd_info = d_break.get("heart_disease", {})

        htn_disp = f"{htn_info['positive']:,}" if htn_info.get("available") and htn_info.get("positive") is not None else "Data Unavailable"
        if dia_info.get("available") and dia_info.get("positive") is not None:
            dia_disp = f"{dia_info['positive']:,}"
            if dia_info.get("borderline", 0) > 0:
                dia_disp += f" (+{dia_info['borderline']:,} Pre-Dia)"
        else:
            dia_disp = "Data Unavailable"
        hd_disp = f"{hd_info['positive']:,}" if hd_info.get("available") and hd_info.get("positive") is not None else "Data Unavailable"

        dk1, dk2, dk3 = st.columns(3)
        with dk1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Hypertension Diagnoses</div>
                <div class="kpi-value">{htn_disp}</div>
                <div class="kpi-sub">Enc: 1=Pos (2,443), 0=Neg (5,366)</div>
            </div>
            """, unsafe_allow_html=True)
        with dk2:
            st.markdown(f"""
            <div class="kpi-card purple">
                <div class="kpi-title">Diabetes Diagnoses</div>
                <div class="kpi-value">{dia_disp}</div>
                <div class="kpi-sub">Enc: 1=Pos (1,070), 2=Neg (6,466), 3=Pre-Dia (270)</div>
            </div>
            """, unsafe_allow_html=True)
        with dk3:
            st.markdown(f"""
            <div class="kpi-card red">
                <div class="kpi-title">Heart Disease Diagnoses</div>
                <div class="kpi-value">{hd_disp}</div>
                <div class="kpi-sub">Enc: 1=Pos (402), 2=Neg (7,371), Missing: 36</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # 4 Secondary Vitals KPI Cards
        v1, v2, v3, v4 = st.columns(4)
        with v1:
            st.markdown(f"""
            <div class="kpi-card purple">
                <div class="kpi-title">Average BMI</div>
                <div class="kpi-value">{kpis['avg_indicators']['bmi']}</div>
                <div class="kpi-sub">Normal target: 18.5 - 24.9</div>
            </div>
            """, unsafe_allow_html=True)
        with v2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Mean Fasting Glucose</div>
                <div class="kpi-value">{kpis['avg_indicators']['glucose']} <span style="font-size: 14px;">mg/dL</span></div>
                <div class="kpi-sub">Pre-diabetic limit: 100 mg/dL</div>
            </div>
            """, unsafe_allow_html=True)
        with v3:
            st.markdown(f"""
            <div class="kpi-card green">
                <div class="kpi-title">Mean Systolic BP</div>
                <div class="kpi-value">{kpis['avg_indicators']['systolic_bp']} <span style="font-size: 14px;">mmHg</span></div>
                <div class="kpi-sub">Hypertension threshold: 130+</div>
            </div>
            """, unsafe_allow_html=True)
        with v4:
            st.markdown(f"""
            <div class="kpi-card amber">
                <div class="kpi-title">Mean Cholesterol</div>
                <div class="kpi-value">{kpis['avg_indicators']['cholesterol']} <span style="font-size: 14px;">mg/dL</span></div>
                <div class="kpi-sub">Desirable: < 200 mg/dL</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

        # Visual Overview: Two interactive charts
        col_left, col_right = st.columns(2)
        vis_bundle = generate_15_healthcare_visualizations(filtered_active_df, column_mapping)
        figs = vis_bundle.get("figures", {})

        with col_left:
            st.markdown('<div class="pbi-panel"><div class="pbi-panel-title">📊 Disease Distribution</div>', unsafe_allow_html=True)
            if "disease_distribution" in figs:
                st.plotly_chart(figs["disease_distribution"], use_container_width=True)
            else:
                st.info("Disease distribution chart requires diagnostic columns.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="pbi-panel"><div class="pbi-panel-title">👥 Gender Distribution</div>', unsafe_allow_html=True)
            if "gender_distribution" in figs:
                st.plotly_chart(figs["gender_distribution"], use_container_width=True)
            else:
                st.info("Gender breakdown requires gender column.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Smart Healthcare Insights on Overview
        st.markdown('<div class="pbi-panel"><div class="pbi-panel-title">💡 Smart Healthcare AI Observations</div>', unsafe_allow_html=True)
        insights = generate_smart_healthcare_insights(filtered_active_df, column_mapping)
        for ins in insights:
            box_cls = ins.get("type", "info")
            st.markdown(f"""
            <div class="insight-box {box_cls}">
                <strong style="color: #0f172a;">[{ins['category']}] {ins['title']}</strong><br/>
                <span style="color: #475467; font-size: 13px;">{ins['observation']}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# PAGE 2: UPLOAD DATASET
# ==============================================================================
elif page_name == "Upload Dataset":
    st.markdown('<div class="pbi-panel"><div class="pbi-panel-title">📁 Drag and Drop Patient Health Records</div>', unsafe_allow_html=True)
    st.write("Upload any CSV or Excel (.xlsx, .xls) dataset. NHANES datasets and standard clinic registries are automatically mapped.")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Upload patient clinical dataset"
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_size_kb = round(len(file_bytes) / 1024, 2)
        new_df, err = load_dataset_file(io.BytesIO(file_bytes), uploaded_file.name)

        if err:
            st.error(f"❌ {err}")
        else:
            st.success(f"✓ Dataset '{uploaded_file.name}' loaded successfully! ({file_size_kb:,} KB)")
            if st.button("Activate and Propagate Across Dashboard", type="primary"):
                st.session_state["raw_df"] = new_df
                st.session_state["dataset_name"] = uploaded_file.name
                st.session_state["cleaned_df"] = None  # Reset cleaning on new raw dataset
                st.session_state["cleaning_report"] = None
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Active Dataset Diagnostic Summary
    if not active_df.empty:
        overview = get_dataset_overview(active_df, filename=st.session_state["dataset_name"])
        
        st.markdown('<div class="pbi-panel"><div class="pbi-panel-title">🔍 Dataset Diagnostics & Metadata</div>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Records", f"{overview['rows']:,}")
        m2.metric("Total Columns", f"{overview['columns']}")
        m3.metric("Missing Cells", f"{overview['missing_total']:,} ({overview['missing_pct']}%)")
        m4.metric("Duplicate Rows", f"{overview['duplicate_rows']:,}")
        
        st.markdown("#### Detected Healthcare Column Mapping")
        mapping = overview["detected_mapping"]
        if mapping:
            map_cols = st.columns(4)
            idx = 0
            for k, v in mapping.items():
                map_cols[idx % 4].write(f"**{k.replace('_', ' ').title()}:** `{v}`")
                idx += 1
        else:
            st.info("No standard clinical columns mapped. Dynamic charts will use generic column types.")

        st.markdown("#### First 15 Records Preview")
        st.dataframe(active_df.head(15), use_container_width=True)

        st.markdown("#### Summary Statistics")
        num_cols = active_df.select_dtypes(include=[np.number]).columns
        if not num_cols.empty:
            st.dataframe(active_df[num_cols].describe().round(2), use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# PAGE 3: DATA CLEANING
# ==============================================================================
elif page_name == "Data Cleaning":
    st.markdown('<div class="pbi-panel"><div class="pbi-panel-title">🧹 Healthcare Data Cleansing & Quality Control</div>', unsafe_allow_html=True)
    st.write("Inspect data hygiene, handle survey missing codes, impute missing values, filter IQR outliers, and eliminate duplicate records on an isolated copy.")

    if active_df.empty:
        st.warning("Please upload a dataset first.")
    else:
        # Detect Data Issues
        issues = detect_data_issues(active_df)

        st.markdown("### 1. Data Quality Audit")
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Total Missing Values", f"{issues['total_missing']:,}")
        d2.metric("Duplicate Rows", f"{issues['duplicate_rows']:,}")
        d3.metric("Outlier Columns", f"{len(issues.get('outlier_details', []))}")
        d4.metric("Empty Rows", f"{issues['empty_rows']:,}")

        if issues.get("missing_details"):
            with st.expander("Detailed Missing Values by Column"):
                st.table(pd.DataFrame(issues["missing_details"]))

        if issues.get("outlier_details"):
            with st.expander("Detected IQR Outliers by Column"):
                st.table(pd.DataFrame(issues["outlier_details"]))

        st.markdown("---")
        st.markdown("### 2. Cleaning Configuration & Actions")

        c_opt1, c_opt2, c_opt3 = st.columns(3)
        with c_opt1:
            missing_strat = st.selectbox(
                "Missing Value Strategy:",
                ["mean", "median", "mode", "drop"],
                help="Method used to handle null entries across numerical/categorical features."
            )
            handle_nhanes = st.checkbox("Handle NHANES Missing Codes (7, 9, 77, 99, 777, 999)", value=True)

        with c_opt2:
            remove_dups = st.checkbox("Remove Duplicate Rows", value=True)
            remove_empty_rows = st.checkbox("Remove Completely Empty Rows/Columns", value=True)

        with c_opt3:
            filter_outliers = st.checkbox("Filter Outliers using IQR Method", value=False)
            num_cols = active_df.select_dtypes(include=[np.number]).columns.tolist()
            selected_outlier_cols = st.multiselect("Select columns for outlier filtering:", num_cols, default=num_cols[:3] if len(num_cols) >= 3 else num_cols)

        # 6 Dedicated Functional Buttons
        st.markdown("##### Cleaning Control Center")
        btn_col1, btn_col2, btn_col3, btn_col4, btn_col5, btn_col6 = st.columns(6)

        with btn_col1:
            detect_clicked = st.button("🔍 Detect Issues", use_container_width=True)
        with btn_col2:
            clean_clicked = st.button("✨ Clean Dataset", type="primary", use_container_width=True)
        with btn_col3:
            preview_clicked = st.button("👁 Preview Cleaned", use_container_width=True)
        with btn_col4:
            compare_clicked = st.button("⚖ Compare B/A", use_container_width=True)
        with btn_col5:
            reset_clicked = st.button("↺ Reset Cleaning", use_container_width=True)
        with btn_col6:
            if st.session_state["cleaned_df"] is not None:
                csv_buffer = io.StringIO()
                st.session_state["cleaned_df"].to_csv(csv_buffer, index=False)
                st.download_button(
                    label="⬇ Download CSV",
                    data=csv_buffer.getvalue(),
                    file_name="cleaned_patient_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.button("⬇ Download CSV", disabled=True, use_container_width=True)

        if detect_clicked:
            st.session_state["show_cleaning_issues"] = True
            st.rerun()

        if clean_clicked:
            cleaned_df, report = perform_clean_dataset(
                st.session_state["raw_df"],
                handle_missing=True,
                missing_strategy=missing_strat,
                remove_duplicates=remove_dups,
                remove_outliers=filter_outliers,
                outlier_cols=selected_outlier_cols,
                convert_numeric=True,
                remove_empty=remove_empty_rows,
                handle_nhanes_codes=handle_nhanes
            )
            st.session_state["cleaned_df"] = cleaned_df
            st.session_state["cleaning_report"] = report
            st.session_state["show_cleaning_preview"] = True
            st.success("✓ Dataset cleaned successfully!")
            st.rerun()

        if reset_clicked:
            st.session_state["cleaned_df"] = None
            st.session_state["cleaning_report"] = None
            st.session_state["show_cleaning_preview"] = False
            st.session_state["show_cleaning_compare"] = False
            st.info("Reverted to raw dataset.")
            st.rerun()

        if preview_clicked:
            st.session_state["show_cleaning_preview"] = not st.session_state.get("show_cleaning_preview", False)

        if compare_clicked:
            st.session_state["show_cleaning_compare"] = not st.session_state.get("show_cleaning_compare", False)

        # Preview Section
        if st.session_state.get("show_cleaning_preview") and st.session_state["cleaned_df"] is not None:
            st.markdown("---")
            st.markdown("### 📋 Preview Cleaned Dataset (First 20 Records)")
            st.dataframe(st.session_state["cleaned_df"].head(20), use_container_width=True)

        # Before & After Comparison Section
        if st.session_state.get("show_cleaning_compare") and st.session_state["cleaned_df"] is not None:
            st.markdown("---")
            st.markdown("### ⚖ Before-and-After Comparison")
            raw_len = len(st.session_state["raw_df"])
            clean_len = len(st.session_state["cleaned_df"])
            raw_miss = int(st.session_state["raw_df"].isna().sum().sum())
            clean_miss = int(st.session_state["cleaned_df"].isna().sum().sum())
            raw_dup = int(st.session_state["raw_df"].duplicated().sum())
            clean_dup = int(st.session_state["cleaned_df"].duplicated().sum())

            cmp_df = pd.DataFrame({
                "Metric": ["Total Records", "Missing Values", "Duplicate Rows", "Total Columns"],
                "Before Cleaning (Raw)": [f"{raw_len:,}", f"{raw_miss:,}", f"{raw_dup:,}", len(st.session_state["raw_df"].columns)],
                "After Cleaning": [f"{clean_len:,}", f"{clean_miss:,}", f"{clean_dup:,}", len(st.session_state["cleaned_df"].columns)],
                "Net Impact": [f"-{raw_len - clean_len:,} removed", f"-{raw_miss - clean_miss:,} resolved", f"-{raw_dup - clean_dup:,} removed", "Standardized"]
            })
            st.table(cmp_df)

        # Cleaning Report Display
        if st.session_state["cleaning_report"]:
            st.markdown("---")
            st.markdown("### 3. Cleaning Audit Report")
            rep = st.session_state["cleaning_report"]
            
            comp1, comp2, comp3, comp4 = st.columns(4)
            comp1.metric("Raw Patients", f"{rep['raw_patients']:,}")
            comp2.metric("Cleaned Patients", f"{rep['cleaned_patients']:,}")
            comp3.metric("Rows Removed", f"{rep['rows_removed']:,}")
            comp4.metric("Missing After Cleaning", f"{rep['missing_values_after']:,}")

            st.write("**Operations Log:**")
            for op in rep.get("operations", []):
                st.write(f"- {op}")

    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# PAGE 4: DATA ANALYSIS
# ==============================================================================
elif page_name == "Data Analysis":
    st.markdown('<div class="pbi-panel"><div class="pbi-panel-title">📈 Statistical Exploratory Data Analysis & Dynamic Visualizer</div>', unsafe_allow_html=True)
    
    if filtered_active_df.empty:
        st.warning("No data available.")
    else:
        stats = get_comprehensive_statistics(filtered_active_df)

        tab1, tab2, tab3 = st.tabs(["Descriptive Statistics", "Correlation Matrix", "Dynamic Chart Generator"])

        with tab1:
            st.markdown("#### Numerical Feature Statistics")
            if stats.get("numeric_stats"):
                stats_df = pd.DataFrame(stats["numeric_stats"]).T
                st.dataframe(stats_df, use_container_width=True)
            else:
                st.info("No numerical features found.")

            st.markdown("#### Categorical Frequency Distribution")
            cat_stats = stats.get("categorical_stats", {})
            if cat_stats:
                for col_name, c_data in cat_stats.items():
                    with st.expander(f"Distribution: {col_name} ({c_data['unique_count']} unique values)"):
                        st.table(pd.DataFrame(list(c_data["value_counts"].items()), columns=["Category", "Frequency"]))
            else:
                st.info("No categorical columns identified.")

        with tab2:
            st.markdown("#### Pearson Correlation Heatmap")
            corr_info = stats.get("correlation_matrix", {})
            if corr_info and corr_info.get("columns"):
                c_cols = corr_info["columns"]
                c_vals = corr_info["values"]
                fig_corr = go.Figure(data=go.Heatmap(
                    z=c_vals,
                    x=c_cols,
                    y=c_cols,
                    colorscale="Blues",
                    text=c_vals,
                    texttemplate="%{text:.2f}"
                ))
                fig_corr.update_layout(template="plotly_white", height=600)
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.info("Insufficient numerical columns for correlation analysis.")

        with tab3:
            st.markdown("#### Dynamic Power BI Chart Builder")
            all_cols = list(filtered_active_df.columns)
            
            c_sel1, c_sel2, c_sel3 = st.columns(3)
            with c_sel1:
                chart_type = st.selectbox(
                    "Chart Type:",
                    ["Bar chart", "Line chart", "Pie chart", "Donut chart", "Histogram", "Scatter plot", "Box plot", "Violin plot", "Heatmap"]
                )
            with c_sel2:
                x_axis = st.selectbox("X-Axis Column:", all_cols, index=0)
            with c_sel3:
                y_axis = st.selectbox("Y-Axis Column (Optional for Histogram/Pie):", ["None"] + all_cols, index=1 if len(all_cols) > 1 else 0)

            # Generate Dynamic Chart
            try:
                if chart_type == "Bar chart":
                    if y_axis != "None":
                        fig_dyn = px.bar(filtered_active_df, x=x_axis, y=y_axis, title=f"Bar Chart: {x_axis} vs {y_axis}")
                    else:
                        vc = filtered_active_df[x_axis].value_counts().reset_index()
                        vc.columns = ["Category", "Count"]
                        fig_dyn = px.bar(vc, x="Category", y="Count", title=f"Frequency Count: {x_axis}")
                elif chart_type == "Line chart":
                    y_val = y_axis if y_axis != "None" else x_axis
                    fig_dyn = px.line(filtered_active_df, x=x_axis, y=y_val, title=f"Line Chart: {x_axis} vs {y_val}")
                elif chart_type in ["Pie chart", "Donut chart"]:
                    hole = 0.5 if chart_type == "Donut chart" else 0.0
                    counts = filtered_active_df[x_axis].value_counts().head(10)
                    fig_dyn = go.Figure(data=[go.Pie(labels=counts.index.astype(str), values=counts.values, hole=hole)])
                    fig_dyn.update_layout(title=f"{chart_type}: {x_axis}")
                elif chart_type == "Histogram":
                    fig_dyn = px.histogram(filtered_active_df, x=x_axis, nbins=30, title=f"Histogram of {x_axis}")
                elif chart_type == "Scatter plot":
                    if y_axis != "None":
                        fig_dyn = px.scatter(filtered_active_df, x=x_axis, y=y_axis, title=f"Scatter Plot: {x_axis} vs {y_axis}", opacity=0.7)
                    else:
                        fig_dyn = px.scatter(filtered_active_df, x=filtered_active_df.index, y=x_axis, labels={"x": "Index", "y": x_axis}, title=f"Scatter Plot: Index vs {x_axis}", opacity=0.7)
                elif chart_type == "Box plot":
                    if y_axis != "None":
                        fig_dyn = px.box(filtered_active_df, x=x_axis, y=y_axis, title=f"Box Plot: {x_axis} by {y_axis}")
                    else:
                        fig_dyn = px.box(filtered_active_df, y=x_axis, title=f"Box Plot of {x_axis}")
                elif chart_type == "Violin plot":
                    if y_axis != "None":
                        fig_dyn = px.violin(filtered_active_df, x=x_axis, y=y_axis, box=True, title=f"Violin Plot: {x_axis} by {y_axis}")
                    else:
                        fig_dyn = px.violin(filtered_active_df, y=x_axis, box=True, title=f"Violin Plot of {x_axis}")
                elif chart_type == "Heatmap":
                    sub_n = filtered_active_df.select_dtypes(include=[np.number])
                    if len(sub_n.columns) >= 2:
                        fig_dyn = px.imshow(sub_n.corr(), text_auto=True, title="Correlation Heatmap")
                    else:
                        fig_dyn = None
                        st.info("Need numerical features for heatmap.")

                if fig_dyn:
                    fig_dyn.update_layout(template="plotly_white")
                    st.plotly_chart(fig_dyn, use_container_width=True)

            except Exception as e:
                st.error(f"Error rendering chart: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# PAGE 5: HEALTHCARE ANALYTICS (15 Visualizations)
# ==============================================================================
elif page_name == "Healthcare Analytics":
    st.markdown('<div class="pbi-panel"><div class="pbi-panel-title">🏥 Advanced Power BI Healthcare Intelligence (15 Clinical Visualizations)</div>', unsafe_allow_html=True)
    
    if filtered_active_df.empty:
        st.warning("No data available.")
    else:
        # KPI Cards on Healthcare Analytics Page (Requirement 7)
        kpis_page5 = calculate_healthcare_kpis(filtered_active_df, column_mapping)
        pk1, pk2, pk3, pk4 = st.columns(4)
        with pk1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Patients</div>
                <div class="kpi-value">{kpis_page5['total_patients']:,}</div>
                <div class="kpi-sub">Cohort sample size</div>
            </div>
            """, unsafe_allow_html=True)
        with pk2:
            st.markdown(f"""
            <div class="kpi-card green">
                <div class="kpi-title">Average Patient Age</div>
                <div class="kpi-value">{kpis_page5['average_age']} <span style="font-size: 16px; font-weight: normal;">yrs</span></div>
                <div class="kpi-sub">Baseline demographic mean</div>
            </div>
            """, unsafe_allow_html=True)
        with pk3:
            st.markdown(f"""
            <div class="kpi-card amber">
                <div class="kpi-title">Total Disease Cases</div>
                <div class="kpi-value">{kpis_page5['total_disease_cases']:,}</div>
                <div class="kpi-sub">Diagnosed chronic cases</div>
            </div>
            """, unsafe_allow_html=True)
        with pk4:
            st.markdown(f"""
            <div class="kpi-card red">
                <div class="kpi-title">High-Risk Patients</div>
                <div class="kpi-value">{kpis_page5['high_risk_patients']:,} <span style="font-size: 14px; color: #ef4444;">({kpis_page5['high_risk_percentage']}%)</span></div>
                <div class="kpi-sub">Clinical risk threshold</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        pk5, pk6, pk7, pk8 = st.columns(4)
        with pk5:
            st.markdown(f"""
            <div class="kpi-card purple">
                <div class="kpi-title">Average BMI</div>
                <div class="kpi-value">{kpis_page5['avg_indicators']['bmi']}</div>
                <div class="kpi-sub">Normal: 18.5 - 24.9</div>
            </div>
            """, unsafe_allow_html=True)
        with pk6:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Mean Fasting Glucose</div>
                <div class="kpi-value">{kpis_page5['avg_indicators']['glucose']} <span style="font-size: 14px;">mg/dL</span></div>
                <div class="kpi-sub">Diabetic limit: 126+ mg/dL</div>
            </div>
            """, unsafe_allow_html=True)
        with pk7:
            st.markdown(f"""
            <div class="kpi-card green">
                <div class="kpi-title">Mean Systolic BP</div>
                <div class="kpi-value">{kpis_page5['avg_indicators']['systolic_bp']} <span style="font-size: 14px;">mmHg</span></div>
                <div class="kpi-sub">Hypertension: 130+ mmHg</div>
            </div>
            """, unsafe_allow_html=True)
        with pk8:
            g_dist = kpis_page5['gender_distribution']
            st.markdown(f"""
            <div class="kpi-card amber">
                <div class="kpi-title">Gender Distribution</div>
                <div class="kpi-value">{g_dist.get('Male', 0):,} M / {g_dist.get('Female', 0):,} F</div>
                <div class="kpi-sub">Demographic split</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        vis_bundle = generate_15_healthcare_visualizations(filtered_active_df, column_mapping)
        figs = vis_bundle.get("figures", {})

        # Row 1: Charts 1, 2, 3
        r1_c1, r1_c2, r1_c3 = st.columns(3)
        with r1_c1:
            if "disease_distribution" in figs:
                st.plotly_chart(figs["disease_distribution"], use_container_width=True)
            else:
                st.info("Chart 1: Disease Distribution unavailable (missing disease columns).")
        with r1_c2:
            if "gender_distribution" in figs:
                st.plotly_chart(figs["gender_distribution"], use_container_width=True)
            else:
                st.info("Chart 2: Gender Distribution unavailable.")
        with r1_c3:
            if "age_group_distribution" in figs:
                st.plotly_chart(figs["age_group_distribution"], use_container_width=True)
            else:
                st.info("Chart 3: Age Group Distribution unavailable.")

        # Row 2: Charts 4, 5, 6
        r2_c1, r2_c2, r2_c3 = st.columns(3)
        with r2_c1:
            if "demographics_stacked" in figs:
                st.plotly_chart(figs["demographics_stacked"], use_container_width=True)
            else:
                st.info("Chart 4: Patient Demographics Stacked Bar unavailable.")
        with r2_c2:
            if "disease_prevalence" in figs:
                st.plotly_chart(figs["disease_prevalence"], use_container_width=True)
            else:
                st.info("Chart 5: Disease Prevalence Bar unavailable.")
        with r2_c3:
            if "risk_gauge" in figs:
                st.plotly_chart(figs["risk_gauge"], use_container_width=True)
            else:
                st.info("Chart 6: Health Risk Gauge unavailable.")

        # Row 3: Charts 7, 8
        r3_c1, r3_c2 = st.columns([1.2, 1])
        with r3_c1:
            if "correlation_heatmap" in figs:
                st.plotly_chart(figs["correlation_heatmap"], use_container_width=True)
            else:
                st.info("Chart 7: Health Indicator Correlation Heatmap unavailable.")
        with r3_c2:
            if "bmi_distribution" in figs:
                st.plotly_chart(figs["bmi_distribution"], use_container_width=True)
            else:
                st.info("Chart 8: BMI Distribution unavailable.")

        # Row 4: Charts 9, 10
        r4_c1, r4_c2 = st.columns(2)
        with r4_c1:
            if "bp_distribution" in figs:
                st.plotly_chart(figs["bp_distribution"], use_container_width=True)
            else:
                st.info("Chart 9: Blood Pressure Distribution Box Plot unavailable.")
        with r4_c2:
            if "glucose_distribution" in figs:
                st.plotly_chart(figs["glucose_distribution"], use_container_width=True)
            else:
                st.info("Chart 10: Glucose Level Distribution unavailable.")

        # Row 5: Charts 11, 12
        r5_c1, r5_c2 = st.columns(2)
        with r5_c1:
            if "age_vs_outcome" in figs:
                st.plotly_chart(figs["age_vs_outcome"], use_container_width=True)
            else:
                st.info("Chart 11: Age vs Health Outcome Scatter unavailable.")
        with r5_c2:
            if "disease_risk_comparison" in figs:
                st.plotly_chart(figs["disease_risk_comparison"], use_container_width=True)
            else:
                st.info("Chart 12: Disease Risk Comparison unavailable.")

        # Row 6: Charts 13, 14, 15
        r6_c1, r6_c2, r6_c3 = st.columns(3)
        with r6_c1:
            if "feature_importance" in figs:
                st.plotly_chart(figs["feature_importance"], use_container_width=True)
            else:
                st.info("Chart 13: Feature Importance unavailable.")
        with r6_c2:
            if "missing_distribution" in figs:
                st.plotly_chart(figs["missing_distribution"], use_container_width=True)
            else:
                st.success("Chart 14: Zero missing data detected!")
        with r6_c3:
            if "radar_indicators" in figs:
                st.plotly_chart(figs["radar_indicators"], use_container_width=True)
            else:
                st.info("Chart 15: Radar Chart requires at least 3 clinical indicators.")

    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# PAGE 6: DISEASE ANALYSIS
# ==============================================================================
elif page_name == "Disease Analysis":
    st.markdown('<div class="pbi-panel"><div class="pbi-panel-title">🔬 Disease-Specific Epidemiological Analysis</div>', unsafe_allow_html=True)
    
    if filtered_active_df.empty:
        st.warning("No data available.")
    else:
        disease_res = get_detailed_disease_analysis(filtered_active_df, column_mapping)
        summaries = disease_res.get("disease_summaries", [])

        if not summaries:
            st.info("No standard disease columns (Diabetes, Heart Disease, Hypertension) identified in this dataset.")
        else:
            for d in summaries:
                if not d.get("available"):
                    st.markdown(f"""
                    <div style="background: white; border: 1px solid #e2e8f0; border-left: 4px solid #94a3b8; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                        <h4 style="margin: 0; color: #64748b;">Condition: {d['disease']} — <span style="color: #ef4444;">Data Unavailable</span></h4>
                        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">The corresponding clinical column for {d['disease']} is not present in the current dataset.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    continue

                with st.expander(f"Condition: {d['disease']} — {d['cases']:,} Cases ({d['prevalence_pct']}% Prevalence)", expanded=True):
                    # Clinical stats summary row
                    stat_cols = st.columns(4)
                    with stat_cols[0]:
                        st.metric("Confirmed Positive", f"{d['cases']:,}")
                    with stat_cols[1]:
                        st.metric("Confirmed Negative", f"{d['negative_cases']:,}")
                    with stat_cols[2]:
                        if d.get("borderline_cases") is not None and d.get("borderline_cases", 0) > 0:
                            st.metric("Pre-Diabetes (Cat 3)", f"{d['borderline_cases']:,}")
                        else:
                            st.metric("Borderline Cases", "N/A")
                    with stat_cols[3]:
                        st.metric("Missing / Excluded", f"{d['missing_cases']:,}", help="Missing records are strictly excluded and never counted as negative.")

                    st.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px solid #f1f5f9;'/>", unsafe_allow_html=True)

                    d_c1, d_c2, d_c3 = st.columns([1, 1, 1.2])

                    with d_c1:
                        st.write("**Age Group Breakdown (Positive Cohort):**")
                        if d.get("age_breakdown"):
                            st.table(pd.DataFrame(list(d["age_breakdown"].items()), columns=["Age Bracket", "Cases"]))

                    with d_c2:
                        st.write("**Gender Distribution (Positive Cohort):**")
                        if d.get("gender_breakdown"):
                            st.table(pd.DataFrame(list(d["gender_breakdown"].items()), columns=["Gender", "Cases"]))

                    with d_c3:
                        st.write("**Risk Factor Differences (Mean Values):**")
                        if d.get("risk_factors"):
                            rf_df = pd.DataFrame(d["risk_factors"]).T
                            rf_df.columns = ["With Condition", "Without Condition"]
                            st.table(rf_df)

                    if d.get("borderline_cases", 0) > 0 and d.get("borderline_age_breakdown"):
                        st.markdown("##### 📌 NHANES Category 3: Borderline / Pre-Diabetes Breakdown")
                        st.caption(f"There are {d['borderline_cases']:,} patients ({d.get('borderline_pct', 0)}%) classified as Category 3 (Pre-Diabetes/Borderline). Analyzed separately from diagnosed diabetics and healthy controls.")
                        b_col1, b_col2 = st.columns(2)
                        with b_col1:
                            st.write("**Borderline Age Breakdown:**")
                            st.table(pd.DataFrame(list(d["borderline_age_breakdown"].items()), columns=["Age Bracket", "Cases"]))
                        with b_col2:
                            if d.get("borderline_gender_breakdown"):
                                st.write("**Borderline Gender Breakdown:**")
                                st.table(pd.DataFrame(list(d["borderline_gender_breakdown"].items()), columns=["Gender", "Cases"]))

    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# PAGE 7: PATIENT PREDICTION (RANDOM FOREST ML)
# ==============================================================================
elif page_name == "Patient Prediction":
    st.markdown('<div class="pbi-panel"><div class="pbi-panel-title">🤖 AI-Powered Patient Health Outcome Predictor</div>', unsafe_allow_html=True)
    st.write("Input real-time patient clinical telemetry to predict multi-factor health risk using the trained Random Forest Classifier.")

    pred_c1, pred_c2 = st.columns([1.5, 1])

    with pred_c1:
        with st.form("patient_prediction_form"):
            st.markdown("#### Patient Telemetry Inputs")
            
            p_row1_c1, p_row1_c2, p_row1_c3 = st.columns(3)
            with p_row1_c1:
                age_val = st.number_input("Age (Years):", min_value=1, max_value=120, value=52)
            with p_row1_c2:
                gender_val = st.selectbox("Gender:", ["Male (1)", "Female (0)"])
                gender_num = 1 if "Male" in gender_val else 0
            with p_row1_c3:
                bmi_val = st.number_input("BMI (kg/m²):", min_value=10.0, max_value=60.0, value=28.4, step=0.1)

            p_row2_c1, p_row2_c2, p_row2_c3 = st.columns(3)
            with p_row2_c1:
                sys_bp = st.number_input("Systolic BP (mmHg):", min_value=60, max_value=240, value=135)
            with p_row2_c2:
                hr_val = st.number_input("Heart Rate (bpm):", min_value=40, max_value=200, value=78)
            with p_row2_c3:
                glu_val = st.number_input("Fasting Glucose (mg/dL):", min_value=40, max_value=400, value=112)

            p_row3_c1, p_row3_c2, p_row3_c3 = st.columns(3)
            with p_row3_c1:
                o2_val = st.number_input("O2 Saturation (%):", min_value=70.0, max_value=100.0, value=97.5, step=0.1)
            with p_row3_c2:
                temp_val = st.number_input("Body Temp (°C):", min_value=34.0, max_value=42.0, value=37.0, step=0.1)
            with p_row3_c3:
                prev_cond = st.number_input("Prior Chronic Conditions:", min_value=0, max_value=10, value=1)

            p_row4_c1, p_row4_c2 = st.columns(2)
            with p_row4_c1:
                smoking_val = st.selectbox("Smoking Status:", ["Non-Smoker (0)", "Smoker (1)"])
                smoking_num = 1 if "Smoker (1)" in smoking_val else 0
            with p_row4_c2:
                hosp_visits = st.number_input("Hospital Visits (Past 12M):", min_value=0, max_value=20, value=1)

            predict_submit = st.form_submit_button("🩺 Run AI Health Risk Prediction", type="primary", use_container_width=True)

    with pred_c2:
        st.markdown("#### Clinical Prediction Result")
        if predict_submit:
            payload = {
                "age": float(age_val),
                "gender": int(gender_num),
                "systolic_bp": float(sys_bp),
                "heart_rate": float(hr_val),
                "glucose": float(glu_val),
                "bmi": float(bmi_val),
                "oxygen_saturation": float(o2_val),
                "temperature": float(temp_val),
                "previous_conditions": int(prev_cond),
                "smoking": int(smoking_num),
                "hospital_visits": int(hosp_visits)
            }
            res = execute_patient_prediction(payload)
            if res.get("success", False):
                risk_label = res["risk"]
                conf = res["confidence"]
                
                badge_bg = "#fee2e2" if risk_label == "High Risk" else "#fef3c7" if risk_label == "Moderate Risk" else "#dcfce7"
                badge_color = "#b91c1c" if risk_label == "High Risk" else "#b45309" if risk_label == "Moderate Risk" else "#15803d"

                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 24px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    <div style="font-size: 12px; font-weight: 700; color: #64748b; letter-spacing: 1px;">PREDICTED OUTCOME</div>
                    <div style="display: inline-block; background-color: {badge_bg}; color: {badge_color}; font-size: 24px; font-weight: 700; padding: 8px 24px; border-radius: 24px; margin: 14px 0;">
                        {risk_label}
                    </div>
                    <div style="font-size: 13px; color: #475467; margin-bottom: 8px;">Model Confidence: <strong>{conf}%</strong></div>
                    <div style="width: 100%; background-color: #f1f5f9; height: 10px; border-radius: 6px; overflow: hidden; margin-bottom: 16px;">
                        <div style="width: {conf}%; background-color: {badge_color}; height: 100%;"></div>
                    </div>
                    <div style="font-size: 11px; color: #94a3b8; text-align: left; line-height: 1.5; border-top: 1px solid #f1f5f9; padding-top: 12px;">
                        <strong>Clinical Guidance:</strong> Prediction generated using pre-trained Random Forest Classifier trained on multidimensional clinical cohorts.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(res.get("error", "Prediction failed."))
        else:
            st.info("Fill out patient telemetry on the left and click **Run AI Health Risk Prediction**.")

    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# PAGE 8: GENERATE REPORTS
# ==============================================================================
elif page_name == "Generate Reports":
    st.markdown('<div class="pbi-panel"><div class="pbi-panel-title">📄 Healthcare Intelligence Reporting & Data Export</div>', unsafe_allow_html=True)
    st.write("Generate and download executive PDF reports, export cleaned CSV datasets, and download analytical summaries.")

    if active_df.empty:
        st.warning("No data available to generate report.")
    else:
        rep_c1, rep_c2 = st.columns(2)

        with rep_c1:
            st.markdown("#### 1. Executive PDF Healthcare Report")
            st.write("Includes executive KPI scorecard, demographic breakdown, AI-based smart insights, and clinical recommendations.")
            
            try:
                pdf_bytes = generate_pdf_healthcare_report(filtered_active_df, column_mapping)
                if pdf_bytes:
                    st.download_button(
                        label="⬇ Download Executive PDF Report",
                        data=bytes(pdf_bytes),
                        file_name="Healthcare_Intelligence_Report.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                else:
                    st.error("PDF generation library not available.")
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")

        with rep_c2:
            st.markdown("#### 2. Cleaned Dataset Export (CSV)")
            st.write("Export the current active dataset with all data cleaning transformations applied.")
            
            csv_buf = io.StringIO()
            filtered_active_df.to_csv(csv_buf, index=False)
            st.download_button(
                label="⬇ Download Cleaned Dataset (CSV)",
                data=csv_buf.getvalue(),
                file_name="patient_data_cleaned.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("#### 3. Analytical Summary Export (JSON)")
        stats_summary = get_comprehensive_statistics(filtered_active_df)
        kpis_summary = calculate_healthcare_kpis(filtered_active_df, column_mapping)
        full_export = {
            "dataset_name": st.session_state["dataset_name"],
            "generated_at": pd.Timestamp.now().isoformat(),
            "kpis": kpis_summary,
            "statistics": stats_summary
        }
        st.download_button(
            label="⬇ Export Analytical Summary (JSON)",
            data=json.dumps(full_export, indent=2, default=str),
            file_name="healthcare_analytics_summary.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

