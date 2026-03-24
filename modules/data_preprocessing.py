"""
Module 2: Data Preprocessing
==============================
Normalize, handle class imbalance, reduce dimensions, and split data.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from modules.logger import log_info, log_success
import config


def preprocess(df):
    """
    Full preprocessing pipeline for credit card data.

    Steps:
        1. Drop 'Time' column
        2. StandardScaler on 'Amount'
        3. Random undersampling (balance classes)
        4. PCA dimensionality reduction
        5. Stratified train/test split
        6. (Optional) Subsample for quantum feasibility

    Parameters
    ----------
    df : pd.DataFrame
        Raw dataset from data_ingestion.

    Returns
    -------
    dict
        Dictionary with keys:
        - X_train, X_test, y_train, y_test (full balanced set)
        - X_train_q, X_test_q, y_train_q, y_test_q (quantum subset)
        - scaler: fitted StandardScaler
        - pca: fitted PCA
    """
    # ── Step 1: Drop Time column ─────────────────────────
    df = df.drop(columns=["Time"], errors="ignore")
    log_info("Dropped 'Time' column")

    # ── Step 2: Normalize Amount ─────────────────────────
    scaler = StandardScaler()
    df["Amount"] = scaler.fit_transform(df[["Amount"]])
    log_info("Normalized 'Amount' column (StandardScaler)")

    # ── Step 3: Handle class imbalance (undersampling) ───
    fraud = df[df["Class"] == 1]
    legit = df[df["Class"] == 0]

    legit_undersampled = legit.sample(n=len(fraud), random_state=config.RANDOM_STATE)
    balanced_df = pd.concat([fraud, legit_undersampled]).sample(
        frac=1, random_state=config.RANDOM_STATE
    ).reset_index(drop=True)

    log_info(f"Undersampled: {len(fraud)} fraud + {len(legit_undersampled)} legit "
             f"= {len(balanced_df)} total")

    # ── Step 4: Separate features and labels ─────────────
    X = balanced_df.drop(columns=["Class"]).values
    y = balanced_df["Class"].values

    # ── Step 5: PCA Dimensionality Reduction ─────────────
    pca = PCA(n_components=config.N_PCA_COMPONENTS, random_state=config.RANDOM_STATE)
    X_pca = pca.fit_transform(X)

    variance_explained = sum(pca.explained_variance_ratio_) * 100
    log_info(f"PCA: {X.shape[1]} features → {config.N_PCA_COMPONENTS} components "
             f"({variance_explained:.1f}% variance retained)")

    # ── Step 6: Train/Test Split ─────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X_pca, y,
        test_size=config.TEST_SIZE,
        random_state=config.RANDOM_STATE,
        stratify=y
    )
    log_info(f"Train/Test split: {len(X_train)} train, {len(X_test)} test")

    # ── Step 7: Quantum Subset (smaller for kernel speed) ─
    q_size = min(config.QUANTUM_SAMPLE_SIZE, len(X_train))
    q_test_size = max(int(q_size * config.TEST_SIZE), 10)

    # Stratified subsample for quantum
    X_train_q, _, y_train_q, _ = train_test_split(
        X_train, y_train,
        train_size=q_size,
        random_state=config.RANDOM_STATE,
        stratify=y_train
    )
    X_test_q, _, y_test_q, _ = train_test_split(
        X_test, y_test,
        train_size=q_test_size,
        random_state=config.RANDOM_STATE,
        stratify=y_test
    )

    log_info(f"Quantum subset: {len(X_train_q)} train, {len(X_test_q)} test")
    log_success("Preprocessing complete")

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "X_train_q": X_train_q,
        "X_test_q": X_test_q,
        "y_train_q": y_train_q,
        "y_test_q": y_test_q,
        "scaler": scaler,
        "pca": pca,
    }
