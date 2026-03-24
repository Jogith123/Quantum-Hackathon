"""
Q-Shield Real-Time API
========================
FastAPI application providing real-time fraud prediction
using pre-trained QSVM models + Plaid Sandbox integration.

Endpoints:
  POST /predict             — Single transaction prediction
  POST /predict/batch       — Batch transaction predictions
  POST /stream              — SSE streaming predictions
  GET  /health              — Health check + model status
  GET  /metrics             — Return saved evaluation metrics
  POST /plaid/connect       — Connect to Plaid Sandbox bank
  GET  /plaid/transactions  — Fetch raw Plaid transactions
  GET  /plaid/scan          — Fetch + quantum fraud scan

Usage:
  python api.py
  # or: uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import sys
import json
import asyncio
from contextlib import asynccontextmanager

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

import config
from modules.streaming import RealTimePredictor
from modules.plaid_bridge import PlaidBridge
from modules.logger import log_success, log_info


# ── Initialize components ────────────────────────────────
predictor = RealTimePredictor()
plaid_bridge = PlaidBridge()


# ── Lifespan (replaces deprecated on_event) ──────────────
@asynccontextmanager
async def lifespan(app):
    """Load models on startup, cleanup on shutdown."""
    try:
        predictor.load_models()
        log_success("Q-Shield API ready — models loaded")
    except FileNotFoundError as e:
        print(f"\n  ⚠ WARNING: {e}")
        print("  ➤ The API will start but predictions will fail.")
        print("  ➤ Run 'python main.py' first to train and save models.\n")
    yield


# ═══════════════════════════════════════════════════════════
# App Configuration
# ═══════════════════════════════════════════════════════════
app = FastAPI(
    title="Q-Shield: Quantum Fraud Detection API",
    description=(
        "Real-time fraud detection using Quantum Support Vector Machines. "
        "This API uses pre-trained QSVM models to classify financial "
        "transactions by computing quantum kernels in Hilbert space."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════
# Request / Response Models
# ═══════════════════════════════════════════════════════════
class TransactionRequest(BaseModel):
    """Single transaction for fraud prediction."""
    V1: float = Field(0.0, description="PCA component V1")
    V2: float = Field(0.0, description="PCA component V2")
    V3: float = Field(0.0, description="PCA component V3")
    V4: float = Field(0.0, description="PCA component V4")
    V5: float = Field(0.0, description="PCA component V5")
    V6: float = Field(0.0, description="PCA component V6")
    V7: float = Field(0.0, description="PCA component V7")
    V8: float = Field(0.0, description="PCA component V8")
    V9: float = Field(0.0, description="PCA component V9")
    V10: float = Field(0.0, description="PCA component V10")
    V11: float = Field(0.0, description="PCA component V11")
    V12: float = Field(0.0, description="PCA component V12")
    V13: float = Field(0.0, description="PCA component V13")
    V14: float = Field(0.0, description="PCA component V14")
    V15: float = Field(0.0, description="PCA component V15")
    V16: float = Field(0.0, description="PCA component V16")
    V17: float = Field(0.0, description="PCA component V17")
    V18: float = Field(0.0, description="PCA component V18")
    V19: float = Field(0.0, description="PCA component V19")
    V20: float = Field(0.0, description="PCA component V20")
    V21: float = Field(0.0, description="PCA component V21")
    V22: float = Field(0.0, description="PCA component V22")
    V23: float = Field(0.0, description="PCA component V23")
    V24: float = Field(0.0, description="PCA component V24")
    V25: float = Field(0.0, description="PCA component V25")
    V26: float = Field(0.0, description="PCA component V26")
    V27: float = Field(0.0, description="PCA component V27")
    V28: float = Field(0.0, description="PCA component V28")
    Amount: float = Field(0.0, description="Transaction amount")


class PredictionResponse(BaseModel):
    """Fraud prediction result."""
    label: str
    prediction: int
    confidence: float
    risk_score: float
    risk_percentage: str
    model: str


class BatchRequest(BaseModel):
    """Batch of transactions for prediction."""
    transactions: list[TransactionRequest]


class HealthResponse(BaseModel):
    """API health and model status."""
    status: str
    models_loaded: bool
    qsvm_ready: bool
    training_samples: int
    message: str


# ═══════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════

@app.get("/", tags=["Info"])
async def root():
    """API welcome message with quantum insight."""
    return {
        "name": "Q-Shield: Quantum Fraud Detection Engine",
        "version": "2.0.0",
        "insight": (
            "Q-Shield uses quantum feature mapping, entanglement, "
            "and kernel-based learning to detect fraud patterns "
            "beyond classical systems."
        ),
        "endpoints": [
            "POST /predict - Single transaction",
            "POST /predict/batch - Batch predictions",
            "POST /stream - SSE streaming",
            "GET /health - System status",
            "GET /metrics - Model metrics",
            "GET /tuning - Adaptive tuning leaderboard",
            "POST /plaid/connect - Connect to Plaid Sandbox",
            "GET /plaid/transactions - Fetch bank transactions",
            "GET /plaid/scan - Quantum scan Plaid transactions",
        ],
    }


@app.get("/tuning", tags=["Info"])
async def get_tuning_results():
    """Return the adaptive quantum kernel tuning leaderboard."""
    tuning_path = os.path.join(config.OUTPUT_DIR, "tuning_results.json")
    if not os.path.exists(tuning_path):
        raise HTTPException(
            status_code=404,
            detail="Tuning results not found. Run 'python main.py' first."
        )
    with open(tuning_path) as f:
        return json.load(f)


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_transaction(transaction: TransactionRequest):
    """
    Predict if a single transaction is fraudulent.

    Flow: Preprocess → Quantum Kernel → QSVM → Risk Score

    The transaction is encoded into a quantum state, its similarity
    to training data is computed via quantum kernel, and the QSVM
    classifies it in high-dimensional Hilbert space.
    """
    if not predictor.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Run 'python main.py' first.",
        )

    try:
        tx_dict = transaction.model_dump()
        result = predictor.predict(tx_dict)
        result["risk_percentage"] = f"{result['risk_score'] * 100:.1f}%"
        return PredictionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/predict/batch", tags=["Prediction"])
async def predict_batch(batch: BatchRequest):
    """
    Predict fraud for a batch of transactions.

    Each transaction is independently encoded and classified
    using the quantum kernel method.
    """
    if not predictor.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Run 'python main.py' first.",
        )

    try:
        results = []
        for tx in batch.transactions:
            tx_dict = tx.model_dump()
            result = predictor.predict(tx_dict)
            result["risk_percentage"] = f"{result['risk_score'] * 100:.1f}%"
            results.append(result)

        fraud_count = sum(1 for r in results if r["prediction"] == 1)
        return {
            "total": len(results),
            "fraud_detected": fraud_count,
            "legitimate": len(results) - fraud_count,
            "predictions": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch error: {str(e)}")


@app.post("/stream", tags=["Streaming"])
async def stream_predictions(batch: BatchRequest):
    """
    Stream predictions via Server-Sent Events (SSE).

    Processes transactions one-by-one and streams results
    as they are computed — suitable for real-time monitoring.
    """
    if not predictor.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Run 'python main.py' first.",
        )

    async def event_generator():
        for i, tx in enumerate(batch.transactions):
            tx_dict = tx.model_dump()
            result = predictor.predict(tx_dict)
            result["risk_percentage"] = f"{result['risk_score'] * 100:.1f}%"
            result["transaction_index"] = i

            yield f"data: {json.dumps(result)}\n\n"
            await asyncio.sleep(0.1)  # Small delay for streaming effect

        yield f"data: {json.dumps({'event': 'complete', 'total': len(batch.transactions)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Check API health and model loading status.
    """
    status = predictor.get_status()
    return HealthResponse(
        status="healthy" if status["loaded"] else "degraded",
        models_loaded=status["loaded"],
        qsvm_ready=status["qsvm_model"],
        training_samples=status["training_samples"],
        message=(
            "Q-Shield API operational — quantum models loaded"
            if status["loaded"]
            else "Models not loaded. Run 'python main.py' to train."
        ),
    )


