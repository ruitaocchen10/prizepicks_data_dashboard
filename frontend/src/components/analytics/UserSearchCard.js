import React, { useState } from "react";
import "./AnalyticsCard.css";

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
      `http://127.0.0.1:5000/api/analytics/user-search?q=${encodeURIComponent(
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

          {/* Financial Stats */}
          <div className="financial-stats">
            <h4>💰 Financial Stats</h4>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-label">Current Balance</span>
                <span className="stat-value">
                  ${result.user.current_balance?.toFixed(2)}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Total Deposits</span>
                <span className="stat-value">
                  ${result.user.total_deposits?.toFixed(2)}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Total Wagered</span>
                <span className="stat-value">
                  ${result.user.total_wagered?.toFixed(2)}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Total Winnings</span>
                <span className="stat-value">
                  ${result.user.total_winnings?.toFixed(2)}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Net Profit</span>
                <span
                  className={`stat-value ${
                    result.user.net_profit >= 0 ? "positive" : "negative"
                  }`}
                >
                  ${result.user.net_profit?.toFixed(2)}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">ROI</span>
                <span
                  className={`stat-value ${
                    result.user.roi_percentage >= 0 ? "positive" : "negative"
                  }`}
                >
                  {result.user.roi_percentage?.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* Entry Stats */}
          <div className="entry-stats">
            <h4>🎲 Betting Stats</h4>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-label">Total Entries</span>
                <span className="stat-value">
                  {result.entry_stats.total_entries}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Wins</span>
                <span className="stat-value positive">
                  {result.entry_stats.winning_entries}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Losses</span>
                <span className="stat-value negative">
                  {result.entry_stats.losing_entries}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Pending</span>
                <span className="stat-value">
                  {result.entry_stats.pending_entries}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Win Rate</span>
                <span className="stat-value">
                  {result.entry_stats.win_rate_percentage}%
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Avg Bet Size</span>
                <span className="stat-value">
                  ${result.entry_stats.avg_bet_size?.toFixed(2)}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Biggest Win</span>
                <span className="stat-value positive">
                  ${result.entry_stats.biggest_win?.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* Most Picked Players */}
          {result.most_picked_players &&
            result.most_picked_players.length > 0 && (
              <div className="most-picked-section">
                <h4>⭐ Most Picked Players</h4>
                <table className="small-table">
                  <thead>
                    <tr>
                      <th>Player</th>
                      <th>Position</th>
                      <th>Team</th>
                      <th>Times Picked</th>
                      <th>Hit Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.most_picked_players.map((player, index) => (
                      <tr key={index}>
                        <td>{player.player_name}</td>
                        <td>{player.position}</td>
                        <td>{player.team}</td>
                        <td>{player.times_picked}</td>
                        <td>{player.hit_rate_percentage}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

          {/* Recent Entries */}
          {result.recent_entries && result.recent_entries.length > 0 && (
            <div className="recent-entries-section">
              <h4>📊 Recent Entries</h4>
              {result.recent_entries.slice(0, 5).map((entry) => (
                <div key={entry.entry_id} className="entry-item">
                  <div className="entry-header">
                    <span className={`status-badge ${entry.status}`}>
                      {entry.status}
                    </span>
                    <span className="entry-type">{entry.entry_type}</span>
                    <span className="entry-date">
                      {new Date(entry.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="entry-details">
                    <span>Wagered: ${entry.entry_amount?.toFixed(2)}</span>
                    {entry.status === "won" && (
                      <span className="positive">
                        Won: ${entry.actual_payout?.toFixed(2)}
                      </span>
                    )}
                    {entry.status === "lost" && (
                      <span className="negative">Lost</span>
                    )}
                  </div>
                  {entry.picks && entry.picks.length > 0 && (
                    <div className="picks-list">
                      {entry.picks.map((pick, idx) => (
                        <div key={idx} className="pick-item">
                          <span className={`pick-result ${pick.result}`}>
                            {pick.result === "hit"
                              ? "✓"
                              : pick.result === "miss"
                              ? "✗"
                              : "○"}
                          </span>
                          {pick.player_name} {pick.selection.toUpperCase()}{" "}
                          {pick.line} {pick.stat_type}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default UserSearchCard;
