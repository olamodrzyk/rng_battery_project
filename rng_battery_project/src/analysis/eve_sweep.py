"""BB84 eavesdropping-fraction sweep."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from src.analysis.battery_runner import run_battery
from src.config import ALPHA, FIGURES_DIR, TABLES_DIR
from src.generators.bb84_rng import simulate_bb84_rng


def _plot_eve_metric(summary: pd.DataFrame, metric: str, ylabel: str, output_name: str) -> None:
    ordered = summary.sort_values("eve_fraction")
    plt.figure(figsize=(8, 5))
    plt.plot(ordered["eve_fraction"], ordered[metric], marker="o", linewidth=1.8)
    plt.xlabel("Eve fraction")
    plt.ylabel(ylabel)
    plt.title(ylabel + " vs Eve fraction")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / output_name, dpi=180)
    plt.close()


def run_eve_sweep(
    eve_fractions: list[float] | tuple[float, ...] = (0.0, 0.1, 0.2, 0.3, 0.35, 0.4, 0.5),
    n: int = 100_000,
    alpha: float = ALPHA,
    seed: int = 123,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Measure BB84 QBER and statistical-test behavior across Eve fractions.

    Eve should increase QBER because intercept-resend attacks disturb basis
    correlations. NIST-style tests may not detect Eve directly: QBER measures
    protocol disturbance, while randomness tests measure distributional
    properties of the extracted bit sequence.
    """
    records: list[pd.DataFrame] = []
    summary_rows: list[dict] = []

    for index, eve_fraction in enumerate(eve_fractions):
        generated = simulate_bb84_rng(n, eve_fraction=eve_fraction, seed=seed + index)
        label = f"BB84 Eve {eve_fraction:.2f}"
        result = run_battery({label: generated["bits"]}, alpha=alpha)
        result.insert(0, "eve_fraction", eve_fraction)
        result.insert(1, "qber", generated["qber"])
        records.append(result)

        summary_rows.append(
            {
                "eve_fraction": eve_fraction,
                "qber": generated["qber"],
                "tests_run": len(result),
                "tests_passed": int(result["passed"].sum()),
                "pass_rate": float(result["passed"].mean()),
                "min_p_value": float(result["p_value"].min()),
                "median_p_value": float(result["p_value"].median()),
            }
        )

    results = pd.concat(records, ignore_index=True)
    summary = pd.DataFrame(summary_rows)

    exportable = results.copy()
    exportable["details"] = exportable["details"].astype(str)
    exportable.to_csv(TABLES_DIR / "eve_sweep_results.csv", index=False)
    summary.to_csv(TABLES_DIR / "eve_sweep_summary.csv", index=False)

    _plot_eve_metric(summary, "qber", "QBER", "qber_vs_eve_fraction.png")
    _plot_eve_metric(summary, "pass_rate", "Pass rate", "pass_rate_vs_eve_fraction.png")
    _plot_eve_metric(summary, "min_p_value", "Minimum p-value", "min_p_value_vs_eve_fraction.png")
    return results, summary

