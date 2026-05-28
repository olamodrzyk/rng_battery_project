"""Sequence length sweep for the RNG statistical test battery."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis.battery_runner import run_battery
from src.config import ALPHA, FIGURES_DIR, TABLES_DIR
from src.generators.bb84_rng import simulate_bb84_rng
from src.generators.bb92_rng import simulate_bb92_rng
from src.generators.classical_rng import numpy_rng, python_random_rng
from src.generators.flawed_rng import biased_rng, block_rng, markov_rng, periodic_rng


def _make_sequences(n: int, seed: int) -> dict:
    """Generate the standard comparison set for a given sequence length."""
    bb84_clean = simulate_bb84_rng(n, eve_fraction=0.0, seed=seed + 10)
    bb84_eve = simulate_bb84_rng(n, eve_fraction=0.35, seed=seed + 11)
    bb92 = simulate_bb92_rng(n, seed=seed + 12)
    return {
        "Python Mersenne": python_random_rng(n, seed=seed + 1),
        "NumPy PCG64": numpy_rng(n, seed=seed),
        "BB84 no Eve": bb84_clean["bits"],
        "BB84 Eve 35%": bb84_eve["bits"],
        "BB92 ideal": bb92["bits"],
        "Biased p(1)=0.70": biased_rng(n, p_one=0.70, seed=seed + 2),
        "Periodic 0101": periodic_rng(n, pattern="0101"),
        "Block RNG": block_rng(n, block_size=16, seed=seed + 3),
        "Markov p_stay=0.95": markov_rng(n, p_stay=0.95, seed=seed + 4),
    }


def _summarize_by_length(results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate pass-rate and p-value diagnostics by length and generator."""
    return (
        results.groupby(["length", "generator"])
        .agg(
            tests_run=("test", "count"),
            tests_passed=("passed", "sum"),
            pass_rate=("passed", "mean"),
            min_p_value=("p_value", "min"),
            median_p_value=("p_value", "median"),
        )
        .reset_index()
    )


def _plot_metric(summary: pd.DataFrame, metric: str, ylabel: str, output_name: str) -> None:
    plt.figure(figsize=(10, 6))
    for generator, group in summary.groupby("generator"):
        ordered = group.sort_values("length")
        plt.plot(ordered["length"], ordered[metric], marker="o", linewidth=1.6, label=generator)
    plt.xscale("log")
    plt.xlabel("Sequence length")
    plt.ylabel(ylabel)
    plt.title(ylabel + " vs sequence length")
    plt.legend(fontsize=7, ncol=2)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / output_name, dpi=180)
    plt.close()


def run_length_sweep(
    lengths: list[int] | tuple[int, ...] = (1_000, 10_000, 100_000),
    alpha: float = ALPHA,
    seed: int = 123,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run the full battery for several sequence lengths.

    Short sequences often produce unstable p-values and can be too small for
    asymptotic tests. Longer sequences provide more reliable statistical
    evidence, but passing a finite battery never proves true randomness.
    """
    all_results: list[pd.DataFrame] = []
    for length in lengths:
        sequences = _make_sequences(length, seed + length)
        result = run_battery(sequences, alpha=alpha)
        result.insert(0, "length", length)
        all_results.append(result)

    results = pd.concat(all_results, ignore_index=True)
    summary = _summarize_by_length(results)

    exportable = results.copy()
    exportable["details"] = exportable["details"].astype(str)
    exportable.to_csv(TABLES_DIR / "length_sweep_results.csv", index=False)
    summary.to_csv(TABLES_DIR / "length_sweep_summary.csv", index=False)

    _plot_metric(summary, "pass_rate", "Pass rate", "pass_rate_vs_length.png")
    _plot_metric(summary, "min_p_value", "Minimum p-value", "min_p_value_vs_length.png")
    return results, summary

