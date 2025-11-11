import React from "react";
import "./App.css";
import Navbar from "./components/Navbar";
import PlayerCard from "./components/PlayerCard";
import BreakevenTable from "./components/BreakevenTable";

function App() {
  return (
    <div className="App">
      <Navbar />
      <div className="dashboard-container">
        <h1>PrizePicks EV Dashboard</h1>
        <BreakevenTable />
        <div className="player-cards">
          <PlayerCard />
          <PlayerCard />
          <PlayerCard />
        </div>
      </div>
    </div>
  );
}

export default App;
