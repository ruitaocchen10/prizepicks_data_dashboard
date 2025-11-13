import React, { useState } from "react";
import "./AnalyticsCard.css";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:5000";

function UserSearchCard() {
  const [searchQuery, setSearchQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = () => {
    if (!searchQuery.trim()) {
      setError("Please enter a username or email");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    fetch(
      `${API_URL}/api/analytics/user-search?q=${encodeURIComponent(
        searchQuery
      )}`
    )
      .then((response) => {
        if (!response.ok) throw new Error("Failed to search user");
        return response.json();
      })
      .then((data) => {
        if (!data.found) {
          setError(data.message || "User not found");
        } else {
          setResult(data);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="analytics-card user-search-card">
      <h2>🔍 User Lookup</h2>

      <div className="search-container">
        <input
          type="text"
          className="search-input"
          placeholder="Enter username or email..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button className="fetch-button" onClick={handleSearch}>
          Search
        </button>
      </div>

      {loading && <p className="loading-text">Searching...</p>}
      {error && <p className="error-text">{error}</p>}

      {result && result.found && (
        <div className="user-card-container">
          {/* User Info Section */}
          <div className="user-info-section">
            <h3>{result.user.username}</h3>
            <div className="user-details">
              <p>
                <strong>Email:</strong> {result.user.email}
              </p>
              <p>
                <strong>Name:</strong> {result.user.first_name}{" "}
                {result.user.last_name}
              </p>
              <p>
                <strong>State:</strong> {result.user.state}
              </p>
              <p>
                <strong>Status:</strong>
                <span className={`status-badge ${result.user.account_status}`}>
                  {result.user.account_status}
                </span>
              </p>
              <p>
                <strong>Member Since:</strong>{" "}
                {new Date(result.user.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>

          {/* Wallet Section */}
          <div className="wallet-section">
            <h4>💰 Wallet</h4>
            <div className="wallet-stats">
              <div className="stat">
                <span className="stat-label">Current Balance:</span>
                <span className="stat-value">
                  ${result.wallet.current_balance?.toFixed(2)}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Total Deposited:</span>
                <span className="stat-value">
                  ${result.wallet.total_deposited?.toFixed(2)}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Total Withdrawn:</span>
                <span className="stat-value">
                  ${result.wallet.total_withdrawn?.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* Betting Performance Section */}
          <div className="performance-section">
            <h4>📊 Betting Performance</h4>
            <div className="performance-grid">
              <div className="perf-stat">
                <span className="perf-label">Total Entries:</span>
                <span className="perf-value">
                  {result.betting.total_entries}
                </span>
              </div>
              <div className="perf-stat">
                <span className="perf-label">Wins:</span>
                <span className="perf-value positive">
                  {result.betting.wins}
                </span>
              </div>
              <div className="perf-stat">
                <span className="perf-label">Losses:</span>
                <span className="perf-value negative">
                  {result.betting.losses}
                </span>
              </div>
              <div className="perf-stat">
                <span className="perf-label">Win Rate:</span>
                <span className="perf-value">
                  {result.betting.win_rate?.toFixed(1)}%
                </span>
              </div>
              <div className="perf-stat">
                <span className="perf-label">Total Wagered:</span>
                <span className="perf-value">
                  ${result.betting.total_wagered?.toFixed(2)}
                </span>
              </div>
              <div className="perf-stat">
                <span className="perf-label">Total Winnings:</span>
                <span className="perf-value">
                  ${result.betting.total_winnings?.toFixed(2)}
                </span>
              </div>
              <div className="perf-stat">
                <span className="perf-label">Net Profit:</span>
                <span
                  className={`perf-value ${
                    result.betting.net_profit >= 0 ? "positive" : "negative"
                  }`}
                >
                  ${result.betting.net_profit?.toFixed(2)}
                </span>
              </div>
              <div className="perf-stat">
                <span className="perf-label">ROI:</span>
                <span
                  className={`perf-value ${
                    result.betting.roi_percentage >= 0 ? "positive" : "negative"
                  }`}
                >
                  {result.betting.roi_percentage?.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserSearchCard;
