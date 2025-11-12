import React from "react";
import { Link, useLocation } from "react-router-dom";
import "./Navbar.css";

function Navbar({ onRefresh }) {
  const location = useLocation();

  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh();
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h1>PrizePicks Dashboard</h1>
      </div>

      <div className="navbar-links">
        <Link
          to="/"
          className={`nav-link ${location.pathname === "/" ? "active" : ""}`}
        >
          EV Analysis
        </Link>
        <Link
          to="/analytics"
          className={`nav-link ${
            location.pathname === "/analytics" ? "active" : ""
          }`}
        >
          User Analytics
        </Link>
      </div>

      {location.pathname === "/" && (
        <button className="refresh-button" onClick={handleRefresh}>
          Refresh Data
        </button>
      )}
    </nav>
  );
}

export default Navbar;
