import './Header.css'

function Header({ status, stats, error, onConnect, onScan }) {
  const statusLabel = {
    disconnected: 'Disconnected',
    connecting: 'Connecting...',
    connected: 'Bank Connected',
    scanning: 'Scanning...',
  }

  const statusClass = {
    disconnected: 'status-offline',
    connecting: 'status-pending',
    connected: 'status-online',
    scanning: 'status-scanning',
  }

  return (
    <header className="header">
      <div className="header-left">
        <div className="logo">
          <span className="logo-icon">⚛️</span>
          <div>
            <h1 className="logo-title">Q-Shield</h1>
            <p className="logo-subtitle">Quantum Fraud Detection</p>
          </div>
        </div>
      </div>

      <div className="header-center">
        <div className="stat-cards">
          <div className="stat-card">
            <span className="stat-value">{stats.total}</span>
            <span className="stat-label">Scanned</span>
          </div>
          <div className="stat-card stat-fraud">
            <span className="stat-value">{stats.fraud}</span>
            <span className="stat-label">Fraud</span>
          </div>
          <div className="stat-card stat-legit">
            <span className="stat-value">{stats.legit}</span>
            <span className="stat-label">Legit</span>
          </div>
        </div>
      </div>

      <div className="header-right">
        <div className={`status-badge ${statusClass[status]}`}>
          <span className="status-dot"></span>
          {statusLabel[status]}
        </div>

        <div className="header-actions">
          <button
            className="btn btn-connect"
            onClick={onConnect}
            disabled={status === 'connecting' || status === 'scanning'}
          >
            {status === 'connecting' ? '⏳ Connecting...' : '🔗 Connect Bank'}
          </button>
          <button
            className="btn btn-scan"
            onClick={onScan}
            disabled={status !== 'connected'}
          >
            {status === 'scanning' ? '⚛️ Scanning...' : '⚡ Quantum Scan'}
          </button>
        </div>

        {error && <div className="error-toast">{error}</div>}
      </div>
    </header>
  )
}

export default Header
