"""Maurer's Universal Statistical Test inspired by NIST SP 800-22."""

from __future__ import annotations

import numpy as np
from scipy.special import erfc

from .common import make_result, validate_bits


EXPECTED_VALUE = {
    6: 5.2177052,
    7: 6.1962507,
    8: 7.1836656,
    9: 8.1764248,
    10: 9.1723243,
    11: 10.170032,
    12: 11.168765,
    13: 12.168070,
    14: 13.167693,
    15: 14.167488,
    16: 15.167379,
}

VARIANCE = {
    6: 2.954,
    7: 3.125,
    8: 3.238,
    9: 3.311,
    10: 3.356,
    11: 3.384,
    12: 3.401,
    13: 3.410,
    14: 3.416,
    15: 3.419,
    16: 3.421,
}


def _select_l(n: int) -> int:
    for l_value, min_n in [(16, 1_059_060), (15, 904_960), (14, 387_840), (13, 904_960 // 2), (12, 387_840 // 2), (11, 200_000), (10, 100_000), (9, 50_000), (8, 25_000), (7, 12_000), (6, 6_000)]:
        if n >= min_n:
            return l_value
    raise ValueError("Maurer test requires at least 6,000 bits.")


def maurer_universal_test(bits: np.ndarray, alpha: float = 0.01) -> dict:
    """Estimate compressibility using distances between repeated L-bit words.

    Maurer's statistic is the average log2 distance since the previous
    occurrence of each observed L-bit pattern. Truly random sequences have
    high expected novelty; periodic or compressible sequences produce smaller
    values and small p-values.
    """
    bits = validate_bits(bits)
    n = len(bits)
    l_value = _select_l(n)
    q = 10 * (2**l_value)
    k = n // l_value - q
    while k <= 0 and l_value > 6:
        l_value -= 1
        q = 10 * (2**l_value)
        k = n // l_value - q
    if k <= 0:
        raise ValueError("Sequence too short for selected Maurer parameters.")

    blocks = bits[: (q + k) * l_value].reshape(q + k, l_value)
    powers = (2 ** np.arange(l_value - 1, -1, -1)).astype(np.uint32)
    words = blocks.dot(powers)

    table = np.zeros(2**l_value, dtype=np.int64)
    for i in range(q):
        table[words[i]] = i + 1

    total = 0.0
    for i in range(q, q + k):
        previous = table[words[i]]
        distance = i + 1 - previous
        table[words[i]] = i + 1
        total += np.log2(distance)

    fn = total / k
    c = 0.7 - 0.8 / l_value + (4.0 + 32.0 / l_value) * (k ** (-3.0 / l_value)) / 15.0
    sigma = c * np.sqrt(VARIANCE[l_value] / k)
    p_value = erfc(abs(fn - EXPECTED_VALUE[l_value]) / (np.sqrt(2.0) * sigma))
    return make_result(
        "Maurer Universal",
        fn,
        p_value,
        alpha,
        {"L": l_value, "Q": q, "K": k, "expected_value": EXPECTED_VALUE[l_value], "sigma": sigma},
    )
