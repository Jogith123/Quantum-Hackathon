"""
Q-Shield Logger
================
Clean structured logging with [STEP N] format.
"""


def log_step(step_num, message):
    """Print a formatted step log line."""
    print(f"\n{'=' * 55}")
    print(f"  [STEP {step_num}] {message}")
    print(f"{'=' * 55}")


def log_info(message):
    """Print an informational message."""
    print(f"  ➤ {message}")


def log_success(message):
    """Print a success message."""
    print(f"  ✓ {message}")


def log_warning(message):
    """Print a warning message."""
    print(f"  ⚠ {message}")


def log_header(title):
    """Print a section header."""
    width = 55
    print(f"\n╔{'═' * width}╗")
    print(f"║  {title:<{width - 2}}║")
    print(f"╚{'═' * width}╝")
