"""Utilities shared by binary sequence generators."""

from __future__ import annotations

from typing import Iterable

import numpy as np


def as_binary_array(bits: Iterable[int] | np.ndarray) -> np.ndarray:
    """Return a one-dimensional uint8 array containing only 0 and 1."""
    if isinstance(bits, np.ndarray):
        array = np.asarray(bits, dtype=np.uint8).reshape(-1)
    else:
        array = np.fromiter(bits, dtype=np.uint8).reshape(-1)
    if not np.isin(array, [0, 1]).all():
        raise ValueError("Binary sequences must contain only 0 and 1.")
    return array


def ensure_length(bits: np.ndarray, n: int) -> np.ndarray:
    """Trim or validate a generated bit array to exactly n bits."""
    bits = as_binary_array(bits)
    if len(bits) < n:
        raise ValueError(f"Generated only {len(bits)} bits, but {n} were requested.")
    return bits[:n]


def rng(seed: int | None = None) -> np.random.Generator:
    """Create a NumPy random generator with an optional reproducible seed."""
    return np.random.default_rng(seed)
