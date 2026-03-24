"""
Module 3: Classical Baseline Model
====================================
Train and evaluate a classical SVM with RBF kernel.
"""

from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from modules.logger import log_info, log_success
import config


def train_classical_svm(X_train, y_train):
    """
    Train a classical SVM with RBF kernel.

    Parameters
    ----------
    X_train : np.ndarray
        Training features (PCA-reduced).
    y_train : np.ndarray
        Training labels.

    Returns
    -------
    SVC
        Trained SVM model.
    """
    model = SVC(kernel="rbf", random_state=config.RANDOM_STATE, probability=False)
    model.fit(X_train, y_train)
    log_success("Classical SVM (RBF) trained")
    return model


def evaluate_classical_svm(model, X_test, y_test):
    """
    Evaluate the classical SVM model.

    Parameters
    ----------
    model : SVC
        Trained classical SVM.
    X_test : np.ndarray
        Test features.
    y_test : np.ndarray
        True test labels.

    Returns
    -------
    dict
        Dictionary with predictions, accuracy, report, and confusion matrix.
    """
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["Legit", "Fraud"])
    cm = confusion_matrix(y_test, y_pred)

    log_info(f"Classical SVM Accuracy: {acc:.4f}")
    print(f"\n{report}")

    return {
        "y_pred": y_pred,
        "accuracy": acc,
        "report": report,
        "confusion_matrix": cm,
    }
