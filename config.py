"""
Q-Shield Configuration
======================
Global constants and hyperparameters for the Q-Shield pipeline.
Set DEMO_MODE = True for fast execution, False for full pipeline.
"""

import os

# ── Load .env file if present ────────────────────────────
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _val = _line.split("=", 1)
                os.environ.setdefault(_key.strip(), _val.strip())

# ── Demo Mode ────────────────────────────────────────────
DEMO_MODE = False  # False = production (100 samples, 6 qubits)

# ── Dataset ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "data", "creditcard.csv")

# ── Preprocessing ────────────────────────────────────────
N_PCA_COMPONENTS = 6              # 6 features = 6 qubits (richer encoding)
TEST_SIZE = 0.2
RANDOM_STATE = 42

# ── Quantum Parameters (auto-adjusted for demo mode) ────
if DEMO_MODE:
    QUANTUM_SAMPLE_SIZE = 30      # Fast demo
    ZZ_REPS = 1                   # Shallow circuit
else:
    QUANTUM_SAMPLE_SIZE = 100     # Balanced: speed vs accuracy
    ZZ_REPS = 2                   # Deeper encoding for 6 qubits

ENTANGLEMENT = "full"             # Entanglement strategy for ZZFeatureMap

# ── Kernel Caching ───────────────────────────────────────
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
KERNEL_TRAIN_CACHE = os.path.join(OUTPUT_DIR, "kernel_train.npy")
KERNEL_TEST_CACHE = os.path.join(OUTPUT_DIR, "kernel_test.npy")

# ── Model Persistence ───────────────────────────────────
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")
QSVM_MODEL_PATH = os.path.join(MODELS_DIR, "qsvm_model.joblib")
CLASSICAL_MODEL_PATH = os.path.join(MODELS_DIR, "classical_model.joblib")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.joblib")
PCA_PATH = os.path.join(MODELS_DIR, "pca.joblib")
TRAINING_DATA_PATH = os.path.join(MODELS_DIR, "training_data.joblib")
FEATURE_MAP_CONFIG_PATH = os.path.join(MODELS_DIR, "feature_map_config.json")

# ── API Configuration ───────────────────────────────────
API_HOST = "0.0.0.0"
API_PORT = 8000

# ── Plaid Sandbox Configuration ─────────────────────────
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID", "")
PLAID_SECRET = os.getenv("PLAID_SECRET", "")
PLAID_ENV_URL = "https://sandbox.plaid.com"

