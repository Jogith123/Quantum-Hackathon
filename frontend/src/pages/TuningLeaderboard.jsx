import { useState, useEffect } from 'react'
import './TuningLeaderboard.css'

export default function TuningLeaderboard({ apiBase }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${apiBase}/api/tuning`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(() => { setError('Cannot load tuning results. Run python main.py first.'); setLoading(false) })
  }, [apiBase])

  if (loading) return <div className="loading-spinner">⏳ Loading tuning results...</div>
  if (error) return <div className="error-box">{error}</div>

  const { best, all_results } = data

  return (
    <div>
      <div className="page-header">
        <h1>⚛️ Adaptive Quantum Kernel Tuning</h1>
        <p>9 ZZFeatureMap configurations tested — best selected by Recall</p>
      </div>

      {/* Winner Card */}
      <div className="winner-card">
        <div className="winner-badge">🏆 OPTIMAL CONFIG</div>
        <div className="winner-grid">
          <div className="winner-detail">
            <span className="wd-label">Reps</span>
            <span className="wd-value mono">{best.reps}</span>
          </div>
          <div className="winner-detail">
            <span className="wd-label">Entanglement</span>
            <span className="wd-value mono">{best.entanglement}</span>
          </div>
          <div className="winner-detail">
            <span className="wd-label">Recall</span>
            <span className="wd-value wd-recall mono">{(best.recall * 100).toFixed(1)}%</span>
          </div>
          <div className="winner-detail">
            <span className="wd-label">Circuit Depth</span>
            <span className="wd-value mono">{best.circuit_depth}</span>
          </div>
          <div className="winner-detail">
            <span className="wd-label">F1-Score</span>
            <span className="wd-value mono">{(best.f1 * 100).toFixed(1)}%</span>
          </div>
          <div className="winner-detail">
            <span className="wd-label">Time</span>
            <span className="wd-value mono">{best.time_s}s</span>
          </div>
        </div>
      </div>

      {/* Quantum Circuit Insight */}
      <div className="card circuit-card" style={{ marginTop: 16 }}>
        <div className="card-title">Quantum Circuit Configuration</div>
        <div className="circuit-viz">
          {Array.from({ length: 4 }, (_, i) => (
            <div key={i} className="qubit-line">
              <span className="qubit-label mono">q{i}</span>
              <div className="qubit-wire">
                {Array.from({ length: best.reps }, (_, r) => (
                  <div key={r} className="gate-group">
                    <div className="gate gate-h">H</div>
                    <div className="gate gate-rz">Rz</div>
                    {best.entanglement === 'full' && i < 3 && <div className="gate gate-zz">ZZ</div>}
                    {best.entanglement === 'linear' && i < 3 && <div className="gate gate-zz">ZZ</div>}
                    {best.entanglement === 'circular' && <div className="gate gate-zz">ZZ</div>}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="card" style={{ marginTop: 16 }}>
        <div className="card-title">Full Leaderboard — 3 Reps × 3 Entanglements</div>
        <table className="leaderboard-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Reps</th>
              <th>Entanglement</th>
              <th>Recall</th>
              <th>Precision</th>
              <th>F1</th>
              <th>Accuracy</th>
              <th>Time</th>
              <th>Depth</th>
            </tr>
          </thead>
          <tbody>
            {[...all_results]
              .sort((a, b) => b.recall - a.recall || b.f1 - a.f1)
              .map((r, idx) => {
                const isWinner = r.reps === best.reps && r.entanglement === best.entanglement
                return (
                  <tr key={idx} className={isWinner ? 'row-winner' : ''}>
                    <td className="mono">{idx + 1}</td>
                    <td className="mono">{r.reps}</td>
                    <td><span className={`ent-badge ent-${r.entanglement}`}>{r.entanglement}</span></td>
                    <td className="mono td-recall">{(r.recall * 100).toFixed(1)}%</td>
                    <td className="mono">{(r.precision * 100).toFixed(1)}%</td>
                    <td className="mono">{(r.f1 * 100).toFixed(1)}%</td>
                    <td className="mono">{(r.accuracy * 100).toFixed(1)}%</td>
                    <td className="mono">{r.time_s}s</td>
                    <td className="mono">{r.circuit_depth}</td>
                  </tr>
                )
              })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
