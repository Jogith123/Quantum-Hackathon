import './TransactionCard.css'

function TransactionCard({ transaction, index, isNew }) {
  const { plaid_data, quantum_analysis } = transaction
  const isFraud = quantum_analysis.label === 'FRAUD'
  const riskPercent = (quantum_analysis.risk_score * 100).toFixed(1)

  const categoryIcons = {
    TRANSPORTATION: '🚗',
    TRAVEL: '✈️',
    FOOD_AND_DRINK: '🍔',
    ENTERTAINMENT: '🎬',
    SHOPPING: '🛍️',
    GENERAL_MERCHANDISE: '📦',
    PERSONAL_CARE: '💇',
    RENT_AND_UTILITIES: '🏠',
    TRANSFER_IN: '💸',
    TRANSFER_OUT: '💸',
    INCOME: '💰',
    BANK_FEES: '🏦',
    LOAN_PAYMENTS: '📋',
    UNKNOWN: '📌',
  }

  const icon = categoryIcons[plaid_data.category] || '📌'

  return (
    <div className={`tx-card ${isFraud ? 'tx-fraud' : 'tx-legit'} ${isNew ? 'tx-new' : ''}`}>
      <div className="tx-icon">{icon}</div>

      <div className="tx-info">
        <div className="tx-merchant">{plaid_data.merchant}</div>
        <div className="tx-meta">
          <span className="tx-category">{plaid_data.category}</span>
          <span className="tx-date">{plaid_data.date}</span>
          <span className="tx-channel">{plaid_data.payment_channel}</span>
        </div>
      </div>

      <div className="tx-amount">
        ${plaid_data.amount.toFixed(2)}
      </div>

      <div className={`tx-badge ${isFraud ? 'badge-fraud' : 'badge-legit'}`}>
        <span className="badge-dot"></span>
        <span className="badge-label">{quantum_analysis.label}</span>
      </div>

      <div className="tx-risk">
        <div className="risk-bar-track">
          <div
            className={`risk-bar-fill ${isFraud ? 'risk-high' : 'risk-low'}`}
            style={{ width: `${riskPercent}%` }}
          ></div>
        </div>
        <span className="risk-value">{riskPercent}%</span>
      </div>
    </div>
  )
}

export default TransactionCard
