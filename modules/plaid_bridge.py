"""
Module 12: Plaid Sandbox Bridge
=================================
Connects to Plaid Sandbox API and bridges real bank transaction
data into the Q-Shield quantum feature format (V1-V28 + Amount).

Architecture:
  Plaid Sandbox → connect_sandbox() → access_token
  access_token → fetch_transactions() → list[PlaidTransaction]
  PlaidTransaction → bridge_to_quantum() → {V1..V28, Amount}

The bridge uses deterministic hashing so the same merchant always
maps to the same V1-V28 features for consistent quantum analysis.
"""

import hashlib
import math
import requests
from modules.logger import log_info, log_success, log_warning
import config


class PlaidBridge:
    """
    Handles Plaid Sandbox authentication and transaction fetching,
    plus the critical data bridge from Plaid format → Quantum format.
    """

    def __init__(self):
        self.access_token = None
        self.credentials = {
            "client_id": config.PLAID_CLIENT_ID,
            "secret": config.PLAID_SECRET,
        }

    def connect_sandbox(self, institution_id="ins_109508"):
        """
        Connect to a Plaid Sandbox test institution.

        Flow:
          1. Create a sandbox public token (bypasses Plaid Link UI)
          2. Exchange it for a permanent access token

        Parameters
        ----------
        institution_id : str
            Plaid sandbox institution ID. Default is "ins_109508"
            (First Platypus Bank — provides test transactions).

        Returns
        -------
        dict
            Connection status with access token info.
        """
        log_info("Connecting to Plaid Sandbox...")

        # Step 1: Create sandbox public token
        create_res = requests.post(
            f"{config.PLAID_ENV_URL}/sandbox/public_token/create",
            json={
                **self.credentials,
                "institution_id": institution_id,
                "initial_products": ["transactions"],
            },
            timeout=30,
        )

        if create_res.status_code != 200:
            error = create_res.json().get("error_message", create_res.text)
            raise ConnectionError(f"Plaid sandbox token creation failed: {error}")

        public_token = create_res.json()["public_token"]
        log_info(f"Public token created: {public_token[:20]}...")

        # Step 2: Exchange for access token
        exchange_res = requests.post(
            f"{config.PLAID_ENV_URL}/item/public_token/exchange",
            json={
                **self.credentials,
                "public_token": public_token,
            },
            timeout=30,
        )

        if exchange_res.status_code != 200:
            error = exchange_res.json().get("error_message", exchange_res.text)
            raise ConnectionError(f"Plaid token exchange failed: {error}")

        self.access_token = exchange_res.json()["access_token"]
        item_id = exchange_res.json()["item_id"]

        log_success(f"Connected to Plaid Sandbox (item: {item_id[:15]}...)")

        return {
            "status": "connected",
            "institution_id": institution_id,
            "item_id": item_id,
            "message": "Plaid Sandbox bank account connected successfully",
        }

    def fetch_transactions(self):
        """
        Fetch transactions from the connected Plaid Sandbox account.

        Uses the /transactions/sync endpoint for the latest data.

        Returns
        -------
        list[dict]
            List of raw Plaid transaction objects.
        """
        if not self.access_token:
            raise RuntimeError(
                "Not connected. Call /plaid/connect first."
            )

        log_info("Fetching transactions from Plaid...")

        sync_res = requests.post(
            f"{config.PLAID_ENV_URL}/transactions/sync",
            json={
                **self.credentials,
                "access_token": self.access_token,
            },
            timeout=30,
        )

        if sync_res.status_code != 200:
            error = sync_res.json().get("error_message", sync_res.text)
            raise ConnectionError(f"Plaid transaction sync failed: {error}")

        data = sync_res.json()
        transactions = data.get("added", [])

        log_success(f"Fetched {len(transactions)} transactions from Plaid")

        # Format for readability
        formatted = []
        for tx in transactions:
            formatted.append({
                "transaction_id": tx.get("transaction_id", ""),
                "merchant": tx.get("merchant_name") or tx.get("name", "Unknown"),
                "amount": abs(tx.get("amount", 0.0)),
                "date": tx.get("date", ""),
                "category": tx.get("personal_finance_category", {}).get("primary", "UNKNOWN"),
                "payment_channel": tx.get("payment_channel", "unknown"),
                "pending": tx.get("pending", False),
            })

        return formatted

    @staticmethod
    def bridge_to_quantum(plaid_transaction):
        """
        Bridge a single Plaid transaction to quantum-compatible format.

        Uses deterministic hashing so the same merchant always
        produces the same V1-V28 features.

        Parameters
        ----------
        plaid_transaction : dict
            Must have 'merchant' and 'amount' keys.

        Returns
        -------
        dict
            {V1: float, V2: float, ..., V28: float, Amount: float}
        """
        # ── Input Validation ─────────────────────────────
        if not isinstance(plaid_transaction, dict):
            raise ValueError("Transaction must be a dictionary")

        merchant = str(plaid_transaction.get("merchant") or "Unknown")
        category = str(plaid_transaction.get("category") or "UNKNOWN")
        channel = str(plaid_transaction.get("payment_channel") or "unknown")

        try:
            amount = abs(float(plaid_transaction.get("amount", 0.0) or 0.0))
        except (TypeError, ValueError):
            amount = 0.0

        # Create a deterministic seed from merchant + category + channel
        seed_str = f"{merchant}:{category}:{channel}"
        hash_bytes = hashlib.sha256(seed_str.encode()).digest()

        # Generate 28 deterministic V-features from the hash
        quantum_features = {}
        for i in range(28):
            # Use different byte pairs for each feature
            byte_idx = i % len(hash_bytes)
            byte_val = hash_bytes[byte_idx]
            next_byte = hash_bytes[(byte_idx + 1) % len(hash_bytes)]

            # Map to range [-3.0, 3.0] (matching Kaggle dataset distribution)
            raw = ((byte_val * 256 + next_byte) / 65535.0) * 6.0 - 3.0

            # Add slight variation per feature index using sin/cos
            variation = math.sin(i * 0.7 + byte_val * 0.01) * 0.5
            quantum_features[f"V{i + 1}"] = round(raw + variation, 4)

        # Amount is used directly (real Plaid value)
        quantum_features["Amount"] = round(amount, 2)

        return quantum_features
