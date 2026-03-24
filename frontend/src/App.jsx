import { useState, useRef } from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import LiveMonitor from './pages/LiveMonitor'
import Dashboard from './pages/Dashboard'
import TuningLeaderboard from './pages/TuningLeaderboard'
import RiskHeatmap from './pages/RiskHeatmap'
import SystemHealth from './pages/SystemHealth'
import './App.css'

const API_BASE = 'http://localhost:3001'

function Sidebar() {
  return (
    <nav className="sidebar">
      <div className="sidebar-brand">
        <span className="brand-icon">⚛️</span>
        <div>
          <h1 className="brand-title">Q-Shield</h1>
          <p className="brand-sub">Quantum Fraud Detection</p>
        </div>
      </div>

      <div className="sidebar-nav">
        <NavLink to="/" end className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">🔴</span>
          <span>Live Monitor</span>
        </NavLink>
        <NavLink to="/dashboard" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">📊</span>
          <span>Dashboard</span>
        </NavLink>
        <NavLink to="/tuning" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">⚛️</span>
          <span>Adaptive Tuning</span>
        </NavLink>
        <NavLink to="/heatmap" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">🗺️</span>
          <span>Risk Heatmap</span>
        </NavLink>
        <NavLink to="/health" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">💓</span>
          <span>System Health</span>
        </NavLink>
      </div>

      <div className="sidebar-footer">
        <span className="footer-badge">v2.0</span>
        <span className="footer-text">Powered by Qiskit</span>
      </div>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <div className="app-layout">
        <div className="background-grid"></div>
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<LiveMonitor apiBase={API_BASE} />} />
            <Route path="/dashboard" element={<Dashboard apiBase={API_BASE} />} />
            <Route path="/tuning" element={<TuningLeaderboard apiBase={API_BASE} />} />
            <Route path="/heatmap" element={<RiskHeatmap apiBase={API_BASE} />} />
            <Route path="/health" element={<SystemHealth apiBase={API_BASE} />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
