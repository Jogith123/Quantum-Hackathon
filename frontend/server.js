import express from 'express';
import cors from 'cors';

const app = express();
const PORT = 3001;
const FASTAPI_URL = 'http://127.0.0.1:8000';

app.use(cors());
app.use(express.json());

// ── Proxy Helpers ───────────────────────────────────────
async function proxyGet(endpoint) {
  const res = await fetch(`${FASTAPI_URL}${endpoint}`);
  return res.json();
}

async function proxyPost(endpoint, body = {}) {
  const res = await fetch(`${FASTAPI_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res.json();
}

// ── API Routes ──────────────────────────────────────────

// Connect to Plaid Sandbox
app.post('/api/connect', async (req, res) => {
  try {
    const data = await proxyPost('/plaid/connect');
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'FastAPI unavailable. Is api.py running?' });
  }
});

// Fetch + Quantum Scan all transactions
app.get('/api/scan', async (req, res) => {
  try {
    const data = await proxyGet('/plaid/scan');
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'FastAPI unavailable. Is api.py running?' });
  }
});

// Health check
app.get('/api/health', async (req, res) => {
  try {
    const data = await proxyGet('/health');
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'FastAPI unavailable.' });
  }
});

// Metrics
app.get('/api/metrics', async (req, res) => {
  try {
    const data = await proxyGet('/metrics');
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'FastAPI unavailable.' });
  }
});

// Tuning leaderboard
app.get('/api/tuning', async (req, res) => {
  try {
    const data = await proxyGet('/tuning');
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'FastAPI unavailable.' });
  }
});

// Batch predict
app.post('/api/predict/batch', async (req, res) => {
  try {
    const data = await proxyPost('/predict/batch', req.body);
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'FastAPI unavailable.' });
  }
});

// Single predict
app.post('/api/predict', async (req, res) => {
  try {
    const data = await proxyPost('/predict', req.body);
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'FastAPI unavailable.' });
  }
});

// ── Start Server ────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`\n  ⚡ Q-Shield Express Proxy running on http://localhost:${PORT}`);
  console.log(`  ➤ Proxying to FastAPI at ${FASTAPI_URL}\n`);
});