@app.get("/metrics", tags=["System"])
async def get_metrics():
    """
    Return saved model evaluation metrics (from training pipeline).
    """
    metrics_path = os.path.join(config.OUTPUT_DIR, "metrics.json")
    if not os.path.exists(metrics_path):
        raise HTTPException(
            status_code=404,
            detail="Metrics not found. Run 'python main.py' first.",
        )

    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    metrics["insight"] = (
        "This system encodes financial data into entangled quantum states, "
        "computes similarity using quantum kernels, and classifies transactions "
        "in a high-dimensional Hilbert space where fraud patterns become separable."
    )
    return metrics

# ═══════════════════════════════════════════════════════════
# Plaid Sandbox Endpoints
# ═══════════════════════════════════════════════════════════

@app.post("/plaid/connect", tags=["Plaid"])
async def plaid_connect():
    """
    Connect to a Plaid Sandbox test bank account.

    This uses Plaid's sandbox bypass to programmatically
    create a test bank connection without a frontend UI.
    Returns an access token for fetching transactions.
    """
    try:
        result = plaid_bridge.connect_sandbox()
        return result
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plaid connection error: {str(e)}")


@app.get("/plaid/transactions", tags=["Plaid"])
async def plaid_transactions():
    """
    Fetch raw transactions from the connected Plaid Sandbox account.

    Must call /plaid/connect first to establish the bank connection.
    Returns merchant name, amount, date, category, and payment channel.
    """
    if not plaid_bridge.access_token:
        raise HTTPException(
            status_code=400,
            detail="Not connected. Call POST /plaid/connect first.",
        )

    try:
        transactions = plaid_bridge.fetch_transactions()
        return {
            "total": len(transactions),
            "source": "Plaid Sandbox",
            "transactions": transactions,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plaid fetch error: {str(e)}")


@app.get("/plaid/scan", tags=["Plaid"])
async def plaid_quantum_scan():
    """
    Fetch Plaid transactions AND run each through the QSVM engine.

    Flow per transaction:
      1. Fetch from Plaid Sandbox
      2. Bridge merchant data → deterministic V1-V28 features
      3. Compute quantum kernel row vs training data
      4. QSVM classifies in Hilbert space
      5. Return fraud label + risk score

    This is the complete end-to-end Plaid → Quantum pipeline.
    """
    if not plaid_bridge.access_token:
        raise HTTPException(
            status_code=400,
            detail="Not connected. Call POST /plaid/connect first.",
        )

    if not predictor.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Run 'python main.py' first.",
        )

    try:
        transactions = plaid_bridge.fetch_transactions()
        results = []

        for tx in transactions:
            # Bridge Plaid data → quantum features
            quantum_features = PlaidBridge.bridge_to_quantum(tx)

            # Run through QSVM
            prediction = predictor.predict(quantum_features)

            results.append({
                "plaid_data": {
                    "merchant": tx["merchant"],
                    "amount": tx["amount"],
                    "date": tx["date"],
                    "category": tx["category"],
                    "payment_channel": tx["payment_channel"],
                },
                "quantum_analysis": {
                    "label": prediction["label"],
                    "risk_score": prediction["risk_score"],
                    "risk_percentage": f"{prediction['risk_score'] * 100:.1f}%",
                    "confidence": prediction["confidence"],
                    "model": "QSVM",
                    "insight": "Analyzed via quantum kernel in Hilbert space",
                },
            })

        fraud_count = sum(1 for r in results if r["quantum_analysis"]["label"] == "FRAUD")

        return {
            "total_transactions": len(results),
            "fraud_detected": fraud_count,
            "legitimate": len(results) - fraud_count,
            "source": "Plaid Sandbox → Q-Shield QSVM",
            "system_positioning": "We prioritize fraud detection over false positives — aligning with real-world financial risk strategies.",
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quantum scan error: {str(e)}")


# ═══════════════════════════════════════════════════════════
# Run Server
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║       Q-SHIELD: Real-Time Quantum Fraud Detection       ║")
    print("║              FastAPI + QSVM Engine                       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"\n  ⚡ Starting API server on http://{config.API_HOST}:{config.API_PORT}")
    print(f"  📖 Docs: http://localhost:{config.API_PORT}/docs\n")

    uvicorn.run(
        "api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=False,
    )
