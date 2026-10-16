import { useState } from "react";

import Sidebar from "./components/Sidebar";
import Dashboard from "./components/Dashboard";
import Prediction from "./components/Prediction";

import "./App.css";

function App() {
  const [activePage, setActivePage] = useState("overview");

  return (
    <div className="app">
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      <main className="main-content">
        {activePage === "prediction" ? (
          <Prediction />
        ) : (
          <Dashboard activePage={activePage} setActivePage={setActivePage} />
        )}
      </main>
    </div>
  );
}

export default App;