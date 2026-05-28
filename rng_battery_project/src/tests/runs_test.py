"""Runs Test from NIST SP 800-22."""

from __future__ import annotations

import numpy as np
from scipy.special import erfc

from .common import make_result, validate_bits


def runs_test(bits: np.ndarray, alpha: float = 0.01) -> dict:
    """Test whether transitions between 0 and 1 occur at the expected rate.

    Conditional on the empirical one-proportion pi being close to 1/2, the
    number of runs V_n should be near 2n pi(1-pi). NIST computes a normal-tail
    p-value using erfc.
    """
    bits = validate_bits(bits)
    n = len(bits)
    pi = float(bits.mean())
    tau = 2.0 / np.sqrt(n)
    if abs(pi - 0.5) >= tau:
        return make_result("Runs", 0.0, 0.0, alpha, {"n": n, "pi": pi, "reason": "frequency precondition failed"})
    runs = 1 + int(np.count_nonzero(bits[1:] != bits[:-1]))
    denominator = 2.0 * np.sqrt(2.0 * n) * pi * (1.0 - pi)
    p_value = erfc(abs(runs - 2.0 * n * pi * (1.0 - pi)) / denominator)
    return make_result("Runs", runs, p_value, alpha, {"n": n, "pi": pi})

