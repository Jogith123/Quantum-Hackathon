import { useState } from 'react'
import TransactionFeed from '../components/TransactionFeed'
import '../components/Header.css'
import '../components/TransactionFeed.css'
import '../components/TransactionCard.css'

export default function LiveMonitor({ apiBase }) {
  const [status, setStatus] = useState('disconnected')
  const [transactions, setTransactions] = useState([])
  const [stats, setStats] = useState({ total: 0, fraud: 0, legit: 0 })
  const [error, setError] = useState(null)

  const handleConnect = async () => {
    setStatus('connecting')
    setError(null)
    try {
      const res = await fetch(`${apiBase}/api/connect`, { method: 'POST' })
      const data = await res.json()
      if (data.status === 'connected') setStatus('connected')
      else { setError(data.error || 'Connection failed'); setStatus('disconnected') }
    } catch { setError('Cannot reach server. Is server.js running?'); setStatus('disconnected') }
  }

  const handleScan = async () => {
    setStatus('scanning')
    setError(null)
    setTransactions([])
    setStats({ total: 0, fraud: 0, legit: 0 })
    try {
      const res = await fetch(`${apiBase}/api/scan`)
      const data = await res.json()
      if (data.error) { setError(data.error); setStatus('connected'); return }
      const results = data.results || []
      let fraudCount = 0, legitCount = 0
      for (let i = 0; i < results.length; i++) {
        await new Promise(r => setTimeout(r, 150))
        const tx = results[i]
        if (tx.quantum_analysis.label === 'FRAUD') fraudCount++
        else legitCount++
        setTransactions(prev => [tx, ...prev])
        setStats({ total: i + 1, fraud: fraudCount, legit: legitCount })
      }
      setStatus('connected')
    } catch { setError('Scan failed.'); setStatus('connected') }
  }

  const statusMap = {
    disconnected: ['Disconnected', 'status-offline'],
    connecting: ['Connecting...', 'status-pending'],
    connected: ['Bank Connected', 'status-online'],
    scanning: ['Scanning...', 'status-scanning'],
  }

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>🔴 Live Transaction Monitor</h1>
          <p>Real-time Plaid transactions scanned by QSVM engine</p>
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <div className={`status-badge ${statusMap[status][1]}`}>
            <span className="status-dot"></span>
            {statusMap[status][0]}
          </div>
          <div className="stat-cards">
            <div className="stat-card"><span className="stat-value">{stats.total}</span><span className="stat-label">Total</span></div>
            <div className="stat-card stat-fraud"><span className="stat-value">{stats.fraud}</span><span className="stat-label">Fraud</span></div>
            <div className="stat-card stat-legit"><span className="stat-value">{stats.legit}</span><span className="stat-label">Legit</span></div>
          </div>
          <button className="btn btn-secondary" onClick={handleConnect} disabled={status === 'connecting' || status === 'scanning'}>
            {status === 'connecting' ? '⏳ Connecting...' : '🔗 Connect'}
          </button>
          <button className="btn btn-primary" onClick={handleScan} disabled={status !== 'connected'}>
            {status === 'scanning' ? '⚛️ Scanning...' : '⚡ Quantum Scan'}
          </button>
        </div>
      </div>
      {error && <div className="error-box">{error}</div>}
      <TransactionFeed transactions={transactions} status={status} />
    </div>
  )
}
