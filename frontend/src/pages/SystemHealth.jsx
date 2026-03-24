import { useState, useEffect, useRef } from 'react'
import './SystemHealth.css'

export default function SystemHealth({ apiBase }) {
  const [health, setHealth] = useState(null)
  const [plaidStatus, setPlaidStatus] = useState('disconnected')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [uptime, setUptime] = useState(0)
  const startTime = useRef(Date.now())
  const intervalRef = useRef(null)

  useEffect(() => {
    fetchHealth()
    intervalRef.current = setInterval(() => {
      setUptime(Math.floor((Date.now() - startTime.current) / 1000))
    }, 1000)
    // Auto-refresh health every 10s
    const healthInterval = setInterval(fetchHealth, 10000)
    return () => {
      clearInterval(intervalRef.current)
      clearInterval(healthInterval)
    }
  }, [])

  const fetchHealth = async () => {
    try {
      const res = await fetch(`${apiBase}/api/health`)
      const data = await res.json()
      setHealth(data)
      setLoading(false)
      setError(null)
    } catch {
      setError('Cannot connect to backend')
      setLoading(false)
    }
  }

  const handlePlaidConnect = async () => {
    setPlaidStatus('connecting')
    try {
      const res = await fetch(`${apiBase}/api/connect`, { method: 'POST' })
      const data = await res.json()
      if (data.status === 'connected') setPlaidStatus('connected')
      else setPlaidStatus('error')
    } catch {
      setPlaidStatus('error')
    }
  }

  const formatUptime = (s) => {
    const h = Math.floor(s / 3600)
    const m = Math.floor((s % 3600) / 60)
    const sec = s % 60
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
  }

  if (loading) return <div className="loading-spinner">⏳ Checking system health...</div>

  const isOnline = health && !error

  return (
    <div>
      <div className="page-header">
        <h1>💓 System Health & Status</h1>
        <p>Real-time monitoring of Q-Shield infrastructure</p>
      </div>

      {/* Status Grid */}
      <div className="grid-3" style={{ marginBottom: 16 }}>
        {/* API Status */}
        <div className={`health-card ${isOnline ? 'hc-online' : 'hc-offline'}`}>
          <div className="hc-icon">{isOnline ? '🟢' : '🔴'}</div>
          <div className="hc-title">FastAPI Backend</div>
          <div className="hc-status">{isOnline ? 'Online' : 'Offline'}</div>
          <div className="hc-detail mono">{isOnline ? 'http://localhost:8000' : error}</div>
        </div>

        {/* Models Status */}
        <div className={`health-card ${health?.models_loaded ? 'hc-online' : 'hc-warning'}`}>
          <div className="hc-icon">{health?.models_loaded ? '🧠' : '⚠️'}</div>
          <div className="hc-title">QSVM Models</div>
          <div className="hc-status">{health?.models_loaded ? 'Loaded' : 'Not Loaded'}</div>
          <div className="hc-detail mono">
            {health?.models_loaded
              ? `${health.training_samples || '?'} training samples`
              : 'Run python main.py'}
          </div>
        </div>

        {/* Plaid Status */}
        <div className={`health-card ${plaidStatus === 'connected' ? 'hc-online' : 'hc-neutral'}`}>
          <div className="hc-icon">
            {plaidStatus === 'connected' ? '🏦' : plaidStatus === 'connecting' ? '⏳' : '🔗'}
          </div>
          <div className="hc-title">Plaid Sandbox</div>
          <div className="hc-status">
            {plaidStatus === 'connected' ? 'Connected' :
             plaidStatus === 'connecting' ? 'Connecting...' :
             plaidStatus === 'error' ? 'Failed' : 'Disconnected'}
          </div>
          <button
            className="btn btn-secondary hc-btn"
            onClick={handlePlaidConnect}
            disabled={plaidStatus === 'connecting' || plaidStatus === 'connected'}
          >
            {plaidStatus === 'connected' ? '✅ Connected' : '🔗 Connect'}
          </button>
        </div>
      </div>

      {/* Uptime + Details */}
      <div className="grid-2">
        <div className="card">
          <div className="card-title">Session Uptime</div>
          <div className="uptime-display mono">{formatUptime(uptime)}</div>
          <div className="uptime-sub">Time since dashboard opened</div>
        </div>

        <div className="card">
          <div className="card-title">System Details</div>
          <div className="detail-rows">
            <div className="detail-row">
              <span className="dr-label">API Version</span>
              <span className="dr-value mono">{health?.version || '2.0.0'}</span>
            </div>
            <div className="detail-row">
              <span className="dr-label">Quantum Engine</span>
              <span className="dr-value mono">Qiskit 2.x + Aer</span>
            </div>
            <div className="detail-row">
              <span className="dr-label">Feature Map</span>
              <span className="dr-value mono">ZZFeatureMap (4 qubits)</span>
            </div>
            <div className="detail-row">
              <span className="dr-label">Model Type</span>
              <span className="dr-value mono">SVC (precomputed kernel)</span>
            </div>
            <div className="detail-row">
              <span className="dr-label">QSVM Ready</span>
              <span className={`dr-value mono ${health?.qsvm_ready ? 'text-green' : 'text-red'}`}>
                {health?.qsvm_ready ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Architecture */}
      <div className="card arch-card" style={{ marginTop: 16 }}>
        <div className="card-title">System Architecture</div>
        <div className="arch-flow">
          <div className="arch-node arch-plaid">
            <span>🏦</span>
            <span>Plaid API</span>
          </div>
          <div className="arch-arrow">→</div>
          <div className="arch-node arch-express">
            <span>📡</span>
            <span>Express Proxy</span>
          </div>
          <div className="arch-arrow">→</div>
          <div className="arch-node arch-fastapi">
            <span>⚡</span>
            <span>FastAPI</span>
          </div>
          <div className="arch-arrow">→</div>
          <div className="arch-node arch-quantum">
            <span>⚛️</span>
            <span>QSVM Engine</span>
          </div>
          <div className="arch-arrow">→</div>
          <div className="arch-node arch-react">
            <span>💻</span>
            <span>React Dashboard</span>
          </div>
        </div>
      </div>
    </div>
  )
}
