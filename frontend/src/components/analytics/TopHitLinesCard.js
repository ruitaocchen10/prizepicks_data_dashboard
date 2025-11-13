import React, { useState, useEffect } from "react";
import "./AnalyticsCard.css";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:5000";

function TopHitLinesCard() {
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

  // Fetch available states and date range
  useEffect(() => {
    fetch(`${API_URL}/api/analytics/states`)
      .then((res) => res.json())
      .then((data) => setAvailableStates(data.states || []))
      .catch((err) => console.error("Failed to fetch states:", err));

    fetch(`${API_URL}/api/analytics/date-range`)
      .then((res) => res.json())
      .then((data) => {
        setDateRange(data.date_range || {});
        setStartDate(data.date_range?.min_date || "");
        setEndDate(data.date_range?.max_date || "");
      })
      .catch((err) => console.error("Failed to fetch date range:", err));
  }, []);

  const fetchTopHitLines = () => {
    setLoading(true);
    setError(null);

    const params = new URLSearchParams({
      sort_by: sortBy,
      limit: limit,
    });

    if (state) params.append("state", state);
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);

    fetch(`${API_URL}/api/analytics/top-hit-lines?${params}`)
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
    fetchTopHitLines();
  }, [sortBy, state, startDate, endDate, limit]);

  return (
    <div className="analytics-card">
      <h2>🎯 Top Hit Player Props</h2>

      <div className="filters">
        <div className="filter-group">
          <label>Sort By:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="revenue">Net Revenue</option>
            <option value="count">Times Hit</option>
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

        <button className="fetch-button" onClick={fetchTopHitLines}>
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
                <th>Player</th>
                <th>Stat Type</th>
                <th>Line</th>
                <th>Times Hit</th>
                <th>Total Wagered</th>
                <th>Total Paid Out</th>
                <th>Net Revenue</th>
                <th>Hit Rate</th>
              </tr>
            </thead>
            <tbody>
              {results.map((prop, index) => (
                <tr key={index}>
                  <td>{index + 1}</td>
                  <td>{prop.player_name}</td>
                  <td>{prop.stat_type}</td>
                  <td>{prop.line_score}</td>
                  <td>{prop.times_hit}</td>
                  <td>${prop.total_wagered?.toFixed(2)}</td>
                  <td>${prop.total_paid_out?.toFixed(2)}</td>
                  <td
                    className={prop.net_revenue >= 0 ? "positive" : "negative"}
                  >
                    ${prop.net_revenue?.toFixed(2)}
                  </td>
                  <td>{prop.hit_rate?.toFixed(1)}%</td>
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

export default TopHitLinesCard;
