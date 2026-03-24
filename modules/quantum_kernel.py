"""
Module 5: Quantum Kernel Computation
======================================
Compute quantum kernel matrices using FidelityQuantumKernel.
Includes kernel caching to avoid recomputation.
"""

import os
import numpy as np
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from modules.logger import log_info, log_success, log_warning
import config


def create_quantum_kernel(feature_map):
    """
    Create a FidelityQuantumKernel from the given feature map.

    Parameters
    ----------
    feature_map : ZZFeatureMap
        Quantum feature map for encoding.

    Returns
    -------
    FidelityQuantumKernel
        Configured quantum kernel.
    """
    kernel = FidelityQuantumKernel(feature_map=feature_map)
    log_success("FidelityQuantumKernel created")
    return kernel


def compute_kernel_matrices(kernel, X_train, X_test):
    """
    Compute quantum kernel matrices with caching support.

    If cached .npy files exist in outputs/, loads them.
    Otherwise computes fresh and saves to cache.

    Parameters
    ----------
    kernel : FidelityQuantumKernel
        The quantum kernel object.
    X_train : np.ndarray
        Training feature vectors.
    X_test : np.ndarray
        Testing feature vectors.

    Returns
    -------
    tuple (np.ndarray, np.ndarray)
        kernel_matrix_train (N×N), kernel_matrix_test (M×N)
    """
    # Ensure output directory exists
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # ── Check cache ──────────────────────────────────────
    if (os.path.exists(config.KERNEL_TRAIN_CACHE) and
            os.path.exists(config.KERNEL_TEST_CACHE)):
        kernel_train = np.load(config.KERNEL_TRAIN_CACHE)
        kernel_test = np.load(config.KERNEL_TEST_CACHE)

        # Validate shapes match current data
        if (kernel_train.shape == (len(X_train), len(X_train)) and
                kernel_test.shape == (len(X_test), len(X_train))):
            log_success("Loaded cached quantum kernel matrices")
            log_info(f"Train kernel: {kernel_train.shape} | Test kernel: {kernel_test.shape}")
            return kernel_train, kernel_test
        else:
            log_warning("Cached kernel shapes don't match data — recomputing")

    # ── Compute kernels ──────────────────────────────────
    log_info(f"Computing quantum kernel matrices...")
    log_info(f"Train: {X_train.shape[0]}×{X_train.shape[0]} | "
             f"Test: {X_test.shape[0]}×{X_train.shape[0]}")

    kernel_train = kernel.evaluate(x_vec=X_train)
    log_info("Train kernel computed")

    kernel_test = kernel.evaluate(x_vec=X_test, y_vec=X_train)
    log_info("Test kernel computed")

    # ── Save to cache ────────────────────────────────────
    np.save(config.KERNEL_TRAIN_CACHE, kernel_train)
    np.save(config.KERNEL_TEST_CACHE, kernel_test)
    log_success("Computed and saved quantum kernel matrices")
    log_info(f"Cached to: {config.KERNEL_TRAIN_CACHE}")

    return kernel_train, kernel_test
