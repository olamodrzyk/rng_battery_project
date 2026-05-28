"""Frequency (Monobit) Test from NIST SP 800-22."""

from __future__ import annotations

import numpy as np
from scipy.special import erfc

from .common import bits_to_pm1, make_result


def frequency_test(bits: np.ndarray, alpha: float = 0.01) -> dict:
    """Test whether ones and zeros are globally balanced.

    For iid fair bits, S_n=sum(2X_i-1) is approximately N(0,n). NIST uses
    s_obs=|S_n|/sqrt(n) and p=erfc(s_obs/sqrt(2)).
    """
    x = bits_to_pm1(bits)
    statistic = abs(int(np.sum(x))) / np.sqrt(len(x))
    p_value = erfc(statistic / np.sqrt(2.0))
    return make_result(
        "Frequency (Monobit)",
        statistic,
        p_value,
        alpha,
        {"n": len(x), "ones": int(np.count_nonzero(bits)), "zeros": int(len(x) - np.count_nonzero(bits))},
    )

