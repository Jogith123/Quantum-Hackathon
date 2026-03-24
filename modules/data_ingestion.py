"""
Module 1: Data Ingestion
=========================
Load the Kaggle creditcard.csv dataset into a pandas DataFrame.
"""

import pandas as pd
import os
from modules.logger import log_info, log_success, log_warning


def load_dataset(filepath):
    """
    Load the credit card transaction dataset from a CSV file.

    Parameters
    ----------
    filepath : str
        Path to the creditcard.csv file.

    Returns
    -------
    pd.DataFrame
        Raw dataframe with all columns.

    Raises
    ------
    FileNotFoundError
        If the dataset file does not exist.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"\n  ✗ Dataset not found at: {filepath}\n"
            f"  ➤ Please download 'creditcard.csv' from:\n"
            f"    https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud\n"
            f"  ➤ Place it in the 'data/' folder and try again.\n"
        )

    df = pd.read_csv(filepath)

    log_success(f"Dataset loaded: {filepath}")
    log_info(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    log_info(f"Fraud cases: {df['Class'].sum()} / {len(df)} "
             f"({df['Class'].mean() * 100:.3f}%)")

    return df
