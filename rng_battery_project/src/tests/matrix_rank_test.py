"""Binary Matrix Rank Test from NIST SP 800-22."""

from __future__ import annotations

import numpy as np
from scipy.special import gammaincc

from .common import make_result, validate_bits


def _binary_rank(matrix: np.ndarray) -> int:
    """Compute rank over GF(2) by Gaussian elimination with XOR row operations."""
    matrix = matrix.copy().astype(np.uint8)
    rows, cols = matrix.shape
    rank = 0
    for col in range(cols):
        pivot_rows = np.flatnonzero(matrix[rank:, col]) + rank
        if pivot_rows.size == 0:
            continue
        pivot = int(pivot_rows[0])
        if pivot != rank:
            matrix[[rank, pivot]] = matrix[[pivot, rank]]
        for row in range(rows):
            if row != rank and matrix[row, col]:
                matrix[row] ^= matrix[rank]
        rank += 1
        if rank == rows:
            break
    return rank


def matrix_rank_test(bits: np.ndarray, rows: int = 32, cols: int = 32, alpha: float = 0.01) -> dict:
    """Test ranks of binary matrices cut from the sequence.

    For 32x32 matrices, NIST groups ranks as full, one less than full, and
    lower. Their asymptotic probabilities are approximately 0.2888, 0.5776,
    and 0.1336; a chi-square goodness-of-fit statistic is then used.
    """
    bits = validate_bits(bits)
    block_size = rows * cols
    n_matrices = len(bits) // block_size
    if n_matrices < 1:
        raise ValueError("Sequence too short for matrix rank test.")

    matrices = bits[: n_matrices * block_size].reshape(n_matrices, rows, cols)
    ranks = np.array([_binary_rank(matrix) for matrix in matrices])
    full_rank = int(np.count_nonzero(ranks == min(rows, cols)))
    one_less = int(np.count_nonzero(ranks == min(rows, cols) - 1))
    lower = int(n_matrices - full_rank - one_less)
    expected_probs = np.array([0.2888, 0.5776, 0.1336])
    observed = np.array([full_rank, one_less, lower], dtype=float)
    chi_square = np.sum((observed - n_matrices * expected_probs) ** 2 / (n_matrices * expected_probs))
    p_value = gammaincc(1.0, chi_square / 2.0)
    return make_result(
        "Binary Matrix Rank",
        chi_square,
        p_value,
        alpha,
        {"matrix_shape": [rows, cols], "n_matrices": n_matrices, "observed": observed.tolist()},
    )

