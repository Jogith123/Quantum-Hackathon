"""
Module 13: Adaptive Quantum Kernel Tuning
============================================
Automatically tests multiple ZZFeatureMap configurations and selects
the one that maximizes fraud detection (Recall).

Search Space:
  - reps: [1, 2, 3]
  - entanglement: ["full", "linear", "circular"]
  - Total: 9 configurations

Each configuration is evaluated on a small validation subset
to keep computation fast. The best config is used for the
final QSVM training in the main pipeline.

This is the ADAPTIVE part of "Adaptive Quantum Kernel Learning."
"""

import time
import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import recall_score, precision_score, f1_score, accuracy_score
from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from modules.logger import log_info, log_success, log_warning
import config


# ── Search Space ─────────────────────────────────────────
REPS_OPTIONS = [1, 2, 3]
ENTANGLEMENT_OPTIONS = ["full", "linear", "circular"]
TUNING_SUBSET_SIZE = 28  # Use most of quantum samples for reliable tuning


def _create_tuning_subset(X, y, subset_size=TUNING_SUBSET_SIZE):
    """
    Create a small balanced subset for fast kernel evaluation.

    Parameters
    ----------
    X : np.ndarray
        Feature matrix.
    y : np.ndarray
        Labels (0 or 1).
    subset_size : int
        Total samples (split evenly between classes).

    Returns
    -------
    tuple
        (X_tune_train, X_tune_val, y_tune_train, y_tune_val)
    """
    # Ensure we have enough samples from each class
    half = subset_size // 2
    fraud_idx = np.where(y == 1)[0]
    legit_idx = np.where(y == 0)[0]

    # Sample from each class
    n_fraud = min(half, len(fraud_idx))
    n_legit = min(half, len(legit_idx))

    rng = np.random.RandomState(config.RANDOM_STATE)
    selected_fraud = rng.choice(fraud_idx, n_fraud, replace=False)
    selected_legit = rng.choice(legit_idx, n_legit, replace=False)

    selected = np.concatenate([selected_fraud, selected_legit])
    rng.shuffle(selected)

    X_sub = X[selected]
    y_sub = y[selected]

    # Split into train (70%) and validation (30%)
    split_idx = int(len(X_sub) * 0.7)
    X_tune_train = X_sub[:split_idx]
    y_tune_train = y_sub[:split_idx]
    X_tune_val = X_sub[split_idx:]
    y_tune_val = y_sub[split_idx:]

    return X_tune_train, X_tune_val, y_tune_train, y_tune_val


def _evaluate_config(reps, entanglement, n_features, X_train, X_val, y_train, y_val):
    """
    Evaluate a single ZZFeatureMap configuration.

    Parameters
    ----------
    reps : int
        Number of ZZFeatureMap repetitions.
    entanglement : str
        Entanglement strategy ("full", "linear", "circular").
    n_features : int
        Number of features (qubits).
    X_train, X_val : np.ndarray
        Tuning train/validation feature matrices.
    y_train, y_val : np.ndarray
        Tuning train/validation labels.

    Returns
    -------
    dict
        {reps, entanglement, recall, precision, f1, accuracy, time_s, circuit_depth}
    """
    start = time.time()

    # Create feature map with this config
    feature_map = ZZFeatureMap(
        feature_dimension=n_features,
        reps=reps,
        entanglement=entanglement,
    )
    circuit_depth = feature_map.decompose().depth()

    # Create quantum kernel
    q_kernel = FidelityQuantumKernel(feature_map=feature_map)

    # Compute kernel matrices
    kernel_train = q_kernel.evaluate(x_vec=X_train)
    kernel_val = q_kernel.evaluate(x_vec=X_val, y_vec=X_train)

    # Train SVM on precomputed kernel
    svm = SVC(kernel="precomputed", random_state=config.RANDOM_STATE)
    svm.fit(kernel_train, y_train)

    # Predict on validation
    y_pred = svm.predict(kernel_val)

    elapsed = time.time() - start

    # Compute metrics
    recall = recall_score(y_val, y_pred, zero_division=0)
    precision = precision_score(y_val, y_pred, zero_division=0)
    f1 = f1_score(y_val, y_pred, zero_division=0)
    accuracy = accuracy_score(y_val, y_pred)

    return {
        "reps": reps,
        "entanglement": entanglement,
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "accuracy": accuracy,
        "time_s": round(elapsed, 1),
        "circuit_depth": circuit_depth,
    }


