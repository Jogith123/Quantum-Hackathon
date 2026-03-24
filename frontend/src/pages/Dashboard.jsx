import { useState, useEffect } from 'react'
import './Dashboard.css'

export default function Dashboard({ apiBase }) {
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${apiBase}/api/metrics`)
      .then(r => r.json())
      .then(data => { setMetrics(data); setLoading(false) })
      .catch(() => { setError('Cannot load metrics. Run python main.py first.'); setLoading(false) })
  }, [apiBase])

  if (loading) return <div className="loading-spinner">⏳ Loading metrics...</div>
  if (error) return <div className="error-box">{error}</div>

  const c = metrics.classical_svm
  const q = metrics.qsvm

  const metricRows = [
    { name: 'Recall', c: c.recall, q: q.recall, icon: '🎯', key: true },
    { name: 'Precision', c: c.precision, q: q.precision, icon: '🎯' },
    { name: 'Accuracy', c: c.accuracy, q: q.accuracy, icon: '📐' },
    { name: 'F1-Score', c: c.f1_score, q: q.f1_score, icon: '⚖️' },
  ]

  const missedFraud = Math.round((1 - q.recall) * 100)

  return (
    <div>
      <div className="page-header">
        <h1>📊 Quantum vs Classical Dashboard</h1>
        <p>Side-by-side model performance comparison — fraud-first evaluation</p>
      </div>

      {/* Hero Stat */}
      <div className="hero-stat-row">
        <div className="hero-stat hero-fraud">
          <div className="hero-value">{missedFraud}</div>
          <div className="hero-label">Fraud Cases Missed by QSVM</div>
          <div className="hero-sub">{q.recall >= 1 ? '✅ Perfect fraud detection' : '⚠️ Some fraud cases undetected'}</div>
        </div>
        <div className="hero-stat hero-recall">
          <div className="hero-value">{(q.recall * 100).toFixed(0)}%</div>
          <div className="hero-label">QSVM Recall</div>
          <div className="hero-sub">Quantum fraud detection rate</div>
        </div>
        <div className="hero-stat hero-classical">
          <div className="hero-value">{(c.recall * 100).toFixed(0)}%</div>
          <div className="hero-label">Classical Recall</div>
          <div className="hero-sub">Standard SVM detection rate</div>
        </div>
      </div>

      {/* Metric Bars */}
      <div className="card" style={{ marginTop: 16 }}>
        <div className="card-title">Performance Comparison</div>
        <div className="metric-bars">
          {metricRows.map(m => (
            <div key={m.name} className={`metric-row ${m.key ? 'metric-key' : ''}`}>
              <div className="metric-name">
                <span>{m.icon}</span>
                <span>{m.name}</span>
                {m.key && <span className="key-badge">KEY METRIC</span>}
              </div>
              <div className="metric-dual-bar">
                <div className="bar-group">
                  <span className="bar-label mono">Classical</span>
                  <div className="bar-track">
                    <div className="bar-fill bar-classical" style={{ width: `${m.c * 100}%` }}></div>
                  </div>
                  <span className="bar-value mono">{(m.c * 100).toFixed(1)}%</span>
                </div>
                <div className="bar-group">
                  <span className="bar-label mono">QSVM</span>
                  <div className="bar-track">
                    <div className="bar-fill bar-qsvm" style={{ width: `${m.q * 100}%` }}></div>
                  </div>
                  <span className="bar-value mono">{(m.q * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Philosophy */}
      <div className="card philosophy-card" style={{ marginTop: 16 }}>
        <div className="card-title">System Positioning</div>
        <p className="philosophy-text">
          "We prioritize <strong>fraud detection</strong> over false positives — aligning with real-world financial risk strategies.
          Missing a $10,000 fraud costs exponentially more than temporarily flagging a legitimate $10 transaction."
        </p>
      </div>
    </div>
  )
}
