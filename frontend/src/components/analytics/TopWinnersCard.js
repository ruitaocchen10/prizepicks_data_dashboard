import React, { useState, useEffect } from "react";
import "./AnalyticsCard.css";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:5000";

function TopWinnersCard() {
  const [sortBy, setSortBy] = useState("revenue");
  const [state, setState] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [limit, setLimit] = useState(10);

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableStates, setAvailableStates] = useState([]);
  const [dateRange, setDateRange] = useState({ min_date: "", max_date: "" });

  // Fetch available states for dropdown
  useEffect(() => {
    fetch(`${API_URL}/api/analytics/states`)
      .then((res) => res.json())
      .then((data) => setAvailableStates(data.states || []))
      .catch((err) => console.error("Failed to fetch states:", err));

    // Fetch date range for date pickers
    fetch(`${API_URL}/api/analytics/date-range`)
      .then((res) => res.json())
      .then((data) => {
        setDateRange(data.date_range || {});
        setStartDate(data.date_range?.min_date || "");
        setEndDate(data.date_range?.max_date || "");
      })
      .catch((err) => console.error("Failed to fetch date range:", err));
  }, []);

  const fetchTopWinners = () => {
    setLoading(true);
    setError(null);

    const params = new URLSearchParams({
      sort_by: sortBy,
      limit: limit,
    });

    if (state) params.append("state", state);
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);

    fetch(`${API_URL}/api/analytics/top-winners?${params}`)
      .then((response) => {
        if (!response.ok) throw new Error("Failed to fetch data");
        return response.json();
      })
      .then((data) => {
        setResults(data.results || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  // Fetch on mount and when filters change
  useEffect(() => {
    fetchTopWinners();
  }, [sortBy, state, startDate, endDate, limit]);

  return (
    <div className="analytics-card">
      <h2>🏆 Top Winners</h2>

      <div className="filters">
        <div className="filter-group">
          <label>Sort By:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="revenue">Net Profit</option>
            <option value="count">Number of Wins</option>
          </select>
        </div>

        <div className="filter-group">
          <label>State:</label>
          <select value={state} onChange={(e) => setState(e.target.value)}>
            <option value="">All States</option>
            {availableStates.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Start Date:</label>
          <input
            type="date"
            value={startDate}
            min={dateRange.min_date}
            max={dateRange.max_date}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <label>End Date:</label>
          <input
            type="date"
            value={endDate}
            min={dateRange.min_date}
            max={dateRange.max_date}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <label>Limit:</label>
          <input
            type="number"
            min="1"
            max="100"
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value))}
          />
        </div>

        <button className="fetch-button" onClick={fetchTopWinners}>
          Refresh
        </button>
      </div>

      {loading && <p className="loading-text">Loading...</p>}
      {error && <p className="error-text">Error: {error}</p>}

      {!loading && !error && results.length > 0 && (
        <div className="results-table-container">
          <table className="results-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Username</th>
                <th>Email</th>
                <th>State</th>
                <th>Wins</th>
                <th>Total Wagered</th>
                <th>Total Won</th>
                <th>Net Profit</th>
                <th>ROI %</th>
              </tr>
            </thead>
            <tbody>
              {results.map((user, index) => (
                <tr key={user.user_id}>
                  <td>{index + 1}</td>
                  <td>{user.username}</td>
                  <td>{user.email}</td>
                  <td>{user.state}</td>
                  <td>{user.wins}</td>
                  <td>${user.total_wagered?.toFixed(2)}</td>
                  <td>${user.total_winnings?.toFixed(2)}</td>
                  <td
                    className={user.net_profit >= 0 ? "positive" : "negative"}
                  >
                    ${user.net_profit?.toFixed(2)}
                  </td>
                  <td
                    className={
                      user.roi_percentage >= 0 ? "positive" : "negative"
                    }
                  >
                    {user.roi_percentage?.toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && !error && results.length === 0 && (
        <p className="no-results">No results found</p>
      )}
    </div>
  );
}

export default TopWinnersCard;
