import React from "react";
import "./BreakevenTable.css";

function BreakevenTable() {
  const breakevenData = [
    { slipType: "2 Power", breakeven: "57.74%" },
    { slipType: "3 Power", breakeven: "58.84%" },
    { slipType: "3 Flex", breakeven: "59.8%" },
    { slipType: "4 Power", breakeven: "56.23%" },
    { slipType: "4 Flex", breakeven: "56.09%" },
    { slipType: "5 Flex", breakeven: "54.34%" },
    { slipType: "6 Flex", breakeven: "54.34%" },
  ];

  return (
    <div className="breakeven-container">
      <h2>PrizePicks Breakeven Rate</h2>
      <p className="breakeven-subtitle">
        Each pick must hit at this percentage or higher to be profitable
        long-term
      </p>

      <table className="breakeven-table">
        <thead>
          <tr>
            <th>Slip Type</th>
            <th>Breakeven %</th>
          </tr>
        </thead>
        <tbody>
          {breakevenData.map((row, index) => (
            <tr key={index}>
              <td className="slip-type">{row.slipType}</td>
              <td className="breakeven-percentage">{row.breakeven}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default BreakevenTable;
