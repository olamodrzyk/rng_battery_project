"""Longest Run of Ones in a Block Test from NIST SP 800-22."""

from __future__ import annotations

import numpy as np
from scipy.special import gammaincc

from .common import make_result, validate_bits


def _longest_run(block: np.ndarray) -> int:
    best = current = 0
    for bit in block:
        current = current + 1 if bit else 0
        best = max(best, current)
    return best


def longest_run_test(bits: np.ndarray, alpha: float = 0.01) -> dict:
    """Compare longest one-runs per block to NIST category probabilities.

    This follows the SP 800-22 block-size regimes. The category counts are
    compared to the published multinomial probabilities using a chi-square
    statistic with K degrees of freedom.
    """
    bits = validate_bits(bits)
    n = len(bits)
    if n < 128:
        raise ValueError("Longest run test requires at least 128 bits.")
    if n < 6_272:
        m, v_values, pi = 8, np.array([1, 2, 3, 4]), np.array([0.2148, 0.3672, 0.2305, 0.1875])
        buckets = [lambda v: v <= 1, lambda v: v == 2, lambda v: v == 3, lambda v: v >= 4]
    elif n < 750_000:
        m, v_values, pi = 128, np.array([4, 5, 6, 7, 8, 9]), np.array([0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124])
        buckets = [lambda v: v <= 4, lambda v: v == 5, lambda v: v == 6, lambda v: v == 7, lambda v: v == 8, lambda v: v >= 9]
    else:
        m, v_values, pi = 10_000, np.array([10, 11, 12, 13, 14, 15, 16]), np.array([0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727])
        buckets = [lambda v: v <= 10, lambda v: v == 11, lambda v: v == 12, lambda v: v == 13, lambda v: v == 14, lambda v: v == 15, lambda v: v >= 16]

    n_blocks = n // m
    blocks = bits[: n_blocks * m].reshape(n_blocks, m)
    longest = np.array([_longest_run(block) for block in blocks])
    observed = np.array([sum(predicate(v) for v in longest) for predicate in buckets], dtype=float)
    chi_square = np.sum((observed - n_blocks * pi) ** 2 / (n_blocks * pi))
    degrees = len(pi) - 1
    p_value = gammaincc(degrees / 2.0, chi_square / 2.0)
    return make_result(
        "Longest Run of Ones",
        chi_square,
        p_value,
        alpha,
        {"block_size": m, "n_blocks": n_blocks, "categories": v_values.tolist(), "observed": observed.tolist()},
    )

