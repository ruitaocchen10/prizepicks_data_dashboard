import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";
import Navbar from "./components/Navbar";
import EVDashboard from "./pages/EVdashboard.js";
import UserAnalytics from "./pages/UserAnalytics.js";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:5000";

function App() {
  const handleRefresh = () => {
    console.log("🔄 Refresh button clicked - calling backend API...");

    // Call the backend refresh endpoint
    fetch(`${API_URL}/api/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Refresh failed");
        }
        return response.json();
      })
      .then((data) => {
        console.log("✅ Refresh successful:", data);
        alert(`Data refreshed successfully! ${data.prop_count} props updated.`);
        // Reload the page to show new data
        window.location.reload();
      })
      .catch((error) => {
        console.error("❌ Refresh failed:", error);
        alert("Failed to refresh data. Check console for details.");
      });
  };

  return (
    <BrowserRouter>
      <div className="App">
        <Navbar onRefresh={handleRefresh} />
        <Routes>
          <Route path="/" element={<EVDashboard />} />
          <Route path="/analytics" element={<UserAnalytics />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
