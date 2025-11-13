import React from "react";
import "./PlayerCard.css";

function PlayerCard({ propData }) {
  // Determine if over or under
  const isOver = propData.ev_analysis.better_side === "over";

  // Get the implied probability (chance of hitting)
  const impliedProbability = propData.ev_analysis.implied_probability;
  const evPercentage = `${impliedProbability.toFixed(2)}%`;

  // Get EV value
  const evValue = propData.ev_analysis.edge_over_breakeven;

  // Determine EV class based on risk level or edge
  const getEvClass = () => {
    if (evValue > 3) return ""; // Positive EV (green)
    if (evValue > 0) return "risky"; // Low positive (orange)
    return "negative"; // Negative (red)
  };

  // Get bookmaker used
  const bookmaker = propData.ev_analysis.bookmaker_used;

  return (
    <div className="player-card">
      {/* Team Badge */}
      <div className="team-badge">{propData.prizepicks.team}</div>

      {/* Player Name */}
      <h3 className="player-name">{propData.player}</h3>

      {/* Matchup */}
      <p className="matchup-info">{propData.game}</p>

      {/* Prop Line */}
      <div className="prop-line-container">
        <div className="prop-line">
          <span className={isOver ? "arrow-up" : "arrow-down"}>
            {isOver ? "↑" : "↓"}
          </span>
          <span className={`prop-direction ${isOver ? "over" : "under"}`}>
            {isOver ? "Over" : "Under"} {propData.prizepicks.line} TDs
            <span className="prop-source">{bookmaker}</span>
          </span>
        </div>
      </div>

      {/* EV Display */}
      <div className={`ev-display ${getEvClass()}`}>
        <div className="ev-percentage">{impliedProbability}%</div>
        <div className="ev-label">{getEvClass()}</div>
        <div className="ev-description">
          {evValue > 0 ? "+" : ""}
          {evValue.toFixed(1)}% vs breakeven
        </div>
      </div>
    </div>
  );
}

export default PlayerCard;
