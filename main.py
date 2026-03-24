"""
Q-Shield: Adaptive Quantum Kernel Learning for Financial Fraud Detection
=========================================================================
Main entry point — runs the full 12-step pipeline + saves models for real-time API.

  ⚛️ Layer 1 (OFFLINE — this script):
    1.  Data Ingestion
    2.  Data Preprocessing
    3.  Classical SVM Training & Evaluation
    4.  Adaptive Quantum Kernel Tuning (NEW)
    5.  Quantum Feature Encoding (uses tuned config)
    6.  Quantum Kernel Computation
    7.  QSVM Training & Evaluation
    8.  Model Evaluation (consolidated metrics)
    9.  Comparison Engine
   10.  Prediction Demo
   11.  Visualization
   12.  Save Models (for real-time API)

  ⚡ Layer 2 (ONLINE — api.py):
    Uses saved models for instant predictions without retraining.
"""

import os
import sys
import json
import joblib

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from modules.logger import log_step, log_info, log_success, log_header
from modules.data_ingestion import load_dataset
from modules.data_preprocessing import preprocess
from modules.classical_model import train_classical_svm, evaluate_classical_svm
from modules.quantum_encoding import create_feature_map
from modules.quantum_kernel import create_quantum_kernel, compute_kernel_matrices
from modules.qsvm_model import train_qsvm, evaluate_qsvm
from modules.evaluation import compute_metrics, print_evaluation_report
from modules.comparison import compare_models, print_quantum_insight, save_comparison
from modules.prediction import demo_prediction
from modules.visualization import generate_all_visualizations
from modules.adaptive_tuning import run_adaptive_tuning


def save_models(qsvm_model, classical_model, scaler, pca, X_train_q,
                feature_map_config):
    """
    Save all trained models and artifacts to disk for the real-time API.

    Parameters
    ----------
    qsvm_model : SVC
        Trained QSVM model.
    classical_model : SVC
        Trained classical SVM model.
    scaler : StandardScaler
        Fitted scaler.
    pca : PCA
        Fitted PCA transformer.
    X_train_q : np.ndarray
        Quantum training subset (reference data for kernel computation).
    feature_map_config : dict
        Config to reconstruct the ZZFeatureMap.
    """
    os.makedirs(config.MODELS_DIR, exist_ok=True)

    joblib.dump(qsvm_model, config.QSVM_MODEL_PATH)
    joblib.dump(classical_model, config.CLASSICAL_MODEL_PATH)
    joblib.dump(scaler, config.SCALER_PATH)
    joblib.dump(pca, config.PCA_PATH)
    joblib.dump(X_train_q, config.TRAINING_DATA_PATH)

    with open(config.FEATURE_MAP_CONFIG_PATH, "w") as f:
        json.dump(feature_map_config, f, indent=2)

    log_success("All models saved for real-time API")
    log_info(f"Models directory: {config.MODELS_DIR}")
    log_info(f"Files: qsvm_model.joblib, classical_model.joblib, "
             f"scaler.joblib, pca.joblib, training_data.joblib, "
             f"feature_map_config.json")


