"""Intentionally flawed RNGs used as negative controls."""

from __future__ import annotations

import numpy as np

from .utils import as_binary_array, ensure_length, rng


def biased_rng(n: int, p_one: float = 0.7, seed: int | None = None) -> np.ndarray:
    """Generate Bernoulli bits with P(1)=p_one, intentionally failing balance tests."""
    return (rng(seed).random(n) < p_one).astype(np.uint8)


def periodic_rng(n: int, pattern: str = "0101") -> np.ndarray:
    """Repeat a short deterministic pattern until n bits are produced."""
    if not pattern or any(ch not in "01" for ch in pattern):
        raise ValueError("pattern must be a non-empty string of 0 and 1 characters.")
    repeated = (pattern * ((n // len(pattern)) + 1))[:n]
    return as_binary_array(int(ch) for ch in repeated)


def block_rng(n: int, block_size: int = 16, seed: int | None = None) -> np.ndarray:
    """Generate long constant blocks, producing unrealistically low transition counts."""
    if block_size <= 0:
        raise ValueError("block_size must be positive.")
    block_values = rng(seed).integers(0, 2, size=(n // block_size) + 1, dtype=np.uint8)
    return ensure_length(np.repeat(block_values, block_size), n)


def markov_rng(n: int, p_stay: float = 0.95, seed: int | None = None) -> np.ndarray:
    """Generate a two-state Markov chain with excessive serial dependence."""
    if not 0.0 <= p_stay <= 1.0:
        raise ValueError("p_stay must lie in [0, 1].")
    generator = rng(seed)
    bits = np.empty(n, dtype=np.uint8)
    bits[0] = generator.integers(0, 2)
    switches = generator.random(n - 1) > p_stay
    for i, switch in enumerate(switches, start=1):
        bits[i] = 1 - bits[i - 1] if switch else bits[i - 1]
    return bits

