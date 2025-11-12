import React, { useState, useEffect } from "react";
import "./App.css";
import Navbar from "./components/Navbar";
import PlayerCard from "./components/PlayerCard";
import BreakevenTable from "./components/BreakevenTable";

function App() {
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
      <div className="App">
        <Navbar />
        <div className="loading-container">
          <h1>Loading...</h1>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App">
        <Navbar />
        <div className="error-container">
          <h1>Error: {error}</h1>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <Navbar onRefresh={fetchData} />
      <div className="dashboard-container">
        <h1>PrizePicks EV Dashboard</h1>
        <BreakevenTable />

        <h2>+EV Opportunities ({evData.length} props)</h2>
        <div className="player-cards">
          {evData.map((prop, index) => (
            <PlayerCard key={index} propData={prop} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
