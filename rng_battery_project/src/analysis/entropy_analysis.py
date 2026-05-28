"""Shannon entropy and autocorrelation diagnostics for binary sequences."""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import FIGURES_DIR, TABLES_DIR
from src.tests.common import validate_bits


def binary_shannon_entropy(bits: np.ndarray) -> dict[str, float]:
    """Compute H(X)=-p0 log2(p0)-p1 log2(p1) for a binary sequence."""
    bits = validate_bits(bits)
    p1 = float(bits.mean())
    p0 = 1.0 - p1
    entropy = 0.0
    for probability in (p0, p1):
        if probability > 0.0:
            entropy -= probability * math.log2(probability)
    return {"entropy": entropy, "normalized_entropy": entropy, "p0": p0, "p1": p1}


def _pm1(bits: np.ndarray) -> np.ndarray:
    return 2.0 * validate_bits(bits).astype(float) - 1.0


def lag1_autocorrelation(bits: np.ndarray) -> float:
    """Return Pearson autocorrelation at lag 1 after mapping bits to {-1,+1}."""
    values = _pm1(bits)
    if len(values) < 2:
        return float("nan")
    return _lag_autocorrelation(values, 1)


def _lag_autocorrelation(values: np.ndarray, lag: int) -> float:
    left = values[:-lag]
    right = values[lag:]
    left_centered = left - left.mean()
    right_centered = right - right.mean()
    denominator = np.linalg.norm(left_centered) * np.linalg.norm(right_centered)
    if denominator == 0.0:
        return 0.0
    return float(np.dot(left_centered, right_centered) / denominator)


def autocorrelation(bits: np.ndarray, max_lag: int = 50) -> pd.DataFrame:
    """Compute autocorrelation for lags 1..max_lag on {-1,+1} values."""
    values = _pm1(bits)
    usable_lag = min(max_lag, len(values) - 1)
    rows = [{"lag": lag, "autocorrelation": _lag_autocorrelation(values, lag)} for lag in range(1, usable_lag + 1)]
    return pd.DataFrame(rows)


def _plot_entropy(summary: pd.DataFrame) -> None:
    ordered = summary.sort_values("normalized_entropy", ascending=False)
    plt.figure(figsize=(10, 5))
    plt.barh(ordered["generator"], ordered["normalized_entropy"], color="#4C78A8")
    plt.gca().invert_yaxis()
    plt.xlim(0, 1.05)
    plt.xlabel("Normalized Shannon entropy")
    plt.title("Shannon entropy by generator")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "shannon_entropy_by_generator.png", dpi=180)
    plt.close()


def _plot_lag1(summary: pd.DataFrame) -> None:
    ordered = summary.sort_values("lag1_autocorrelation")
    plt.figure(figsize=(10, 5))
    plt.barh(ordered["generator"], ordered["lag1_autocorrelation"], color="#F58518")
    plt.axvline(0.0, color="black", linewidth=0.8)
    plt.xlabel("Lag-1 autocorrelation")
    plt.title("Lag-1 autocorrelation by generator")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "lag1_autocorrelation_by_generator.png", dpi=180)
    plt.close()


def _plot_selected_autocorrelations(sequences: dict[str, np.ndarray], max_lag: int) -> None:
    selected = ["NumPy PCG64", "BB84 no Eve", "Periodic 0101", "Markov p_stay=0.95", "Biased p(1)=0.70"]
    plt.figure(figsize=(10, 5))
    for generator in selected:
        if generator not in sequences:
            continue
        acf = autocorrelation(sequences[generator], max_lag=max_lag)
        plt.plot(acf["lag"], acf["autocorrelation"], marker="o", markersize=2.5, linewidth=1.2, label=generator)
    plt.axhline(0.0, color="black", linewidth=0.8)
    plt.xlabel("Lag")
    plt.ylabel("Autocorrelation")
    plt.title("Selected autocorrelation functions")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "autocorrelation_selected_generators.png", dpi=180)
    plt.close()


def run_entropy_analysis(sequences: dict[str, np.ndarray], max_lag: int = 50) -> pd.DataFrame:
    """Compute entropy and autocorrelation diagnostics for each generator.

    Shannon entropy measures uncertainty of the marginal bit distribution. It
    detects bias, but not all predictability: an alternating 0101 sequence has
    nearly one bit of marginal entropy while remaining fully predictable.
    Autocorrelation complements entropy by exposing temporal dependence.
    """
    rows: list[dict] = []
    for generator, bits in sequences.items():
        entropy = binary_shannon_entropy(bits)
        acf = autocorrelation(bits, max_lag=max_lag)
        rows.append(
            {
                "generator": generator,
                "p0": entropy["p0"],
                "p1": entropy["p1"],
                "shannon_entropy": entropy["entropy"],
                "normalized_entropy": entropy["normalized_entropy"],
                "lag1_autocorrelation": lag1_autocorrelation(bits),
                "max_abs_autocorrelation": float(acf["autocorrelation"].abs().max()) if not acf.empty else float("nan"),
            }
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(TABLES_DIR / "entropy_summary.csv", index=False)
    _plot_entropy(summary)
    _plot_lag1(summary)
    _plot_selected_autocorrelations(sequences, max_lag=max_lag)
    return summary

