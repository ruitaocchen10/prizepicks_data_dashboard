import React from "react";
import { Link, useLocation } from "react-router-dom";
import "./Navbar.css";

function Navbar({ onRefresh }) {
  const location = useLocation();

  // Determine if reload button should be disabled
  const isDisabled = location.pathname !== "/";

  const handleRefresh = () => {
    if (!isDisabled && onRefresh) {
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
          <button
            className={`reload-button ${isDisabled ? "disabled" : ""}`}
            onClick={handleRefresh}
            disabled={isDisabled}
          >
            Reload
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
