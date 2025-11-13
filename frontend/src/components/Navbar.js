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
      <div className="navbar-content">
        <div className="navbar-brand">
          <h1>PrizePicks Analytics</h1>
        </div>

        <div className="navbar-center">
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
          {location.pathname === "/" && (
            <button className="reload-button" onClick={handleRefresh}>
              Reload
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
