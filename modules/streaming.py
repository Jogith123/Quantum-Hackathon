"""
Module 11: Real-Time Streaming Engine
========================================
Loads pre-trained models and provides instant fraud prediction
without retraining or recomputing full kernel matrices.

Architecture:
  [Saved Models] → RealTimePredictor.load_models()
  [New Transaction] → preprocess → quantum kernel row → QSVM predict → risk score
"""

import os
import json
import math
import numpy as np
import joblib
from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from modules.logger import log_info, log_success, log_warning
import config


class RealTimePredictor:
    """
    Real-time fraud prediction engine.

    Uses pre-trained QSVM model, saved scaler/PCA transformers,
    and quantum kernel computed against training reference data.

    CRITICAL: This engine NEVER retrains models or recomputes
    full kernel matrices. It only computes the kernel row for
    a single new sample against the saved training data.
    """

    def __init__(self):
        self.qsvm_model = None
        self.classical_model = None
        self.scaler = None
        self.pca = None
        self.X_train_q = None
        self.quantum_kernel = None
        self.is_loaded = False

    def load_models(self):
        """
        Load all pre-trained models and artifacts from disk.

        Raises
        ------
        FileNotFoundError
            If model files are missing (run main.py first).
        """
        required_files = [
            config.QSVM_MODEL_PATH,
            config.SCALER_PATH,
            config.PCA_PATH,
            config.TRAINING_DATA_PATH,
            config.FEATURE_MAP_CONFIG_PATH,
        ]

        for f in required_files:
            if not os.path.exists(f):
                raise FileNotFoundError(
                    f"\n  ✗ Model file not found: {f}\n"
                    f"  ➤ Run 'python main.py' first to train and save models.\n"
                )

        # Load trained models
        self.qsvm_model = joblib.load(config.QSVM_MODEL_PATH)
        self.scaler = joblib.load(config.SCALER_PATH)
        self.pca = joblib.load(config.PCA_PATH)
        self.X_train_q = joblib.load(config.TRAINING_DATA_PATH)

        # Load classical model if available
        if os.path.exists(config.CLASSICAL_MODEL_PATH):
            self.classical_model = joblib.load(config.CLASSICAL_MODEL_PATH)

        # Reconstruct quantum kernel from saved config
        with open(config.FEATURE_MAP_CONFIG_PATH, "r") as f:
            fm_config = json.load(f)

        feature_map = ZZFeatureMap(
            feature_dimension=fm_config["feature_dimension"],
            reps=fm_config["reps"],
            entanglement=fm_config["entanglement"],
        )
        self.quantum_kernel = FidelityQuantumKernel(feature_map=feature_map)
        self.is_loaded = True

        log_success("All models loaded for real-time prediction")
        log_info(f"Training reference data shape: {self.X_train_q.shape}")

    def preprocess_transaction(self, transaction):
        """
        Preprocess a single raw transaction for prediction.

        Parameters
        ----------
        transaction : dict or np.ndarray
            If dict: raw feature values (V1-V28 + Amount).
            If ndarray: already-processed feature vector.

        Returns
        -------
        np.ndarray
            PCA-reduced feature vector (1 × n_components).
        """
        if isinstance(transaction, dict):
            # Extract features in expected order
            feature_names = [f"V{i}" for i in range(1, 29)] + ["Amount"]
            raw = np.array([transaction.get(name, 0.0) for name in feature_names])

            # Scale Amount (last feature)
            raw[-1] = self.scaler.transform([[raw[-1]]])[0, 0]

            # PCA transform
            features_pca = self.pca.transform(raw.reshape(1, -1))
        elif isinstance(transaction, np.ndarray):
            if transaction.ndim == 1:
                transaction = transaction.reshape(1, -1)
            if transaction.shape[1] == config.N_PCA_COMPONENTS:
                # Already PCA-reduced
                features_pca = transaction
            else:
                # Scale Amount (assume last column)
                transaction[0, -1] = self.scaler.transform(
                    [[transaction[0, -1]]]
                )[0, 0]
                features_pca = self.pca.transform(transaction)
        else:
            raise ValueError("Transaction must be dict or np.ndarray")

        return features_pca

    def predict(self, transaction):
        """
        Predict fraud/legit for a single transaction with risk score.

        Flow: Preprocess → Quantum Kernel Row → QSVM Predict → Risk Score

        Parameters
        ----------
        transaction : dict or np.ndarray
            Raw or preprocessed transaction data.

        Returns
        -------
        dict
            {
                "label": "FRAUD" or "LEGITIMATE",
                "prediction": int (0 or 1),
                "confidence": float,
                "risk_score": float (0.0 to 1.0),
                "model": "QSVM"
            }
        """
        if not self.is_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")

        # Preprocess
        features_pca = self.preprocess_transaction(transaction)

        # Compute quantum kernel row: similarity of new sample vs all training samples
        kernel_row = self.quantum_kernel.evaluate(
            x_vec=features_pca,
            y_vec=self.X_train_q
        )

        # QSVM prediction
        prediction = self.qsvm_model.predict(kernel_row)[0]
        decision_value = self.qsvm_model.decision_function(kernel_row)[0]

        # Sigmoid risk score
        risk_score = 1.0 / (1.0 + math.exp(-float(decision_value)))

        return {
            "label": "FRAUD" if prediction == 1 else "LEGITIMATE",
            "prediction": int(prediction),
            "confidence": round(abs(float(decision_value)), 4),
            "risk_score": round(risk_score, 4),
            "model": "QSVM",
        }

    def predict_batch(self, transactions):
        """
        Predict fraud/legit for multiple transactions.

        Parameters
        ----------
        transactions : list[dict] or list[np.ndarray]
            List of transaction data.

        Returns
        -------
        list[dict]
            List of prediction results.
        """
        return [self.predict(t) for t in transactions]

    def get_status(self):
        """Return model loading status and info."""
        return {
            "loaded": self.is_loaded,
            "qsvm_model": self.qsvm_model is not None,
            "classical_model": self.classical_model is not None,
            "scaler": self.scaler is not None,
            "pca": self.pca is not None,
            "training_samples": (
                self.X_train_q.shape[0] if self.X_train_q is not None else 0
            ),
        }
