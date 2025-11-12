import React from "react";
import "./BreakevenTable.css";

function BreakevenTable() {
  const breakevenRates = [
    { slip: "2 Power", rate: 57.74, american: -137, color: "#ff6b6b" },
    { slip: "3 Power", rate: 58.48, american: -141, color: "#ff8787" },
    { slip: "3 Flex", rate: 59.8, american: -149, color: "#ffa07a" },
    { slip: "4 Power", rate: 56.23, american: -128, color: "#98d8c8" },
    { slip: "4 Flex", rate: 56.89, american: -132, color: "#a8e6cf" },
    { slip: "5 Flex", rate: 54.34, american: -119, color: "#7bed9f" },
    { slip: "6 Flex", rate: 54.34, american: -119, color: "#2ed573" },
  ];

  return (
    <div className="breakeven-container">
      <h2 className="breakeven-title">PrizePicks Breakeven Rates</h2>
      <p className="breakeven-subtitle">
        Each pick must hit at this percentage or higher to be profitable
        long-term
      </p>

      <div className="breakeven-table">
        <div className="table-header">
          <div className="header-cell">Slip Type</div>
          <div className="header-cell">Breakeven %</div>
          <div className="header-cell">American Odds</div>
        </div>

        {breakevenRates.map((item, index) => (
          <div
            key={index}
            className="table-row"
            style={{ borderLeft: `4px solid ${item.color}` }}
          >
            <div className="table-cell slip-type">{item.slip}</div>
            <div className="table-cell rate">
              <span className="rate-number">{item.rate}%</span>
            </div>
            <div className="table-cell american">{item.american}</div>
          </div>
        ))}
      </div>

      <div className="breakeven-footer">
        <p className="footer-note">
          💡 <strong>Tip:</strong> Look for props with probabilities above these
          thresholds!
        </p>
      </div>
    </div>
  );
}

export default BreakevenTable;
