import React, { useState } from "react";
import "./Navbar.css";

function Navbar({ onRefresh }) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshMessage, setRefreshMessage] = useState("");

  const handleRefresh = async () => {
    console.log(
      "\n🔄 ==================== REFRESH STARTED ===================="
    );
    console.log("⏰ Time:", new Date().toLocaleTimeString());

    setIsRefreshing(true);
    setRefreshMessage("Refreshing data...");

    try {
      console.log("📡 Sending POST request to /api/refresh...");

      const response = await fetch("http://127.0.0.1:5000/api/refresh", {
        method: "POST",
      });

      console.log(
        "📨 Response received:",
        response.status,
        response.statusText
      );

      if (!response.ok) {
        throw new Error("Refresh failed");
      }

      const result = await response.json();
      console.log("✅ Refresh successful!");
      console.log("📊 Result:", result);

      setRefreshMessage(`✓ Success! Found ${result.prop_count} props`);

      // Call the parent's refresh function to reload data
      console.log("🔄 Calling onRefresh to reload data in App...");
      if (onRefresh) {
        onRefresh();
      }

      console.log("✅ Data reloaded successfully");

      // Clear success message after 3 seconds
      setTimeout(() => {
        setRefreshMessage("");
      }, 3000);
    } catch (error) {
      console.error("❌ Refresh failed!");
      console.error("Error:", error);
      setRefreshMessage("✗ Refresh failed");
      setTimeout(() => {
        setRefreshMessage("");
      }, 3000);
    } finally {
      setIsRefreshing(false);
      console.log(
        "🏁 ==================== REFRESH COMPLETE ====================\n"
      );
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-left">
          <h1 className="navbar-logo">🏈 PrizePicks EV Finder</h1>
        </div>

        <div className="navbar-center">
          <button
            className={`nav-link ${
              window.location.pathname === "/" ? "active" : ""
            }`}
          >
            EV Dashboard
          </button>
          <button className="nav-link disabled" disabled>
            User Data (Coming Soon)
          </button>
        </div>

        <div className="navbar-right">
          <button
            className={`refresh-btn ${isRefreshing ? "refreshing" : ""}`}
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            {isRefreshing ? "⟳ Refreshing..." : "↻ Refresh Data"}
          </button>
          {refreshMessage && (
            <span
              className={`refresh-message ${
                refreshMessage.includes("✓") ? "success" : "error"
              }`}
            >
              {refreshMessage}
            </span>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
