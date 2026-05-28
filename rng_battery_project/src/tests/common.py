"""Shared helpers for NIST SP 800-22-inspired statistical tests."""

from __future__ import annotations

from typing import Any

import numpy as np

from src.config import ALPHA


def validate_bits(bits: np.ndarray) -> np.ndarray:
    """Return a clean one-dimensional binary array."""
    array = np.asarray(bits, dtype=np.uint8).reshape(-1)
    if array.size == 0:
        raise ValueError("A statistical test requires at least one bit.")
    if not np.isin(array, [0, 1]).all():
        raise ValueError("Input must contain only 0 and 1.")
    return array


def make_result(
    test_name: str,
    statistic: float,
    p_value: float,
    alpha: float = ALPHA,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create the common result dictionary used by all tests."""
    p = float(np.clip(p_value, 0.0, 1.0)) if np.isfinite(p_value) else 0.0
    return {
        "test_name": test_name,
        "statistic": float(statistic),
        "p_value": p,
        "passed": bool(p >= alpha),
        "alpha": alpha,
        "details": details or {},
    }


def bits_to_pm1(bits: np.ndarray) -> np.ndarray:
    """Map 0 -> -1 and 1 -> +1, as used by several NIST statistics."""
    return 2 * validate_bits(bits).astype(np.int8) - 1

