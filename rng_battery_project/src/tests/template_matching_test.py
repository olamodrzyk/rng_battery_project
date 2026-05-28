"""Non-overlapping Template Matching Test from NIST SP 800-22."""

from __future__ import annotations

import numpy as np
from scipy.special import gammaincc

from .common import make_result, validate_bits


def _count_non_overlapping(block: np.ndarray, template: np.ndarray) -> int:
    count = 0
    i = 0
    m = len(template)
    while i <= len(block) - m:
        if np.array_equal(block[i : i + m], template):
            count += 1
            i += m
        else:
            i += 1
    return count


def template_matching_test(
    bits: np.ndarray,
    template: str = "001",
    block_size: int = 1_024,
    alpha: float = 0.01,
) -> dict:
    """Count non-overlapping occurrences of a fixed aperiodic template.

    Under iid fair bits, block counts are approximately normal with
    mean=(M-m+1)/2^m and variance from the NIST approximation. Summed squared
    standardized deviations produce a chi-square statistic.
    """
    bits = validate_bits(bits)
    if any(ch not in "01" for ch in template):
        raise ValueError("template must contain only 0 and 1.")
    pattern = np.array([int(ch) for ch in template], dtype=np.uint8)
    m = len(pattern)
    n_blocks = len(bits) // block_size
    if n_blocks < 1 or block_size <= m:
        raise ValueError("Sequence too short for template matching settings.")
    blocks = bits[: n_blocks * block_size].reshape(n_blocks, block_size)
    counts = np.array([_count_non_overlapping(block, pattern) for block in blocks], dtype=float)
    mean = (block_size - m + 1) / (2.0**m)
    variance = block_size * ((1.0 / (2.0**m)) - ((2.0 * m - 1.0) / (2.0 ** (2 * m))))
    chi_square = np.sum((counts - mean) ** 2 / variance)
    p_value = gammaincc(n_blocks / 2.0, chi_square / 2.0)
    return make_result(
        "Non-overlap Template",
        chi_square,
        p_value,
        alpha,
        {"template": template, "block_size": block_size, "n_blocks": n_blocks, "mean": mean, "variance": variance},
    )

