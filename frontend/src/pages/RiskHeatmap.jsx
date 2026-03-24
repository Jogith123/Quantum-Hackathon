import { useState } from 'react'
import './RiskHeatmap.css'

export default function RiskHeatmap({ apiBase }) {
  const [inputMode, setInputMode] = useState('manual') // manual | csv
  const [manualAmount, setManualAmount] = useState('')
  const [manualFeatures, setManualFeatures] = useState('')
  const [csvText, setCsvText] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const generateRandomTransaction = () => {
    const features = Array.from({ length: 28 }, () => (Math.random() * 4 - 2).toFixed(4))
    setManualFeatures(features.join(', '))
    setManualAmount((Math.random() * 500 + 1).toFixed(2))
  }

  const generateBatch = () => {
    const lines = []
    for (let i = 0; i < 20; i++) {
      const features = Array.from({ length: 28 }, () => (Math.random() * 4 - 2).toFixed(4))
      const amount = (Math.random() * 500 + 1).toFixed(2)
      lines.push([...features, amount].join(','))
    }
    setCsvText(lines.join('\n'))
    setInputMode('csv')
  }

  const handlePredict = async () => {
    setLoading(true)
    setError(null)
    setResults([])

    try {
      let transactions = []

      if (inputMode === 'manual') {
        const features = manualFeatures.split(',').map(f => parseFloat(f.trim()))
        const amount = parseFloat(manualAmount) || 0
        if (features.length !== 28) {
          setError('Need exactly 28 V-features (comma-separated)')
          setLoading(false)
          return
        }
        const tx = {}
        features.forEach((f, i) => { tx[`V${i + 1}`] = f })
        tx.Amount = amount
        transactions = [tx]
      } else {
        const rows = csvText.trim().split('\n').filter(r => r.trim())
        for (const row of rows) {
          const vals = row.split(',').map(v => parseFloat(v.trim()))
          if (vals.length !== 29) continue
          const tx = {}
          vals.slice(0, 28).forEach((f, i) => { tx[`V${i + 1}`] = f })
          tx.Amount = vals[28]
          transactions = [...transactions, tx]
        }
      }

      if (transactions.length === 0) {
        setError('No valid transactions to predict')
        setLoading(false)
        return
      }

      // Send as individual predictions (batch endpoint format)
      const allResults = []
      for (const tx of transactions) {
        const res = await fetch(`${apiBase}/api/predict`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(tx),
        })
        const data = await res.json()
        allResults.push({ tx, result: data })
      }
      setResults(allResults)
    } catch (e) {
      setError('Prediction failed. Check that api.py and server.js are running.')
    }
    setLoading(false)
  }

  const getRiskColor = (score) => {
    if (score >= 0.7) return '#ef4444'
    if (score >= 0.4) return '#f59e0b'
    return '#22c55e'
  }

  return (
    <div>
      <div className="page-header">
        <h1>🗺️ Risk Heatmap — Transaction Explorer</h1>
        <p>Submit transactions manually or in batch for QSVM analysis</p>
      </div>

      {/* Input Controls */}
      <div className="card input-card">
        <div className="input-tabs">
          <button
            className={`tab-btn ${inputMode === 'manual' ? 'tab-active' : ''}`}
            onClick={() => setInputMode('manual')}
          >
            ✍️ Manual Entry
          </button>
          <button
            className={`tab-btn ${inputMode === 'csv' ? 'tab-active' : ''}`}
            onClick={() => setInputMode('csv')}
          >
            📋 Batch CSV
          </button>
          <button className="btn btn-secondary" onClick={generateRandomTransaction} style={{ marginLeft: 'auto' }}>
            🎲 Random Transaction
          </button>
          <button className="btn btn-secondary" onClick={generateBatch}>
            🎲 Random Batch (20)
          </button>
        </div>

        {inputMode === 'manual' ? (
          <div className="manual-input">
            <div className="input-group">
              <label>V1-V28 Features (comma-separated)</label>
              <textarea
                value={manualFeatures}
                onChange={e => setManualFeatures(e.target.value)}
                placeholder="0.1234, -0.5678, 1.234, ..."
                rows={3}
              />
            </div>
            <div className="input-group" style={{ maxWidth: 200 }}>
              <label>Amount ($)</label>
              <input
                type="number"
                value={manualAmount}
                onChange={e => setManualAmount(e.target.value)}
                placeholder="149.99"
              />
            </div>
          </div>
        ) : (
          <div className="csv-input">
            <label>CSV Format: V1,V2,...,V28,Amount (one per line)</label>
            <textarea
              value={csvText}
              onChange={e => setCsvText(e.target.value)}
              placeholder="0.123,-0.456,...,1.23,149.99"
              rows={8}
            />
          </div>
        )}

        <button className="btn btn-primary" onClick={handlePredict} disabled={loading} style={{ marginTop: 12 }}>
          {loading ? '⏳ Analyzing...' : '⚡ Run QSVM Analysis'}
        </button>
      </div>

      {error && <div className="error-box" style={{ marginTop: 12 }}>{error}</div>}

      {/* Results Heatmap */}
      {results.length > 0 && (
        <div className="card" style={{ marginTop: 16 }}>
          <div className="card-title">Risk Heatmap — {results.length} Transactions</div>
          <div className="heatmap-grid">
            {results.map((r, idx) => {
              const riskScore = r.result.risk_score || r.result.risk_percentage ? parseFloat(r.result.risk_percentage) / 100 : 0.5
              const color = getRiskColor(riskScore)
              return (
                <div
                  key={idx}
                  className="heatmap-cell"
                  style={{
                    background: `${color}22`,
                    borderColor: `${color}66`,
                    boxShadow: `0 0 12px ${color}33`,
                  }}
                  title={`TX #${idx + 1} — Risk: ${(riskScore * 100).toFixed(1)}%`}
                >
                  <div className="cell-idx mono">#{idx + 1}</div>
                  <div className="cell-label" style={{ color }}>{r.result.prediction || r.result.label}</div>
                  <div className="cell-risk mono" style={{ color }}>{(riskScore * 100).toFixed(0)}%</div>
                  <div className="cell-amount mono">${r.tx.Amount.toFixed(2)}</div>
                </div>
              )
            })}
          </div>

          {/* Summary */}
          <div className="heatmap-summary">
            <div className="hs-item">
              <span className="hs-dot" style={{ background: '#ef4444' }}></span>
              <span>High Risk (≥70%): {results.filter(r => (r.result.risk_score || 0.5) >= 0.7).length}</span>
            </div>
            <div className="hs-item">
              <span className="hs-dot" style={{ background: '#f59e0b' }}></span>
              <span>Medium Risk (40-70%): {results.filter(r => { const s = r.result.risk_score || 0.5; return s >= 0.4 && s < 0.7 }).length}</span>
            </div>
            <div className="hs-item">
              <span className="hs-dot" style={{ background: '#22c55e' }}></span>
              <span>Low Risk (&lt;40%): {results.filter(r => (r.result.risk_score || 0.5) < 0.4).length}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
