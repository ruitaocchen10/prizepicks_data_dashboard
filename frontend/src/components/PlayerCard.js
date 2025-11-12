import React from "react";
import "./PlayerCard.css";

function PlayerCard({ propData }) {
  // Extract data from the prop
  const { player, game, prizepicks, ev_analysis } = propData;

  // If no EV analysis, show error state
  if (ev_analysis.status !== "calculated") {
    return (
      <div className="player-card error">
        <h3>{player}</h3>
        <p className="error-message">{ev_analysis.message}</p>
      </div>
    );
  }

  // Extract EV data
  const {
    better_side,
    implied_probability,
    risk_color,
    risk_label,
    edge_over_breakeven,
    bookmaker_used,
    reference_line,
  } = ev_analysis;

  return (
    <div
      className="player-card"
      style={{ borderLeft: `5px solid ${risk_color}` }}
    >
      {/* Header */}
      <div className="card-header">
        <h3 className="player-name">{player}</h3>
        <span className="team-badge">{prizepicks.team}</span>
      </div>

      {/* Game Info */}
      <p className="game-info">{game}</p>

      {/* Main Prop Display */}
      <div className="prop-display">
        <span className="prop-side">{better_side.toUpperCase()}</span>
        <span className="prop-line">{prizepicks.line} TDs</span>
      </div>

      {/* Probability Display */}
      <div className="probability-section">
        <div
          className="probability-circle"
          style={{ backgroundColor: risk_color }}
        >
          <span className="probability-number">{implied_probability}%</span>
        </div>
        <div className="probability-details">
          <p className="risk-label">{risk_label}</p>
          <p className="edge-label">
            {edge_over_breakeven > 0 ? "+" : ""}
            {edge_over_breakeven.toFixed(1)}% vs breakeven
          </p>
        </div>
      </div>

      {/* Reference Info */}
      <div className="reference-info">
        <p className="reference-line">
          {bookmaker_used}: {reference_line} TDs
        </p>
      </div>
    </div>
  );
}

export default PlayerCard;
