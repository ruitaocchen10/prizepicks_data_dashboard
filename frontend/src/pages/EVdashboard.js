import React, { useState, useEffect } from "react";
import PlayerCard from "../components/PlayerCard";
import BreakevenTable from "../components/BreakevenTable";

function EVDashboard() {
  const [evData, setEvData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Function to fetch data
  const fetchData = () => {
    setLoading(true);
    setError(null);

    fetch("http://127.0.0.1:5000/api/ev-data")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load data");
        }
        return response.json();
      })
      .then((data) => {
        setEvData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  // Load data when component mounts
  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <h1>Loading...</h1>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h1>Error: {error}</h1>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div>
        <h2>+EV Opportunities ({evData.length} props)</h2>
        <div className="player-cards">
          {evData.map((prop, index) => (
            <PlayerCard key={index} propData={prop} />
          ))}
        </div>
      </div>
      <BreakevenTable />
    </div>
  );
}

export default EVDashboard;
