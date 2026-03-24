"""
Module 4: Quantum Feature Encoding
====================================
Encode classical feature vectors into quantum states using ZZFeatureMap.
"""

from qiskit.circuit.library import ZZFeatureMap
from modules.logger import log_info, log_success
import config


def create_feature_map(n_features=None, reps=None):
    """
    Create a ZZFeatureMap quantum circuit for feature encoding.

    The ZZFeatureMap applies:
    - Hadamard gates on all qubits
    - Single-qubit Z-rotations parameterized by feature values
    - Two-qubit ZZ-entangling gates for pairwise feature interactions
    - Repeated for 'reps' layers

    Parameters
    ----------
    n_features : int, optional
        Number of features (qubits). Defaults to config.N_PCA_COMPONENTS.
    reps : int, optional
        Number of repetitions. Defaults to config.ZZ_REPS.

    Returns
    -------
    ZZFeatureMap
        Configured quantum feature map circuit.
    """
    if n_features is None:
        n_features = config.N_PCA_COMPONENTS
    if reps is None:
        reps = config.ZZ_REPS

    feature_map = ZZFeatureMap(
        feature_dimension=n_features,
        reps=reps,
        entanglement=config.ENTANGLEMENT
    )

    log_success("ZZFeatureMap created")
    log_info(f"Qubits: {n_features} | Reps: {reps} | Entanglement: {config.ENTANGLEMENT}")
    log_info(f"Circuit depth: {feature_map.decompose().depth()}")

    # ── Quantum Entanglement Insight ─────────────────────
    print(f"\n  ╔{'═' * 56}╗")
    print(f"  ║  {'QUANTUM ENTANGLEMENT INSIGHT':<54}║")
    print(f"  ╠{'═' * 56}╣")
    print(f"  ║  {'Quantum entanglement captures hidden nonlinear':<54}║")
    print(f"  ║  {'relationships between transaction features,':<54}║")
    print(f"  ║  {'enabling improved fraud detection.':<54}║")
    print(f"  ║  {'':<54}║")
    print(f"  ║  {'Each transaction is encoded into a quantum state':<54}║")
    print(f"  ║  {'via ZZ entangling gates that model pairwise':<54}║")
    print(f"  ║  {'feature interactions in Hilbert space.':<54}║")
    print(f"  ╚{'═' * 56}╝")

    return feature_map
