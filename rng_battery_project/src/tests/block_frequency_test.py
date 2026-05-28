"""Block Frequency Test from NIST SP 800-22."""

from __future__ import annotations

import numpy as np
from scipy.special import gammaincc

from .common import make_result, validate_bits


def block_frequency_test(bits: np.ndarray, block_size: int = 128, alpha: float = 0.01) -> dict:
    """Test whether the fraction of ones is close to 1/2 inside fixed blocks.

    With N blocks, chi-square = 4M sum_i (pi_i-1/2)^2. Under the iid fair-bit
    null, this statistic is approximately chi-square with N degrees of freedom.
    """
    bits = validate_bits(bits)
    n_blocks = len(bits) // block_size
    if n_blocks < 1:
        raise ValueError("Sequence too short for the selected block size.")
    trimmed = bits[: n_blocks * block_size].reshape(n_blocks, block_size)
    proportions = trimmed.mean(axis=1)
    chi_square = 4.0 * block_size * np.sum((proportions - 0.5) ** 2)
    p_value = gammaincc(n_blocks / 2.0, chi_square / 2.0)
    return make_result(
        "Block Frequency",
        chi_square,
        p_value,
        alpha,
        {"block_size": block_size, "n_blocks": n_blocks},
    )

