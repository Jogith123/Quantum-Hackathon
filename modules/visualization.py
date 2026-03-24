"""
Module 10: Visualization
==========================
Generate confusion matrix heatmaps and comparison bar charts.
All plots are saved to the outputs/ directory.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for saving
import matplotlib.pyplot as plt
import seaborn as sns
from modules.logger import log_info, log_success
import config


# ── Style Configuration ─────────────────────────────────
plt.style.use("dark_background")
COLORS = {
    "classical": "#4FC3F7",   # Light blue
    "qsvm": "#AB47BC",        # Purple
    "accent": "#66BB6A",      # Green
}


def plot_confusion_matrix(cm, title, filename):
    """
    Plot and save a confusion matrix heatmap.

    Parameters
    ----------
    cm : np.ndarray
        2×2 confusion matrix.
    title : str
        Plot title.
    filename : str
        Output filename (saved to OUTPUT_DIR).
    """
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(config.OUTPUT_DIR, filename)

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="coolwarm",
        xticklabels=["Legit", "Fraud"],
        yticklabels=["Legit", "Fraud"],
        linewidths=1,
        linecolor="gray",
        cbar_kws={"shrink": 0.8},
        ax=ax,
    )
    ax.set_xlabel("Predicted", fontsize=12, fontweight="bold")
    ax.set_ylabel("Actual", fontsize=12, fontweight="bold")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close(fig)

    log_info(f"Saved: {filepath}")


def plot_comparison_chart(classical_metrics, qsvm_metrics, filename="comparison_chart.png"):
    """
    Generate a grouped bar chart comparing Classical SVM vs QSVM.

    Parameters
    ----------
    classical_metrics : dict
        Metrics dict for Classical SVM.
    qsvm_metrics : dict
        Metrics dict for QSVM.
    filename : str
        Output filename.
    """
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(config.OUTPUT_DIR, filename)

    metrics = ["Accuracy", "Precision", "Recall", "F1-Score"]
    keys = ["accuracy", "precision", "recall", "f1_score"]

    classical_vals = [classical_metrics[k] for k in keys]
    qsvm_vals = [qsvm_metrics[k] for k in keys]

    x = np.arange(len(metrics))
    width = 0.32

    fig, ax = plt.subplots(figsize=(10, 6))

    bars1 = ax.bar(x - width / 2, classical_vals, width,
                   label="Classical SVM", color=COLORS["classical"],
                   edgecolor="white", linewidth=0.5, alpha=0.9)
    bars2 = ax.bar(x + width / 2, qsvm_vals, width,
                   label="QSVM", color=COLORS["qsvm"],
                   edgecolor="white", linewidth=0.5, alpha=0.9)

    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                f"{height:.3f}", ha="center", va="bottom",
                fontsize=9, fontweight="bold", color=COLORS["classical"])

    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                f"{height:.3f}", ha="center", va="bottom",
                fontsize=9, fontweight="bold", color=COLORS["qsvm"])

    ax.set_xlabel("Metric", fontsize=12, fontweight="bold")
    ax.set_ylabel("Score", fontsize=12, fontweight="bold")
    ax.set_title("Q-Shield: Classical SVM vs QSVM Performance",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11)
    ax.legend(fontsize=11, loc="lower right")
    ax.set_ylim(0, 1.15)
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close(fig)

    log_info(f"Saved: {filepath}")


def plot_fraud_detection_insight(classical_cm, qsvm_cm, filename="fraud_detection_insight.png"):
    """
    Generate a grouped bar chart explicitly comparing Detected vs Missed Fraud.
    """
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(config.OUTPUT_DIR, filename)

    # cm structure: [[TN, FP], [FN, TP]]
    c_fn, c_tp = classical_cm[1, 0], classical_cm[1, 1]
    q_fn, q_tp = qsvm_cm[1, 0], qsvm_cm[1, 1]

    categories = ["Detected Fraud\n(Higher is Better)", "Missed Fraud\n(Lower is Better)"]
    c_vals = [c_tp, c_fn]
    q_vals = [q_tp, q_fn]

    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))

    bars1 = ax.bar(x - width / 2, c_vals, width,
                   label="Classical SVM", color=COLORS["classical"], alpha=0.9)
    bars2 = ax.bar(x + width / 2, q_vals, width,
                   label="QSVM", color=COLORS["accent"], alpha=0.9)  # Accent color for emphasis

    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height,
                f"{int(height)}", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color="white")

    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height,
                f"{int(height)}", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color="white")

    ax.set_ylabel("Number of Transactions", fontsize=12, fontweight="bold")
    ax.set_title("Fraud-First Insight: Missed Fraud vs Detected Fraud", 
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11, fontweight="bold")
    ax.legend(fontsize=11)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close(fig)

    log_info(f"Saved: {filepath}")


def generate_all_visualizations(classical_metrics, qsvm_metrics):
    """
    Generate all visualization plots.

    Parameters
    ----------
    classical_metrics : dict
        Must contain 'confusion_matrix' key.
    qsvm_metrics : dict
        Must contain 'confusion_matrix' key.
    """
    # Confusion matrices
    plot_confusion_matrix(
        classical_metrics["confusion_matrix"],
        "Classical SVM — Confusion Matrix",
        "classical_confusion_matrix.png"
    )
    plot_confusion_matrix(
        qsvm_metrics["confusion_matrix"],
        "QSVM — Confusion Matrix",
        "qsvm_confusion_matrix.png"
    )

    # Comparison bar chart
    plot_comparison_chart(classical_metrics, qsvm_metrics)

    # Fraud-first insight chart
    plot_fraud_detection_insight(
        classical_metrics["confusion_matrix"], 
        qsvm_metrics["confusion_matrix"]
    )

    log_success("All visualizations generated")