def run_adaptive_tuning(X_quantum, y_quantum):
    """
    Run the adaptive quantum kernel tuning process.

    Tests all combinations of reps × entanglement on a small
    validation subset, selects the configuration that maximizes
    Recall (fraud detection rate), and returns it.

    Parameters
    ----------
    X_quantum : np.ndarray
        Quantum-subset feature matrix (from preprocessing).
    y_quantum : np.ndarray
        Quantum-subset labels.

    Returns
    -------
    dict
        Best configuration: {reps, entanglement, recall, ...}
        Plus 'all_results' key with full leaderboard.
    """
    n_features = X_quantum.shape[1]

    # Create tuning subset
    X_train, X_val, y_train, y_val = _create_tuning_subset(X_quantum, y_quantum)

    log_info(f"Tuning subset: {len(X_train)} train, {len(X_val)} validation")
    log_info(f"Features (qubits): {n_features}")
    log_info(f"Search space: {len(REPS_OPTIONS)} reps × {len(ENTANGLEMENT_OPTIONS)} entanglements = "
             f"{len(REPS_OPTIONS) * len(ENTANGLEMENT_OPTIONS)} configs")

    # ── Header ───────────────────────────────────────────
    width = 60
    print(f"\n  ╔{'═' * width}╗")
    print(f"  ║  {'ADAPTIVE QUANTUM KERNEL TUNING':<{width - 2}}║")
    print(f"  ╠{'═' * width}╣")
    print(f"  ║  {'Testing ZZFeatureMap configurations to maximize':<{width - 2}}║")
    print(f"  ║  {'fraud detection (Recall) in Hilbert space.':<{width - 2}}║")
    print(f"  ╚{'═' * width}╝")

    print(f"\n  {'CONFIG':<25} {'RECALL':>8} {'PREC':>8} {'F1':>8} {'ACC':>8} {'TIME':>7} {'DEPTH':>6}")
    print(f"  {'─' * 72}")

    all_results = []

    for reps in REPS_OPTIONS:
        for entanglement in ENTANGLEMENT_OPTIONS:
            config_name = f"reps={reps}, ent={entanglement}"
            log_info(f"Testing: {config_name}")

            try:
                result = _evaluate_config(
                    reps, entanglement, n_features,
                    X_train, X_val, y_train, y_val,
                )
                all_results.append(result)

                # Highlight best recall with marker
                marker = " ★" if result["recall"] >= 1.0 else ""
                print(f"  reps={reps}, {entanglement:<12}  "
                      f"{result['recall']:>7.4f}  "
                      f"{result['precision']:>7.4f}  "
                      f"{result['f1']:>7.4f}  "
                      f"{result['accuracy']:>7.4f}  "
                      f"{result['time_s']:>5.1f}s  "
                      f"{result['circuit_depth']:>4}  {marker}")

            except Exception as e:
                log_warning(f"Config {config_name} failed: {e}")
                all_results.append({
                    "reps": reps,
                    "entanglement": entanglement,
                    "recall": 0.0, "precision": 0.0,
                    "f1": 0.0, "accuracy": 0.0,
                    "time_s": 0, "circuit_depth": 0,
                })

    print(f"  {'─' * 72}")

    # ── Select Best ─────────────────────────────────────
    # Primary: maximize Recall (fraud detection)
    # Tiebreaker: maximize F1, then minimize time
    best = max(all_results, key=lambda r: (r["recall"], r["f1"], -r["time_s"]))

    best_recall_str = f"{best['recall']:.4f}"
    best_f1_str = f"{best['f1']:.4f}"
    best_reps_str = str(best['reps'])
    best_ent_str = best['entanglement']
    best_depth_str = str(best['circuit_depth'])

    print(f"\n  ╔{'═' * width}╗")
    print(f"  ║  {'OPTIMAL CONFIGURATION SELECTED':<{width - 2}}║")
    print(f"  ╠{'═' * width}╣")
    print(f"  ║  {'Reps:          ' + best_reps_str:<{width - 2}}║")
    print(f"  ║  {'Entanglement:  ' + best_ent_str:<{width - 2}}║")
    print(f"  ║  {'Recall:        ' + best_recall_str:<{width - 2}}║")
    print(f"  ║  {'F1-Score:      ' + best_f1_str:<{width - 2}}║")
    print(f"  ║  {'Circuit Depth: ' + best_depth_str:<{width - 2}}║")
    print(f"  ╚{'═' * width}╝")

    log_success(f"Best config: reps={best['reps']}, entanglement={best['entanglement']} "
                f"(Recall={best['recall']:.4f})")

    best["all_results"] = all_results
    return best
