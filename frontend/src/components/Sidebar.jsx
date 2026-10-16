import React from "react";

function Sidebar({ activePage, setActivePage }) {
  const menuItems = [
    { id: "overview", label: "Dashboard Overview", icon: "▦" },
    { id: "upload", label: "Upload Dataset", icon: "⇪" },
    { id: "cleaning", label: "Data Cleaning", icon: "🧹" },
    { id: "analysis", label: "Data Analysis", icon: "📈" },
    { id: "analytics", label: "Healthcare Analytics", icon: "🏥" },
    { id: "disease", label: "Disease Analysis", icon: "🔬" },
    { id: "prediction", label: "Patient Prediction", icon: "✦" },
    { id: "reports", label: "Generate Reports", icon: "📄" }
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">+</div>
        <div>
          <h2>HealthPulse BI</h2>
          <p>Clinical Analytics Platform</p>
        </div>
      </div>

      <div className="menu-heading">POWER BI NAVIGATION</div>

      <div className="sidebar-menu">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={activePage === item.id ? "menu-item active" : "menu-item"}
            onClick={() => setActivePage(item.id)}
          >
            <span>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="model-status">
          <div className="online-dot"></div>
          <div>
            <strong>Python Model Online</strong>
            <small>Random Forest Classifier</small>
          </div>
        </div>
        <div className="api-status">Flask API Connected (Port 5000)</div>
      </div>
    </aside>
  );
}

export default Sidebar;