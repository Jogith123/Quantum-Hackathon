import { forwardRef } from 'react'
import TransactionCard from './TransactionCard'
import './TransactionFeed.css'

const TransactionFeed = forwardRef(({ transactions, status }, ref) => {
  if (transactions.length === 0) {
    return (
      <div className="feed-empty" ref={ref}>
        <div className="feed-empty-icon">
          {status === 'scanning' ? '⚛️' : '🛡️'}
        </div>
        <h2>
          {status === 'scanning'
            ? 'Quantum Scan in Progress...'
            : status === 'connected'
            ? 'Ready to Scan'
            : 'Connect a Bank to Begin'}
        </h2>
        <p>
          {status === 'scanning'
            ? 'Encoding transactions into quantum states via ZZFeatureMap...'
            : status === 'connected'
            ? 'Click "⚡ Quantum Scan" to analyze transactions with QSVM'
            : 'Click "🔗 Connect Bank" to link a Plaid Sandbox account'}
        </p>
        {status === 'scanning' && (
          <div className="quantum-loader">
            <div className="qubit q1"></div>
            <div className="qubit q2"></div>
            <div className="qubit q3"></div>
            <div className="qubit q4"></div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="feed" ref={ref}>
      <div className="feed-header">
        <h2>Live Transaction Feed</h2>
        <span className="feed-count">{transactions.length} transactions</span>
      </div>
      <div className="feed-list">
        {transactions.map((tx, idx) => (
          <TransactionCard
            key={idx}
            transaction={tx}
            index={idx}
            isNew={idx === 0}
          />
        ))}
      </div>
    </div>
  )
})

TransactionFeed.displayName = 'TransactionFeed'
export default TransactionFeed
