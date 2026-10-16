import React, { useState, useEffect } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  LineChart,
  Line
} from "recharts";

import "./Dashboard.css";

const API_BASE = "http://127.0.0.1:5000";

// Power BI Palette
const COLORS = [
  "#0284c7",
  "#38bdf8",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#ec4899",
  "#6366f1"
];

function Dashboard({ activePage = "overview", setActivePage }) {
  // States
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [cleaningResult, setCleaningResult] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [issuesData, setIssuesData] = useState(null);
  const [diseaseData, setDiseaseData] = useState(null);
  const [insights, setInsights] = useState([]);

  // Filter Slicers
  const [filterAge, setFilterAge] = useState("All");
  const [filterGender, setFilterGender] = useState("All");
  const [filterDisease, setFilterDisease] = useState("All");
  const [filterRisk, setFilterRisk] = useState("All");

  // Dynamic Chart Builder States
  const [chartType, setChartType] = useState("Bar");
  const [xAxisCol, setXAxisCol] = useState("");
  const [yAxisCol, setYAxisCol] = useState("");

  // Cleaning options
  const [missingStrategy, setMissingStrategy] = useState("mean");
  const [removeDuplicates, setRemoveDuplicates] = useState(true);
  const [filterOutliers, setFilterOutliers] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [showComparison, setShowComparison] = useState(false);

  // Loading & status
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // Auto-fetch analysis data on initial mount
  useEffect(() => {
    fetchAnalysis();
    fetchInsights();
    fetchDiseaseAnalysis();
  }, []);

  // Re-fetch healthcare analytics when filters change
  useEffect(() => {
    if (activePage === "analytics") {
      fetchFilteredAnalytics();
    }
  }, [filterAge, filterGender, filterDisease, filterRisk]);

  const fetchAnalysis = async () => {
    try {
      const res = await fetch(`${API_BASE}/analysis`);
      if (res.ok) {
        const data = await res.json();
        setAnalysisData(data);
        if (data.numeric_columns && data.numeric_columns.length > 0) {
          if (!xAxisCol) setXAxisCol(data.numeric_columns[0]);
          if (!yAxisCol) setYAxisCol(data.numeric_columns[1] || data.numeric_columns[0]);
        }
      }
    } catch (err) {
      console.warn("Could not fetch initial analysis:", err);
    }
  };

  const fetchInsights = async () => {
    try {
      const res = await fetch(`${API_BASE}/smart-insights`);
      if (res.ok) {
        const data = await res.json();
        if (data.insights) setInsights(data.insights);
      }
    } catch (err) {
      console.warn("Could not fetch smart insights:", err);
    }
  };

  const fetchDiseaseAnalysis = async () => {
    try {
      const res = await fetch(`${API_BASE}/disease-analysis`);
      if (res.ok) {
        const data = await res.json();
        if (data.data) setDiseaseData(data.data);
      }
    } catch (err) {
      console.warn("Could not fetch disease analysis:", err);
    }
  };

  const fetchFilteredAnalytics = async () => {
    try {
      const params = new URLSearchParams({
        age_group: filterAge,
        gender: filterGender,
        disease: filterDisease,
        risk: filterRisk
      });
      const res = await fetch(`${API_BASE}/healthcare-analytics?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        if (data.kpis) {
          setAnalysisData((prev) => ({
            ...prev,
            total_patients: data.kpis.total_patients,
            average_age: data.kpis.average_age,
            total_disease_cases: data.kpis.total_disease_cases,
            high_risk_patients: data.kpis.high_risk_patients,
            high_risk_percentage: data.kpis.high_risk_percentage,
            average_bmi: data.kpis.avg_indicators?.bmi,
            average_glucose: data.kpis.avg_indicators?.glucose,
            average_systolic_bp: data.kpis.avg_indicators?.systolic_bp,
            average_cholesterol: data.kpis.avg_indicators?.cholesterol
          }));
        }
      }
    } catch (err) {
      console.warn("Error fetching filtered analytics:", err);
    }
  };

  // Upload Dataset Handler
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setError("");
      setMessage("");
    }
  };

  const uploadDataset = async () => {
    if (!selectedFile) {
      setError("Please select a CSV or Excel file first.");
      return;
    }
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const res = await fetch(`${API_BASE}/upload-csv`, {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Dataset upload failed.");

      setUploadResult(data);
      setMessage(data.message || "Dataset uploaded successfully.");
      // Refresh analysis and insights
      fetchAnalysis();
      fetchInsights();
      fetchDiseaseAnalysis();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Detect Issues Handler
  const detectDataIssues = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/detect-issues`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to detect issues.");
      setIssuesData(data.issues);
      setMessage("Data issue audit completed.");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Clean Data Handler
  const cleanDataset = async () => {
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const res = await fetch(`${API_BASE}/clean-data`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          missing_strategy: missingStrategy,
          remove_duplicates: removeDuplicates,
          remove_outliers: filterOutliers
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Data cleaning failed.");

      setCleaningResult(data);
      setMessage("Data cleaning completed successfully.");
      fetchAnalysis();
      fetchInsights();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Reset Cleaning
  const resetCleaning = async () => {
    try {
      const res = await fetch(`${API_BASE}/reset-cleaning`, { method: "POST" });
      if (res.ok) {
        setCleaningResult(null);
        setMessage("Cleaned dataset reset. Active data reverted to raw records.");
        fetchAnalysis();
      }
    } catch (err) {
      setError(err.message);
    }
  };

  // Reset Filters
  const resetFilters = () => {
    setFilterAge("All");
    setFilterGender("All");
    setFilterDisease("All");
    setFilterRisk("All");
  };

  const pieData = analysisData?.disease_distribution || [];
  const barData = analysisData?.patient_statistics || [];

  return (
    <div className="dashboard-container">
      {/* Messages */}
      {error && <div className="error-message">❌ {error}</div>}
      {message && <div className="global-success-message">✓ {message}</div>}

      {/* ==============================================================
          1. DASHBOARD OVERVIEW PAGE
      ============================================================== */}
      {activePage === "overview" && (
        <div>
          <div className="dashboard-header">
            <h1>Healthcare Executive Dashboard</h1>
            <p>Real-time clinical intelligence, biomarker distributions, and predictive triage.</p>
          </div>

          {/* ==============================================================
              POWER BI-INSPIRED 11-CARD RESPONSIVE KPI GRID (4 - 4 - 3)
              Row 1: 4 Demographics & Executive Outcome Metrics
              Row 2: 4 Clinical Biomarkers & Vitals
              Row 3: 3 Chronic Disease Diagnoses
          ============================================================== */}
          <div className="kpi-grid">
            {/* ROW 1 (Desktop: 4 cards, span 3 each) */}
            <div className="kpi-card-unified kpi-col-4 accent-blue">
              <div className="kpi-card-header">
                <span className="kpi-card-title">TOTAL PATIENTS</span>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#2563eb" }}></span>
              </div>
              <div className="kpi-card-metric">
                <span className="kpi-metric-main">{analysisData?.total_patients?.toLocaleString() || "—"}</span>
              </div>
              <div className="kpi-card-subtitle">Active cohort size</div>
            </div>

            <div className="kpi-card-unified kpi-col-4 accent-emerald">
              <div className="kpi-card-header">
                <span className="kpi-card-title">AVERAGE AGE</span>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#10b981" }}></span>
              </div>
              <div className="kpi-card-metric">
                <span className="kpi-metric-main">{analysisData?.average_age || "—"}</span>
                <span className="kpi-metric-unit">yrs</span>
              </div>
              <div className="kpi-card-subtitle">Cohort baseline demographic</div>
            </div>

            <div className="kpi-card-unified kpi-col-4 accent-amber">
              <div className="kpi-card-header">
                <span className="kpi-card-title">TOTAL DISEASE CASES</span>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#f59e0b" }}></span>
              </div>
              <div className="kpi-card-metric">
                <span className="kpi-metric-main">{analysisData?.total_disease_cases?.toLocaleString() || "—"}</span>
              </div>
              <div className="kpi-card-subtitle">Cumulative diagnosed cases</div>
            </div>

            <div className="kpi-card-unified kpi-col-4 accent-red">
              <div className="kpi-card-header">
                <span className="kpi-card-title">HIGH-RISK PATIENTS</span>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#ef4444" }}></span>
              </div>
              <div className="kpi-card-metric">
                <span className="kpi-metric-main red">{analysisData?.high_risk_patients?.toLocaleString() || "—"}</span>
                <span className="kpi-badge-supplement red">({analysisData?.high_risk_percentage || 0}%)</span>
              </div>
              <div className="kpi-card-subtitle">Multi-morbidity risk threshold</div>
            </div>

            {/* ROW 2 (Desktop: 4 cards, span 3 each) */}
            <div className="kpi-card-unified kpi-col-4 accent-purple">
              <div className="kpi-card-header">
                <span className="kpi-card-title">AVERAGE BMI</span>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#8b5cf6" }}></span>
              </div>
              <div className="kpi-card-metric">
                <span className="kpi-metric-main">{analysisData?.average_bmi || "—"}</span>
              </div>
              <div className="kpi-card-subtitle">Reference normal: 18.5 - 24.9</div>
            </div>

            <div className="kpi-card-unified kpi-col-4 accent-slate">
              <div className="kpi-card-header">
                <span className="kpi-card-title">MEAN FASTING GLUCOSE</span>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#0284c7" }}></span>
              </div>
              <div className="kpi-card-metric">
                <span className="kpi-metric-main">{analysisData?.average_glucose || "—"}</span>
                <span className="kpi-metric-unit">mg/dL</span>
              </div>
              <div className="kpi-card-subtitle">Normal threshold: &lt; 100 mg/dL</div>
            </div>

            <div className="kpi-card-unified kpi-col-4 accent-emerald">
              <div className="kpi-card-header">
                <span className="kpi-card-title">MEAN HBA1C</span>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#10b981" }}></span>
              </div>
              <div className="kpi-card-metric">
                <span className="kpi-metric-main">{analysisData?.average_hba1c || "—"}</span>
                <span className="kpi-metric-unit">%</span>
              </div>
              <div className="kpi-card-subtitle">Normal reference: &lt; 5.7%</div>
            </div>

            <div className="kpi-card-unified kpi-col-4 accent-amber">
              <div className="kpi-card-header">
                <span className="kpi-card-title">MEAN CHOLESTEROL</span>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#f59e0b" }}></span>
              </div>
              <div className="kpi-card-metric">
                <span className="kpi-metric-main">{analysisData?.average_cholesterol || "—"}</span>
                <span className="kpi-metric-unit">mg/dL</span>
              </div>
              <div className="kpi-card-subtitle">Desirable: &lt; 200 mg/dL</div>
            </div>

            {/* ROW 3 (Desktop: 3 cards, span 4 each) */}
            <div className="kpi-card-unified kpi-col-3 accent-blue">
              <div className="kpi-card-header">
                <span className="kpi-card-title">HYPERTENSION CASES</span>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#2563eb" }}></span>
              </div>
              <div className="kpi-card-metric">
                <span className="kpi-metric-main">
                  {analysisData?.disease_breakdown?.hypertension?.available
                    ? analysisData.hypertension_cases?.toLocaleString()
                    : analysisData?.hypertension_cases !== undefined && analysisData?.hypertension_cases !== null
                    ? analysisData.hypertension_cases.toLocaleString()
                    : "Data Unavailable"}
                </span>
              </div>
              <div className="kpi-card-subtitle">Enc: 1=Pos (2,443), 0=Neg (5,366)</div>
            </div>

            <div className="kpi-card-unified kpi-col-3 accent-purple">
              <div className="kpi-card-header">
                <span className="kpi-card-title">DIABETES CASES</span>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#8b5cf6" }}></span>
              </div>
              <div className="kpi-card-metric">
                <span className="kpi-metric-main">
                  {analysisData?.disease_breakdown?.diabetes?.available || analysisData?.diabetes_cases !== undefined
                    ? (analysisData.diabetes_cases?.toLocaleString() || "0")
                    : "Data Unavailable"}
                </span>
                {analysisData?.borderline_diabetes_cases > 0 && (
                  <span className="kpi-badge-supplement purple">
                    +{analysisData.borderline_diabetes_cases} Pre-Dia
                  </span>
                )}
              </div>
              <div className="kpi-card-subtitle">Enc: 1=Pos (1,070), 2=Neg (6,466), 3=Pre-Dia (270)</div>
            </div>

            <div className="kpi-card-unified kpi-col-3 accent-red">
              <div className="kpi-card-header">
                <span className="kpi-card-title">HEART DISEASE CASES</span>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#ef4444" }}></span>
              </div>
              <div className="kpi-card-metric">
                <span className="kpi-metric-main">
                  {analysisData?.disease_breakdown?.heart_disease?.available
                    ? analysisData.heart_disease_cases?.toLocaleString()
                    : analysisData?.heart_disease_cases !== undefined && analysisData?.heart_disease_cases !== null
                    ? analysisData.heart_disease_cases.toLocaleString()
                    : "Data Unavailable"}
                </span>
              </div>
              <div className="kpi-card-subtitle">Enc: 1=Pos (402), 2=Neg (7,371), Missing: 36</div>
            </div>
          </div>

          {/* Charts Row */}
          <div className="charts-container" style={{ marginTop: "24px" }}>
            <div className="chart-card">
              <h3>Disease Distribution</h3>
              <ResponsiveContainer width="100%" height={320}>
                <PieChart>
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    innerRadius={50}
                    label
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h3>Patient Health Statistics</h3>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="cases" fill="#0284c7" name="Patient Count" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Smart Insights Section */}
          <div style={{ marginTop: "25px", background: "white", padding: "24px", borderRadius: "14px", border: "1px solid #eaecf0" }}>
            <h3 style={{ margin: "0 0 16px", color: "#0f172a", fontSize: "18px" }}>💡 Smart Healthcare Insights (AI-Derived)</h3>
            {insights.length > 0 ? (
              insights.map((ins, idx) => (
                <div key={idx} className={`insight-box ${ins.type || "info"}`}>
                  <strong style={{ color: "#0f172a" }}>[{ins.category}] {ins.title}</strong>
                  <div style={{ color: "#475467", fontSize: "13px", marginTop: "4px" }}>{ins.observation}</div>
                </div>
              ))
            ) : (
              <p style={{ color: "#64748b" }}>Loading calculated insights from active dataset...</p>
            )}
          </div>
        </div>
      )}

      {/* ==============================================================
          2. UPLOAD DATASET PAGE
      ============================================================== */}
      {activePage === "upload" && (
        <div>
          <div className="dashboard-header">
            <h1>Upload Patient Dataset</h1>
            <p>Upload CSV or Excel files. NHANES datasets and custom patient health registries are supported.</p>
          </div>

          <div className="dashboard-section">
            <div className="section-number">⇪</div>
            <div className="section-content">
              <h2>Select Dataset File</h2>
              <p className="section-description">
                Files are processed and verified by Python on the Flask server before propagation across all dashboard views.
              </p>

              <div className="upload-area">
                <input type="file" accept=".csv, .xlsx, .xls" onChange={handleFileChange} />
                {selectedFile && (
                  <p className="selected-file">
                    Selected File: <strong>{selectedFile.name}</strong> ({(selectedFile.size / 1024).toFixed(1)} KB)
                  </p>
                )}

                <button className="primary-button" onClick={uploadDataset} disabled={loading || !selectedFile}>
                  {loading ? "Uploading & Analyzing..." : "Upload & Analyze Dataset"}
                </button>
              </div>

              {uploadResult && (
                <div className="success-box" style={{ marginTop: "20px" }}>
                  <h3>✓ Dataset Successfully Activated</h3>
                  <div className="result-grid">
                    <div>
                      <span>Total Patient Records</span>
                      <strong>{uploadResult.raw_patients?.toLocaleString()}</strong>
                    </div>
                    <div>
                      <span>Feature Columns</span>
                      <strong>{uploadResult.columns}</strong>
                    </div>
                    <div>
                      <span>Missing Cells</span>
                      <strong>{uploadResult.missing_total?.toLocaleString()} ({uploadResult.missing_pct}%)</strong>
                    </div>
                    <div>
                      <span>Duplicate Rows</span>
                      <strong>{uploadResult.duplicate_rows?.toLocaleString()}</strong>
                    </div>
                  </div>

                  <div style={{ marginTop: "16px" }}>
                    <strong>Detected Column Names:</strong>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "8px" }}>
                      {uploadResult.column_names?.map((col) => (
                        <span key={col} style={{ background: "#e0f2fe", color: "#0284c7", padding: "4px 10px", borderRadius: "12px", fontSize: "12px" }}>
                          {col}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ==============================================================
          3. DATA CLEANING PAGE
      ============================================================== */}
      {activePage === "cleaning" && (
        <div>
          <div className="dashboard-header">
            <h1>Data Cleaning & Quality Control</h1>
            <p>Detect data issues, impute missing values, eliminate duplicates, and isolate IQR outliers.</p>
          </div>

          <div className="dashboard-section">
            <div className="section-number cleaning-number">🧹</div>
            <div className="section-content">
              <h2>Configure Cleaning Operations</h2>
              <p className="section-description">
                All transformations run on an isolated copy of your dataset. The original dataset remains completely intact.
              </p>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px", marginBottom: "20px" }}>
                <div>
                  <label style={{ display: "block", fontSize: "12px", fontWeight: "700", color: "#344054", marginBottom: "6px" }}>
                    Missing Value Strategy
                  </label>
                  <select
                    value={missingStrategy}
                    onChange={(e) => setMissingStrategy(e.target.value)}
                    style={{ width: "100%", height: "40px", borderRadius: "8px", border: "1px solid #d0d5dd", padding: "0 10px" }}
                  >
                    <option value="mean">Fill with Mean (Numerical)</option>
                    <option value="median">Fill with Median (Numerical)</option>
                    <option value="mode">Fill with Mode (Categorical)</option>
                    <option value="drop">Drop Rows with Missing Values</option>
                  </select>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "10px", marginTop: "24px" }}>
                  <input
                    type="checkbox"
                    id="dupCheck"
                    checked={removeDuplicates}
                    onChange={(e) => setRemoveDuplicates(e.target.checked)}
                  />
                  <label htmlFor="dupCheck" style={{ fontSize: "13px", fontWeight: "600", color: "#344054" }}>
                    Remove Duplicate Rows
                  </label>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "10px", marginTop: "24px" }}>
                  <input
                    type="checkbox"
                    id="outlierCheck"
                    checked={filterOutliers}
                    onChange={(e) => setFilterOutliers(e.target.checked)}
                  />
                  <label htmlFor="outlierCheck" style={{ fontSize: "13px", fontWeight: "600", color: "#344054" }}>
                    Filter Outliers (IQR Method)
                  </label>
                </div>
              </div>

              <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
                <button className="primary-button" onClick={detectDataIssues} disabled={loading}>
                  🔍 Detect Data Issues
                </button>
                <button className="clean-button" onClick={cleanDataset} disabled={loading}>
                  {loading ? "Cleaning..." : "✨ Clean Dataset"}
                </button>
                <button
                  className="analysis-button"
                  onClick={() => setShowPreview(!showPreview)}
                  disabled={!cleaningResult && !analysisData}
                >
                  👁 Preview Cleaned Dataset
                </button>
                <button
                  className="analysis-button"
                  onClick={() => setShowComparison(!showComparison)}
                  disabled={!cleaningResult}
                >
                  ⚖ Compare Before & After
                </button>
                <button className="analysis-button" onClick={resetCleaning}>
                  ↺ Reset Cleaning
                </button>
                <a
                  href={`${API_BASE}/download-cleaned`}
                  download
                  className="primary-button"
                  style={{ textDecoration: "none", display: "inline-block", background: "#0f172a" }}
                >
                  ⬇ Download Cleaned CSV
                </a>
              </div>

              {/* Detected Issues Box */}
              {issuesData && (
                <div style={{ marginTop: "24px", background: "#fffbeb", border: "1px solid #fef3c7", padding: "18px", borderRadius: "10px" }}>
                  <h4 style={{ margin: "0 0 10px", color: "#b45309" }}>Data Quality Audit Results:</h4>
                  <p style={{ margin: "4px 0", fontSize: "13px" }}>• Total Missing Values: <strong>{issuesData.total_missing?.toLocaleString()}</strong></p>
                  <p style={{ margin: "4px 0", fontSize: "13px" }}>• Duplicate Rows: <strong>{issuesData.duplicate_rows?.toLocaleString()}</strong></p>
                  <p style={{ margin: "4px 0", fontSize: "13px" }}>• Columns with IQR Outliers: <strong>{issuesData.outlier_details?.length || 0}</strong></p>
                </div>
              )}

              {/* Side-by-Side Before & After Comparison */}
              {showComparison && cleaningResult && (
                <div style={{ marginTop: "24px", background: "#f8fafc", border: "1px solid #cbd5e1", padding: "20px", borderRadius: "12px" }}>
                  <h4 style={{ margin: "0 0 14px", color: "#0f172a" }}>⚖ Before & After Cleaning Comparison</h4>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "12px" }}>
                    <div className="detail-card">
                      <span>Total Patients</span>
                      <strong>{cleaningResult.raw_patients?.toLocaleString()} → {cleaningResult.cleaned_patients?.toLocaleString()}</strong>
                      <small style={{ color: "#ef4444" }}>-{cleaningResult.rows_removed} removed</small>
                    </div>
                    <div className="detail-card">
                      <span>Missing Cells</span>
                      <strong>{cleaningResult.missing_values_before?.toLocaleString()} → {cleaningResult.missing_values_after?.toLocaleString()}</strong>
                      <small style={{ color: "#10b981" }}>Imputed successfully</small>
                    </div>
                    <div className="detail-card">
                      <span>Duplicate Rows</span>
                      <strong>{cleaningResult.duplicate_rows} → 0</strong>
                      <small style={{ color: "#10b981" }}>Duplicates eliminated</small>
                    </div>
                    <div className="detail-card">
                      <span>Empty Rows</span>
                      <strong>{cleaningResult.empty_rows} → 0</strong>
                      <small style={{ color: "#10b981" }}>Purged</small>
                    </div>
                  </div>
                </div>
              )}

              {/* Cleaned Records Preview */}
              {showPreview && cleaningResult?.preview && (
                <div style={{ marginTop: "24px", background: "white", padding: "20px", borderRadius: "12px", border: "1px solid #eaecf0" }}>
                  <h4 style={{ margin: "0 0 12px", color: "#0f172a" }}>📋 Cleaned Records Preview (First 10 Rows)</h4>
                  <div style={{ overflowX: "auto" }}>
                    <table style={{ width: "100%", fontSize: "12px", borderCollapse: "collapse", background: "white" }}>
                      <thead>
                        <tr style={{ background: "#f1f5f9", textAlign: "left" }}>
                          {Object.keys(cleaningResult.preview[0] || {}).slice(0, 10).map((k) => (
                            <th key={k} style={{ padding: "8px 12px", border: "1px solid #e2e8f0" }}>{k}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {cleaningResult.preview.slice(0, 10).map((row, idx) => (
                          <tr key={idx} style={{ borderBottom: "1px solid #f8fafc" }}>
                            {Object.values(row).slice(0, 10).map((val, cIdx) => (
                              <td key={cIdx} style={{ padding: "8px 12px", border: "1px solid #f1f5f9" }}>
                                {val !== null ? String(val) : "—"}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Cleaning Result Report */}
              {cleaningResult && (
                <div className="cleaning-results" style={{ marginTop: "20px" }}>
                  <div className="cleaning-success">✓ Data Cleaning Completed Successfully</div>
                  <div className="cleaning-comparison">
                    <div className="comparison-card raw">
                      <span>Raw Patients</span>
                      <strong>{cleaningResult.raw_patients?.toLocaleString()}</strong>
                    </div>
                    <div className="arrow">→</div>
                    <div className="comparison-card cleaned">
                      <span>Cleaned Patients</span>
                      <strong>{cleaningResult.cleaned_patients?.toLocaleString()}</strong>
                    </div>
                    <div className="comparison-card removed">
                      <span>Rows Removed</span>
                      <strong>{cleaningResult.rows_removed?.toLocaleString()}</strong>
                    </div>
                  </div>

                  <div className="cleaning-grid" style={{ marginTop: "16px" }}>
                    <div className="detail-card">
                      <span>Duplicates Removed</span>
                      <strong>{cleaningResult.duplicate_rows}</strong>
                    </div>
                    <div className="detail-card">
                      <span>Missing Before</span>
                      <strong>{cleaningResult.missing_values_before?.toLocaleString()}</strong>
                    </div>
                    <div className="detail-card">
                      <span>Missing After</span>
                      <strong>{cleaningResult.missing_values_after?.toLocaleString()}</strong>
                    </div>
                  </div>

                  {cleaningResult.preview && (
                    <div style={{ marginTop: "20px" }}>
                      <h4>Cleaned Records Preview</h4>
                      <div style={{ overflowX: "auto" }}>
                        <table style={{ width: "100%", fontSize: "12px", borderCollapse: "collapse", background: "white" }}>
                          <thead>
                            <tr style={{ background: "#f1f5f9", textAlign: "left" }}>
                              {Object.keys(cleaningResult.preview[0] || {}).slice(0, 8).map((k) => (
                                <th key={k} style={{ padding: "8px 12px", border: "1px solid #e2e8f0" }}>{k}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {cleaningResult.preview.slice(0, 5).map((row, idx) => (
                              <tr key={idx}>
                                {Object.keys(row).slice(0, 8).map((k) => (
                                  <td key={k} style={{ padding: "8px 12px", border: "1px solid #e2e8f0" }}>{String(row[k])}</td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ==============================================================
          4. DATA ANALYSIS PAGE
      ============================================================== */}
      {activePage === "analysis" && (
        <div>
          <div className="dashboard-header">
            <h1>Data Analysis & Dynamic Visualizer</h1>
            <p>Compute descriptive statistics, feature correlations, and generate custom Plotly charts dynamically.</p>
          </div>

          {/* Dynamic Chart Generator Panel */}
          <div className="dashboard-section">
            <div className="section-number">📈</div>
            <div className="section-content">
              <h2>Dynamic Chart Builder</h2>
              <p className="section-description">Select features and visualization formats to inspect relationships in the dataset.</p>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px", marginBottom: "20px" }}>
                <div>
                  <label style={{ display: "block", fontSize: "12px", fontWeight: "700", marginBottom: "6px" }}>Chart Type</label>
                  <select
                    value={chartType}
                    onChange={(e) => setChartType(e.target.value)}
                    style={{ width: "100%", height: "40px", borderRadius: "8px", border: "1px solid #d0d5dd", padding: "0 10px" }}
                  >
                    <option value="Bar">Bar Chart</option>
                    <option value="Line">Line Chart</option>
                    <option value="Pie">Pie Chart</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "12px", fontWeight: "700", marginBottom: "6px" }}>X-Axis Feature</label>
                  <select
                    value={xAxisCol}
                    onChange={(e) => setXAxisCol(e.target.value)}
                    style={{ width: "100%", height: "40px", borderRadius: "8px", border: "1px solid #d0d5dd", padding: "0 10px" }}
                  >
                    {analysisData?.numeric_columns?.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "12px", fontWeight: "700", marginBottom: "6px" }}>Y-Axis Feature</label>
                  <select
                    value={yAxisCol}
                    onChange={(e) => setYAxisCol(e.target.value)}
                    style={{ width: "100%", height: "40px", borderRadius: "8px", border: "1px solid #d0d5dd", padding: "0 10px" }}
                  >
                    {analysisData?.numeric_columns?.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Chart Preview */}
              <div style={{ background: "white", padding: "20px", borderRadius: "12px", border: "1px solid #eaecf0", height: "350px" }}>
                <ResponsiveContainer width="100%" height="100%">
                  {chartType === "Bar" ? (
                    <BarChart data={barData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="cases" fill="#0284c7" />
                    </BarChart>
                  ) : chartType === "Line" ? (
                    <LineChart data={barData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="cases" stroke="#0284c7" strokeWidth={3} />
                    </LineChart>
                  ) : (
                    <PieChart>
                      <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                        {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  )}
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Descriptive Statistics Table */}
          {analysisData?.numeric_stats && (
            <div style={{ background: "white", padding: "24px", borderRadius: "14px", border: "1px solid #eaecf0", marginTop: "24px" }}>
              <h3 style={{ margin: "0 0 16px", color: "#0f172a" }}>Descriptive Numerical Statistics</h3>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", fontSize: "12px", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ background: "#f8fafc", textAlign: "left", color: "#475467" }}>
                      <th style={{ padding: "10px", borderBottom: "2px solid #e2e8f0" }}>Feature</th>
                      <th style={{ padding: "10px", borderBottom: "2px solid #e2e8f0" }}>Mean</th>
                      <th style={{ padding: "10px", borderBottom: "2px solid #e2e8f0" }}>Median</th>
                      <th style={{ padding: "10px", borderBottom: "2px solid #e2e8f0" }}>Std Dev</th>
                      <th style={{ padding: "10px", borderBottom: "2px solid #e2e8f0" }}>Min</th>
                      <th style={{ padding: "10px", borderBottom: "2px solid #e2e8f0" }}>Max</th>
                      <th style={{ padding: "10px", borderBottom: "2px solid #e2e8f0" }}>Variance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(analysisData.numeric_stats).slice(0, 10).map(([col, s]) => (
                      <tr key={col} style={{ borderBottom: "1px solid #f1f5f9" }}>
                        <td style={{ padding: "10px", fontWeight: "600", color: "#0f172a" }}>{col}</td>
                        <td style={{ padding: "10px" }}>{s.mean}</td>
                        <td style={{ padding: "10px" }}>{s.median}</td>
                        <td style={{ padding: "10px" }}>{s.std}</td>
                        <td style={{ padding: "10px" }}>{s.min}</td>
                        <td style={{ padding: "10px" }}>{s.max}</td>
                        <td style={{ padding: "10px" }}>{s.variance}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ==============================================================
          5. HEALTHCARE ANALYTICS (Filtered Visualizations)
      ============================================================== */}
      {activePage === "analytics" && (
        <div>
          <div className="dashboard-header">
            <h1>Healthcare Analytics & Interactive Cohort Slicers</h1>
            <p>Filter by age bracket, gender, chronic condition, and risk level. All visual components update dynamically.</p>
          </div>

          {/* Slicers Filter Bar */}
          <div style={{ background: "white", padding: "18px 24px", borderRadius: "12px", border: "1px solid #e2e8f0", marginBottom: "22px", display: "flex", gap: "16px", alignItems: "flex-end", flexWrap: "wrap" }}>
            <div style={{ flex: 1, minWidth: "140px" }}>
              <label style={{ fontSize: "11px", fontWeight: "700", color: "#64748b" }}>AGE BRACKET</label>
              <select value={filterAge} onChange={(e) => setFilterAge(e.target.value)} style={{ width: "100%", height: "38px", borderRadius: "8px", border: "1px solid #d0d5dd", marginTop: "4px", padding: "0 8px" }}>
                <option value="All">All Ages</option>
                <option value="< 30">&lt; 30</option>
                <option value="30-44">30 - 44</option>
                <option value="45-59">45 - 59</option>
                <option value="60-74">60 - 74</option>
                <option value="75+">75+</option>
              </select>
            </div>

            <div style={{ flex: 1, minWidth: "140px" }}>
              <label style={{ fontSize: "11px", fontWeight: "700", color: "#64748b" }}>GENDER</label>
              <select value={filterGender} onChange={(e) => setFilterGender(e.target.value)} style={{ width: "100%", height: "38px", borderRadius: "8px", border: "1px solid #d0d5dd", marginTop: "4px", padding: "0 8px" }}>
                <option value="All">All Genders</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
            </div>

            <div style={{ flex: 1, minWidth: "140px" }}>
              <label style={{ fontSize: "11px", fontWeight: "700", color: "#64748b" }}>CONDITION</label>
              <select value={filterDisease} onChange={(e) => setFilterDisease(e.target.value)} style={{ width: "100%", height: "38px", borderRadius: "8px", border: "1px solid #d0d5dd", marginTop: "4px", padding: "0 8px" }}>
                <option value="All">All Conditions</option>
                <option value="Diabetes">Diabetes</option>
                <option value="Heart Disease">Heart Disease</option>
                <option value="Hypertension">Hypertension</option>
              </select>
            </div>

            <div style={{ flex: 1, minWidth: "140px" }}>
              <label style={{ fontSize: "11px", fontWeight: "700", color: "#64748b" }}>HEALTH RISK</label>
              <select value={filterRisk} onChange={(e) => setFilterRisk(e.target.value)} style={{ width: "100%", height: "38px", borderRadius: "8px", border: "1px solid #d0d5dd", marginTop: "4px", padding: "0 8px" }}>
                <option value="All">All Risk Levels</option>
                <option value="Low Risk">Low Risk</option>
                <option value="Moderate Risk">Moderate Risk</option>
                <option value="High Risk">High Risk</option>
              </select>
            </div>

            <button onClick={resetFilters} style={{ height: "38px", padding: "0 18px", borderRadius: "8px", border: "1px solid #cbd5e1", background: "#f8fafc", fontWeight: "600", cursor: "pointer" }}>
              ↺ Reset Filters
            </button>
          </div>

          {/* Filtered KPIs */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-title">FILTERED COHORT</div>
              <div className="stat-value">{analysisData?.total_patients?.toLocaleString() || "—"}</div>
              <div className="stat-subtitle">Matching patients</div>
            </div>

            <div className="stat-card">
              <div className="stat-title">MEAN COHORT AGE</div>
              <div className="stat-value">{analysisData?.average_age || "—"} yrs</div>
              <div className="stat-subtitle">Demographic mean</div>
            </div>

            <div className="stat-card">
              <div className="stat-title">DIABETES CASES</div>
              <div className="stat-value">{analysisData?.diabetes_cases?.toLocaleString() || "—"}</div>
              <div className="stat-subtitle">Diagnosed in cohort</div>
            </div>

            <div className="stat-card">
              <div className="stat-title">HYPERTENSION CASES</div>
              <div className="stat-value">{analysisData?.hypertension_cases?.toLocaleString() || "—"}</div>
              <div className="stat-subtitle">Elevated blood pressure</div>
            </div>
          </div>

          {/* Clinical Charts */}
          <div className="charts-container" style={{ marginTop: "24px" }}>
            <div className="chart-card">
              <h3>Condition Prevalence (Donut)</h3>
              <ResponsiveContainer width="100%" height={320}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} innerRadius={55} label>
                    {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h3>Cohort Disease Burden</h3>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="cases" fill="#0284c7" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* ==============================================================
          6. DISEASE ANALYSIS PAGE
      ============================================================== */}
      {activePage === "disease" && (
        <div>
          <div className="dashboard-header">
            <h1>Epidemiological Disease Analysis</h1>
            <p>Condition-specific prevalence rates, age patterns, gender distributions, and clinical biomarker comparisons.</p>
          </div>

          {diseaseData?.disease_summaries?.length > 0 ? (
            diseaseData.disease_summaries.map((d) => {
              if (!d.available) {
                return (
                  <div key={d.disease} style={{ background: "white", padding: "20px 24px", borderRadius: "14px", border: "1px solid #eaecf0", borderLeft: "4px solid #94a3b8", marginBottom: "20px" }}>
                    <h3 style={{ margin: 0, color: "#64748b", fontSize: "18px" }}>
                      {d.disease} — <span style={{ color: "#ef4444" }}>Data Unavailable</span>
                    </h3>
                    <p style={{ margin: "4px 0 0", color: "#94a3b8", fontSize: "13px" }}>
                      The clinical biomarker column for {d.disease} is not present in the current dataset.
                    </p>
                  </div>
                );
              }

              return (
                <div key={d.disease} style={{ background: "white", padding: "24px", borderRadius: "14px", border: "1px solid #eaecf0", marginBottom: "22px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #f1f5f9", paddingBottom: "14px", marginBottom: "16px" }}>
                    <div>
                      <h3 style={{ margin: 0, color: "#0f172a", fontSize: "20px" }}>{d.disease}</h3>
                      <p style={{ margin: "4px 0 0", color: "#64748b", fontSize: "13px" }}>
                        Prevalence Rate: <strong>{d.prevalence_pct}%</strong> ({d.cases?.toLocaleString()} documented positive cases)
                      </p>
                    </div>
                    <span style={{ background: "#e0f2fe", color: "#0284c7", padding: "6px 14px", borderRadius: "16px", fontWeight: "700", fontSize: "13px" }}>
                      {d.cases?.toLocaleString()} Positive
                    </span>
                  </div>

                  {/* Clinical Breakdown Metrics */}
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "10px", marginBottom: "16px", background: "#f8fafc", padding: "12px", borderRadius: "8px" }}>
                    <div>
                      <div style={{ fontSize: "11px", color: "#64748b", fontWeight: "700" }}>CONFIRMED POSITIVE</div>
                      <div style={{ fontSize: "16px", fontWeight: "700", color: "#0f172a" }}>{d.cases?.toLocaleString()}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: "11px", color: "#64748b", fontWeight: "700" }}>CONFIRMED NEGATIVE</div>
                      <div style={{ fontSize: "16px", fontWeight: "700", color: "#10b981" }}>{d.negative_cases?.toLocaleString()}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: "11px", color: "#64748b", fontWeight: "700" }}>PRE-DIABETES (CAT 3)</div>
                      <div style={{ fontSize: "16px", fontWeight: "700", color: "#f59e0b" }}>{d.borderline_cases ? d.borderline_cases.toLocaleString() : "N/A"}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: "11px", color: "#64748b", fontWeight: "700" }}>EXCLUDED MISSING</div>
                      <div style={{ fontSize: "16px", fontWeight: "700", color: "#94a3b8" }} title="Missing values are strictly excluded and never treated as negative.">
                        {d.missing_cases?.toLocaleString()}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1.2fr", gap: "20px" }}>
                    <div>
                      <strong style={{ fontSize: "13px", color: "#344054" }}>Age Breakdown (Positive Cohort):</strong>
                      <div style={{ marginTop: "8px" }}>
                        {Object.entries(d.age_breakdown || {}).map(([bracket, cnt]) => (
                          <div key={bracket} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid #f8fafc", fontSize: "12px" }}>
                            <span style={{ color: "#64748b" }}>{bracket}</span>
                            <strong>{cnt} cases</strong>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <strong style={{ fontSize: "13px", color: "#344054" }}>Gender Distribution (Positive Cohort):</strong>
                      <div style={{ marginTop: "8px" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid #f8fafc", fontSize: "12px" }}>
                          <span style={{ color: "#64748b" }}>Male</span>
                          <strong>{d.gender_breakdown?.Male || 0} cases</strong>
                        </div>
                        <div style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid #f8fafc", fontSize: "12px" }}>
                          <span style={{ color: "#64748b" }}>Female</span>
                          <strong>{d.gender_breakdown?.Female || 0} cases</strong>
                        </div>
                      </div>
                    </div>

                    <div>
                      <strong style={{ fontSize: "13px", color: "#344054" }}>Risk Factor Differences (Mean Values):</strong>
                      <div style={{ marginTop: "8px" }}>
                        {Object.entries(d.risk_factors || {}).map(([rf, vals]) => (
                          <div key={rf} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid #f8fafc", fontSize: "12px" }}>
                            <span style={{ color: "#64748b", textTransform: "capitalize" }}>{rf.replace("_", " ")}</span>
                            <span style={{ color: "#ef4444", fontWeight: "600" }}>{vals.with_disease} (with)</span>
                            <span style={{ color: "#0284c7" }}>{vals.without_disease} (without)</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="dashboard-section">
              <p style={{ color: "#64748b" }}>No disease conditions mapped in current dataset.</p>
            </div>
          )}
        </div>
      )}

      {/* ==============================================================
          8. GENERATE REPORTS PAGE
      ============================================================== */}
      {activePage === "reports" && (
        <div>
          <div className="dashboard-header">
            <h1>Healthcare Intelligence Reporting & Export</h1>
            <p>Export executive PDF reports, clean CSV datasets, and analytical summaries.</p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "22px" }}>
            <div style={{ background: "white", padding: "28px", borderRadius: "14px", border: "1px solid #eaecf0" }}>
              <div style={{ fontSize: "32px", marginBottom: "12px" }}>📄</div>
              <h3 style={{ margin: "0 0 8px", color: "#0f172a" }}>Executive PDF Healthcare Report</h3>
              <p style={{ color: "#64748b", fontSize: "13px", lineHeight: "1.6", marginBottom: "20px" }}>
                Includes executive KPI scorecard, patient demographic distributions, AI smart healthcare insights, and clinical recommendations in a formatted document.
              </p>
              <a
                href={`${API_BASE}/export-pdf`}
                download="Healthcare_Intelligence_Report.pdf"
                className="primary-button"
                style={{ textDecoration: "none", display: "inline-block" }}
              >
                ⬇ Download Executive PDF Report
              </a>
            </div>

            <div style={{ background: "white", padding: "28px", borderRadius: "14px", border: "1px solid #eaecf0" }}>
              <div style={{ fontSize: "32px", marginBottom: "12px" }}>📊</div>
              <h3 style={{ margin: "0 0 8px", color: "#0f172a" }}>Cleaned Dataset (CSV)</h3>
              <p style={{ color: "#64748b", fontSize: "13px", lineHeight: "1.6", marginBottom: "20px" }}>
                Export the currently active dataset with all data imputation, duplicate row removals, and type corrections applied.
              </p>
              <a
                href={`${API_BASE}/download-cleaned`}
                download="cleaned_patient_data.csv"
                className="clean-button"
                style={{ textDecoration: "none", display: "inline-block" }}
              >
                ⬇ Download Cleaned CSV Dataset
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;