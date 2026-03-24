"""
Module 6: QSVM Model
======================
Train an SVM using precomputed quantum kernel matrices.
"""

from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from modules.logger import log_info, log_success
import config


def train_qsvm(kernel_train, y_train):
    """
    Train an SVM with a precomputed quantum kernel.

    Parameters
    ----------
    kernel_train : np.ndarray
        Precomputed kernel matrix (N×N) from quantum kernel computation.
    y_train : np.ndarray
        Training labels.

    Returns
    -------
    SVC
        Trained QSVM model.
    """
    model = SVC(kernel="precomputed", random_state=config.RANDOM_STATE)
    model.fit(kernel_train, y_train)
    log_success("QSVM (precomputed quantum kernel) trained")
    print("\n  ⚛️  QSVM operating in quantum-transformed feature space")
    print("     Decision boundary learned in high-dimensional Hilbert space")
    return model


def evaluate_qsvm(model, kernel_test, y_test):
    """
    Evaluate the QSVM model on test data.

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
        Dictionary with predictions, accuracy, report, and confusion matrix.
    """
    y_pred = model.predict(kernel_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["Legit", "Fraud"])
    cm = confusion_matrix(y_test, y_pred)

    log_info(f"QSVM Accuracy: {acc:.4f}")
    print(f"\n{report}")

    return {
        "y_pred": y_pred,
        "accuracy": acc,
        "report": report,
        "confusion_matrix": cm,
    }
