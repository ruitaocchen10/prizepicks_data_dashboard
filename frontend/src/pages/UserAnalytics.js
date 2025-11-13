import React from "react";
import TopWinnersCard from "../components/analytics/TopWinnersCard";
import TopHitLinesCard from "../components/analytics/TopHitLinesCard";
import UserSearchCard from "../components/analytics/UserSearchCard";
import "./UserAnalytics.css";

function UserAnalytics() {
  return (
    <div className="user-analytics-container">
      <h1>User Analytics Dashboard</h1>
      <p className="subtitle">
        Analyze betting patterns, top performers, and user data
      </p>

      <div className="analytics-cards-grid">
        <TopWinnersCard />
        <TopHitLinesCard />
      </div>
      <div>
        <UserSearchCard />
      </div>

      {/* Future: Natural Language Query section will go here */}
    </div>
  );
}

export default UserAnalytics;
