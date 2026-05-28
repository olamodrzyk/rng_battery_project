"""Classical pseudo-random binary sequence generators."""

from __future__ import annotations

import random

import numpy as np

from .utils import as_binary_array


def numpy_rng(n: int, seed: int | None = None) -> np.ndarray:
    """Generate n bits with NumPy's default PCG64-based generator."""
    generator = np.random.default_rng(seed)
    return generator.integers(0, 2, size=n, dtype=np.uint8)


def python_random_rng(n: int, seed: int | None = None) -> np.ndarray:
    """Generate n bits using Python's Mersenne Twister implementation."""
    generator = random.Random(seed)
    return as_binary_array(np.fromiter((generator.getrandbits(1) for _ in range(n)), dtype=np.uint8, count=n))
