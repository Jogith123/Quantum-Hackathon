"""
Module 9: Prediction Module
==============================
Make predictions with QSVM and compute fraud risk scores
using sigmoid transformation of decision function values.
"""

import math
import numpy as np
from modules.logger import log_info, log_success


def predict_with_risk(model, kernel_sample):
    """
    Predict fraud/legit for a single sample and compute risk score.

    Uses the SVM decision function value and applies sigmoid
    transformation to produce a probability-like risk score.

    Parameters
    ----------
    model : SVC
        Trained QSVM model (precomputed kernel).
    kernel_sample : np.ndarray
        Precomputed kernel row for the sample (1×N array).

    Returns
    -------
    dict
        {
            "label": "FRAUD" or "LEGITIMATE",
            "prediction": int (0 or 1),
            "confidence": float (absolute decision value),
            "risk_score": float (0.0 to 1.0)
        }
    """
    # Ensure 2D shape
    if kernel_sample.ndim == 1:
        kernel_sample = kernel_sample.reshape(1, -1)

    prediction = model.predict(kernel_sample)[0]
    decision_value = model.decision_function(kernel_sample)[0]

    # Sigmoid transformation for risk score
    risk_score = 1.0 / (1.0 + math.exp(-float(decision_value)))

    return {
        "label": "FRAUD" if prediction == 1 else "LEGITIMATE",
        "prediction": int(prediction),
        "confidence": round(abs(float(decision_value)), 4),
        "risk_score": round(risk_score, 4),
    }


def demo_prediction(model, kernel_test, y_test):
    """
    Run a demo prediction on the first test sample.

    Parameters
    ----------
    model : SVC
        Trained QSVM model.
    kernel_test : np.ndarray
        Precomputed test kernel matrix (M×N).
    y_test : np.ndarray
        True test labels.

    Returns
    -------
    dict
        Prediction result with risk score.
    """
    # Pick first test sample
    sample_kernel = kernel_test[0:1, :]
    true_label = y_test[0]

    result = predict_with_risk(model, sample_kernel)

    # ── Display ──────────────────────────────────────────
    print(f"\n  ┌──────────────────────────────────────────┐")
    print(f"  │  PREDICTION DEMO                         │")
    print(f"  ├──────────────────────────────────────────┤")
    print(f"  │  True Label:    {'FRAUD' if true_label == 1 else 'LEGITIMATE':<24}│")
    print(f"  │  Predicted:     {result['label']:<24}│")
    print(f"  │  Confidence:    {result['confidence']:<24}│")
    print(f"  │  Risk Score:    {result['risk_score'] * 100:.1f}%{' ' * 19}│")
    print(f"  │  Status:        {'✓ CORRECT' if result['prediction'] == true_label else '✗ INCORRECT':<24}│")
    print(f"  └──────────────────────────────────────────┘")

    log_success(f"Fraud Risk Score: {result['risk_score'] * 100:.1f}%")
    return result
