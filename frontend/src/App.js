import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";
import Navbar from "./components/Navbar";
import EVDashboard from "./pages/EVdashboard.js";
import UserAnalytics from "./pages/UserAnalytics.js";

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/" element={<EVDashboard />} />
          <Route path="/analytics" element={<UserAnalytics />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
