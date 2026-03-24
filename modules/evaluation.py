"""
Module 7: Model Evaluation
============================
Compute comprehensive performance metrics for any model.
"""

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from modules.logger import log_info


def compute_metrics(y_true, y_pred):
    """
    Compute accuracy, precision, recall, F1, confusion matrix, and report.

    Parameters
    ----------
    y_true : np.ndarray
        True labels.
    y_pred : np.ndarray
        Predicted labels.

    Returns
    -------
    dict
        All evaluation metrics.
    """
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1_score": f1_score(y_true, y_pred, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred),
        "report": classification_report(y_true, y_pred,
                                         target_names=["Legit", "Fraud"]),
    }
    return metrics


def print_evaluation_report(metrics, model_name):
    """
    Print a formatted evaluation report.

    Parameters
    ----------
    metrics : dict
        Output from compute_metrics.
    model_name : str
        Name of the model (e.g., 'Classical SVM', 'QSVM').
    """
    print(f"\n  ┌──────────────────────────────────────────┐")
    print(f"  │  {model_name} Evaluation Report")
    print(f"  ├──────────────────────────────────────────┤")
    print(f"  │  Accuracy:   {metrics['accuracy']:.4f}")
    print(f"  │  Precision:  {metrics['precision']:.4f}")
    print(f"  │  Recall:     {metrics['recall']:.4f}")
    print(f"  │  F1-Score:   {metrics['f1_score']:.4f}")
    print(f"  └──────────────────────────────────────────┘")
    print(f"\n{metrics['report']}")