def main():
    """Run the complete Q-Shield pipeline."""

    # ── Banner ───────────────────────────────────────────
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║        Q-SHIELD: Quantum Fraud Detection Engine         ║")
    print("║   Quantum Feature Mapping-Based Real-Time Detection     ║")
    print("╚══════════════════════════════════════════════════════════╝")

    if config.DEMO_MODE:
        print("\n  ⚡ Running in DEMO MODE (fast execution)")
        print(f"     Quantum samples: {config.QUANTUM_SAMPLE_SIZE}")
        print(f"     ZZFeatureMap reps: {config.ZZ_REPS}")
    else:
        print("\n  🔬 Running in FULL MODE (production pipeline)")
        print(f"     Quantum samples: {config.QUANTUM_SAMPLE_SIZE}")
        print(f"     ZZFeatureMap reps: {config.ZZ_REPS}")

    # Ensure output directory exists
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # ═══════════════════════════════════════════════════════
    # STEP 1: Data Ingestion
    # ═══════════════════════════════════════════════════════
    log_step(1, "Data Ingestion")
    df = load_dataset(config.DATASET_PATH)

    # ═══════════════════════════════════════════════════════
    # STEP 2: Data Preprocessing
    # ═══════════════════════════════════════════════════════
    log_step(2, "Data Preprocessing")
    data = preprocess(df)

    # ═══════════════════════════════════════════════════════
    # STEP 3: Classical SVM Training
    # ═══════════════════════════════════════════════════════
    log_step(3, "Classical SVM Training")
    classical_model = train_classical_svm(data["X_train"], data["y_train"])
    classical_results = evaluate_classical_svm(
        classical_model, data["X_test"], data["y_test"]
    )

    # ═══════════════════════════════════════════════════════
    # STEP 4: Adaptive Quantum Kernel Tuning
    # ═══════════════════════════════════════════════════════
    log_step(4, "Adaptive Quantum Kernel Tuning")
    tuning_result = run_adaptive_tuning(data["X_train_q"], data["y_train_q"])
    tuned_reps = tuning_result["reps"]
    tuned_entanglement = tuning_result["entanglement"]

    # Save tuning leaderboard for frontend dashboard
    tuning_output = {
        "best": {
            "reps": tuned_reps,
            "entanglement": tuned_entanglement,
            "recall": tuning_result["recall"],
            "precision": tuning_result["precision"],
            "f1": tuning_result["f1"],
            "accuracy": tuning_result["accuracy"],
            "time_s": tuning_result["time_s"],
            "circuit_depth": tuning_result["circuit_depth"],
        },
        "all_results": [
            {k: v for k, v in r.items() if k != "all_results"}
            for r in tuning_result.get("all_results", [])
        ],
    }
    tuning_path = os.path.join(config.OUTPUT_DIR, "tuning_results.json")
    with open(tuning_path, "w") as f:
        json.dump(tuning_output, f, indent=2)
    log_success(f"Tuning leaderboard saved to: {tuning_path}")

    # ═══════════════════════════════════════════════════════
    # STEP 5: Quantum Feature Encoding (Tuned Config)
    # ═══════════════════════════════════════════════════════
    log_step(5, "Quantum Feature Encoding (Tuned)")
    # Apply tuned entanglement for feature map creation
    original_entanglement = config.ENTANGLEMENT
    config.ENTANGLEMENT = tuned_entanglement
    feature_map = create_feature_map(reps=tuned_reps)
    config.ENTANGLEMENT = original_entanglement  # restore

    # ═══════════════════════════════════════════════════════
    # STEP 6: Quantum Kernel Computation
    # ═══════════════════════════════════════════════════════
    log_step(6, "Quantum Kernel Computation")
    q_kernel = create_quantum_kernel(feature_map)
    kernel_train, kernel_test = compute_kernel_matrices(
        q_kernel, data["X_train_q"], data["X_test_q"]
    )

    # ═══════════════════════════════════════════════════════
    # STEP 7: QSVM Training
    # ═══════════════════════════════════════════════════════
    log_step(7, "QSVM Training")
    qsvm_model = train_qsvm(kernel_train, data["y_train_q"])
    qsvm_results = evaluate_qsvm(qsvm_model, kernel_test, data["y_test_q"])

    # ═══════════════════════════════════════════════════════
    # STEP 8: Model Evaluation
    # ═══════════════════════════════════════════════════════
    log_step(8, "Model Evaluation")

    classical_metrics = compute_metrics(data["y_test"], classical_results["y_pred"])
    qsvm_metrics = compute_metrics(data["y_test_q"], qsvm_results["y_pred"])

    print_evaluation_report(classical_metrics, "Classical SVM")
    print_evaluation_report(qsvm_metrics, "QSVM")

    # Save metrics to JSON
    metrics_output = {
        "classical_svm": {
            "accuracy": classical_metrics["accuracy"],
            "precision": classical_metrics["precision"],
            "recall": classical_metrics["recall"],
            "f1_score": classical_metrics["f1_score"],
        },
        "qsvm": {
            "accuracy": qsvm_metrics["accuracy"],
            "precision": qsvm_metrics["precision"],
            "recall": qsvm_metrics["recall"],
            "f1_score": qsvm_metrics["f1_score"],
        },
    }
    metrics_path = os.path.join(config.OUTPUT_DIR, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics_output, f, indent=2)
    log_success(f"Metrics saved to: {metrics_path}")

    # ═══════════════════════════════════════════════════════
    # STEP 9: Comparison Engine
    # ═══════════════════════════════════════════════════════
    log_step(9, "Comparison Engine")
    comparison = compare_models(classical_metrics, qsvm_metrics)
    print_quantum_insight()
    save_comparison(comparison)

    # ═══════════════════════════════════════════════════════
    # STEP 10: Prediction Demo
    # ═══════════════════════════════════════════════════════
    log_step(10, "Prediction Demo")
    prediction_result = demo_prediction(
        qsvm_model, kernel_test, data["y_test_q"]
    )

    # ═══════════════════════════════════════════════════════
    # STEP 11: Visualization
    # ═══════════════════════════════════════════════════════
    log_step(11, "Visualization")
    generate_all_visualizations(classical_metrics, qsvm_metrics)

    # ═══════════════════════════════════════════════════════
    # STEP 12: Save Models for Real-Time API
    # ═══════════════════════════════════════════════════════
    log_step(12, "Saving Models for Real-Time API")
    feature_map_config = {
        "feature_dimension": config.N_PCA_COMPONENTS,
        "reps": tuned_reps,
        "entanglement": tuned_entanglement,
        "tuning_recall": tuning_result["recall"],
    }
    save_models(
        qsvm_model=qsvm_model,
        classical_model=classical_model,
        scaler=data["scaler"],
        pca=data["pca"],
        X_train_q=data["X_train_q"],
        feature_map_config=feature_map_config,
    )

    # ── Final Quantum Summary ────────────────────────────
    print("\n")
    width = 58
    print(f"╔{'═' * width}╗")
    print(f"║  {'Q-SHIELD PIPELINE COMPLETE':<{width - 2}}║")
    print(f"╠{'═' * width}╣")

    summary_lines = [
        "",
        "Q-Shield uses quantum feature mapping, entanglement,",
        "and kernel-based learning to detect fraud patterns",
        "beyond classical systems.",
        "",
        "REPRESENTATION ADVANTAGE:",
        "  ZZFeatureMap encodes transactions into quantum states",
        "",
        "SIMILARITY ADVANTAGE:",
        "  FidelityQuantumKernel computes quantum state overlap",
        "",
        "SEPARATION ADVANTAGE:",
        "  QSVM finds optimal boundary in Hilbert space",
        "",
    ]
    for line in summary_lines:
        print(f"║  {line:<{width - 2}}║")
    print(f"╚{'═' * width}╝")

    # ── Output Files ─────────────────────────────────────
    print(f"\n  Output files saved to: {config.OUTPUT_DIR}/")
    print(f"    ├── metrics.json")
    print(f"    ├── comparison.txt")
    print(f"    ├── classical_confusion_matrix.png")
    print(f"    ├── qsvm_confusion_matrix.png")
    print(f"    ├── comparison_chart.png")
    print(f"    ├── fraud_detection_insight.png")
    print(f"    ├── kernel_train.npy  (cached)")
    print(f"    ├── kernel_test.npy   (cached)")
    print(f"    └── models/")
    print(f"        ├── qsvm_model.joblib")
    print(f"        ├── classical_model.joblib")
    print(f"        ├── scaler.joblib")
    print(f"        ├── pca.joblib")
    print(f"        ├── training_data.joblib")
    print(f"        └── feature_map_config.json")

    # ── Real-Time API Hint ───────────────────────────────
    print(f"\n  {'━' * 50}")
    print(f"  ⚡ To start the real-time prediction API:")
    print(f"     python api.py")
    print(f"  📖 API docs: http://localhost:{config.API_PORT}/docs")
    print(f"  {'━' * 50}\n")


if __name__ == "__main__":
    main()
