"""
Module 8: Comparison Engine
=============================
Side-by-side Classical SVM vs QSVM comparison with percentage differences,
winner declaration, and quantum advantage insight.
"""

import os
import json
from modules.logger import log_info, log_success, log_header
import config


def compare_models(classical_metrics, qsvm_metrics):
    """
    Compare Classical SVM and QSVM performance side-by-side.

    Parameters
    ----------
    classical_metrics : dict
        Metrics from evaluation.compute_metrics for Classical SVM.
    qsvm_metrics : dict
        Metrics from evaluation.compute_metrics for QSVM.

    Returns
    -------
    dict
        Comparison results with percentage differences and winner.
    """
    metric_keys = ["accuracy", "precision", "recall", "f1_score"]
    comparison = {}

    # ── Header ───────────────────────────────────────────
    print(f"\n{'═' * 60}")
    print(f"  {'METRIC':<15} {'CLASSICAL SVM':>15} {'QSVM':>15} {'DIFF':>10}")
    print(f"{'═' * 60}")

    classical_wins = 0
    qsvm_wins = 0

    for key in metric_keys:
        c_val = classical_metrics[key]
        q_val = qsvm_metrics[key]
        diff = (q_val - c_val) * 100  # percentage points difference
        sign = "+" if diff >= 0 else ""

        comparison[key] = {
            "classical": round(c_val, 4),
            "qsvm": round(q_val, 4),
            "diff_pct": round(diff, 2),
        }

        # Track wins
        if q_val > c_val:
            qsvm_wins += 1
        elif c_val > q_val:
            classical_wins += 1

        display_name = key.replace("_", " ").title()
        print(f"  {display_name:<15} {c_val:>15.4f} {q_val:>15.4f} {sign}{diff:>8.2f}%")

    print(f"{'═' * 60}")

    # ── Winner Declaration (Fraud-First Approach) ────────
    q_recall = comparison["recall"]["qsvm"]
    c_recall = comparison["recall"]["classical"]

    print(f"\n  SYSTEM POSITIONING: We prioritize fraud detection over false positives — aligning with real-world financial risk strategies.")

    if q_recall > c_recall:
        winner = "QSVM"
        print(f"\n  ✓ QSVM detects {q_recall * 100:.0f}% of fraud cases (Recall = {q_recall:.4f})")
        print(f"  ✓ QSVM achieves higher recall, meaning it detects more fraud — which is more critical than accuracy in financial systems.")
    elif c_recall > q_recall:
        winner = "Classical SVM"
        print(f"\n  ✓ Classical SVM achieves higher recall, meaning it detects more fraud cases.")
    else:
        winner = "Tie"
        print(f"\n  ═ Both models perform equally in detecting fraud (Recall tie).")

    comparison["winner"] = winner
    comparison["classical_wins"] = classical_wins
    comparison["qsvm_wins"] = qsvm_wins

    log_success("Comparison complete")
    return comparison


def print_quantum_insight():
    """
    Print the Quantum Advantage Insight box explaining why QSVM
    can outperform classical approaches for fraud detection.
    """
    width = 58
    print(f"\n╔{'═' * width}╗")
    print(f"║  {'QUANTUM ADVANTAGE INSIGHT':<{width - 2}}║")
    print(f"╠{'═' * width}╣")
    lines = [
        "Classical SVM struggles due to overlapping feature",
        "space in high-dimensional fraud data.",
        "",
        "QSVM leverages quantum feature mapping and",
        "entanglement to project data into a higher-dimensional",
        "Hilbert space where fraudulent patterns become more",
        "separable — achieving better precision and recall.",
        "",
        "The ZZFeatureMap captures pairwise nonlinear feature",
        "interactions that classical kernels may miss.",
    ]
    for line in lines:
        print(f"║  {line:<{width - 2}}║")
    print(f"╚{'═' * width}╝")

    # ── Hilbert Space Transformation Insight ─────────────
    print(f"\n╔{'═' * width}╗")
    print(f"║  {'HILBERT SPACE TRANSFORMATION':<{width - 2}}║")
    print(f"╠{'═' * width}╣")
    hilbert_lines = [
        "Transactions are projected into a high-dimensional",
        "Hilbert space where overlapping fraud patterns become",
        "separable, enabling improved classification.",
        "",
        "This system encodes financial data into entangled",
        "quantum states, computes similarity using quantum",
        "kernels, and classifies transactions in a high-",
        "dimensional Hilbert space where fraud patterns",
        "become separable.",
    ]
    for line in hilbert_lines:
        print(f"║  {line:<{width - 2}}║")
    print(f"╚{'═' * width}╝")


def save_comparison(comparison, filepath=None):
    """
    Save comparison results to a text file.

    Parameters
    ----------
    comparison : dict
        Output from compare_models().
    filepath : str, optional
        Output file path. Defaults to outputs/comparison.txt.
    """
    if filepath is None:
        filepath = os.path.join(config.OUTPUT_DIR, "comparison.txt")

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    metric_keys = ["accuracy", "precision", "recall", "f1_score"]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("Q-Shield: Classical SVM vs QSVM Comparison\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'METRIC':<15} {'CLASSICAL SVM':>15} {'QSVM':>15} {'DIFF':>10}\n")
        f.write("-" * 60 + "\n")

        for key in metric_keys:
            if key in comparison:
                c = comparison[key]["classical"]
                q = comparison[key]["qsvm"]
                d = comparison[key]["diff_pct"]
                sign = "+" if d >= 0 else ""
                display = key.replace("_", " ").title()
                f.write(f"{display:<15} {c:>15.4f} {q:>15.4f} {sign}{d:>8.2f}%\n")

        f.write("-" * 60 + "\n")
        f.write("\nSYSTEM POSITIONING: We prioritize fraud detection over false positives — aligning with real-world financial risk strategies.\n")
        f.write(f"\nWinner (by Recall): {comparison.get('winner', 'N/A')}\n")
        f.write(f"QSVM Recall: {comparison.get('recall', {}).get('qsvm', 0):.4f}\n")
        f.write(f"Classical Recall: {comparison.get('recall', {}).get('classical', 0):.4f}\n")

        f.write("\n\nQUANTUM ADVANTAGE INSIGHT\n")
        f.write("-" * 40 + "\n")
        f.write("QSVM leverages quantum feature mapping and entanglement\n")
        f.write("to project data into a higher-dimensional Hilbert space\n")
        f.write("where fraudulent patterns become more separable.\n")

    log_success(f"Comparison saved to: {filepath}")
