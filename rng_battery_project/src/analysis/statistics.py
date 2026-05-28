"""Summary tables and report generation for RNG battery results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def summarize_results(results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate pass counts and p-value summaries by generator."""
    return (
        results.groupby("generator")
        .agg(
            tests_run=("test", "count"),
            tests_passed=("passed", "sum"),
            pass_rate=("passed", "mean"),
            min_p_value=("p_value", "min"),
            median_p_value=("p_value", "median"),
            total_execution_time=("execution_time", "sum"),
        )
        .reset_index()
        .sort_values(["tests_passed", "median_p_value"], ascending=[False, False])
    )


def export_tables(results: pd.DataFrame, summary: pd.DataFrame, output_dir: Path) -> None:
    """Write CSV and JSON summaries for downstream reports."""
    output_dir.mkdir(parents=True, exist_ok=True)
    exportable = results.copy()
    exportable["details"] = exportable["details"].apply(json.dumps)
    exportable.to_csv(output_dir / "rng_battery_results.csv", index=False)
    summary.to_csv(output_dir / "rng_battery_summary.csv", index=False)
    with (output_dir / "rng_battery_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary.to_dict(orient="records"), handle, indent=2)


def generate_markdown_report(
    results: pd.DataFrame,
    summary: pd.DataFrame,
    qber_metadata: dict[str, Any],
    output_path: Path,
    length_sweep_summary: pd.DataFrame | None = None,
    eve_sweep_summary: pd.DataFrame | None = None,
    entropy_summary: pd.DataFrame | None = None,
    qiskit_status: dict[str, Any] | None = None,
) -> None:
    """Create a concise academic-style Markdown report."""
    best = summary.iloc[0]
    failed = results.loc[~results["passed"], ["generator", "test", "p_value"]]
    lines = [
        "# RNG Statistical Test Battery Report",
        "",
        "This report compares classical, intentionally flawed, and quantum-inspired binary sequence generators using a selected battery of tests inspired by NIST SP 800-22.",
        "",
        "## Summary",
        "",
        summary.to_markdown(index=False),
        "",
        f"The strongest overall result in this run is `{best['generator']}`, with {int(best['tests_passed'])}/{int(best['tests_run'])} tests passed.",
        "",
        "## Failed Tests",
        "",
        failed.to_markdown(index=False) if not failed.empty else "All tested generator/test pairs passed at the selected alpha level.",
        "",
        "## BB84 / BB92 Metadata",
        "",
        "Quantum-inspired generators are interpreted here as bit sources. BB84 QBER is reported as a diagnostic of simulated channel disturbance, not as the main object of study.",
        "",
        "```json",
        json.dumps(qber_metadata, indent=2),
        "```",
        "",
        "## Interpretation",
        "",
        "Low p-values indicate that a sequence is unlikely under the ideal iid Bernoulli(1/2) model for the statistic considered. Flawed generators are included as negative controls: biased sources should fail balance-sensitive tests, periodic sources should fail structure-sensitive tests, and Markov/block sources should fail transition and compressibility tests.",
        "",
        "## Sequence Length Dependence",
        "",
        "Short sequences may produce less stable p-values because asymptotic approximations have less information to work with, and some tests require a minimum number of bits. Longer sequences provide more reliable statistical evidence, but passing a test battery does not prove true randomness.",
    ]
    if length_sweep_summary is not None and not length_sweep_summary.empty:
        lines.extend(["", length_sweep_summary.to_markdown(index=False)])

    lines.extend(
        [
            "",
            "## BB84 Eve Fraction Dependence",
            "",
            "Eve should increase QBER in the BB84 simulation because intercept-resend measurements disturb Alice/Bob correlations. Classical randomness tests may not detect Eve directly: QBER measures protocol security and correlation disturbance, while NIST-style tests measure statistical properties of the extracted bit sequence. These diagnostics are related, but not identical.",
        ]
    )
    if eve_sweep_summary is not None and not eve_sweep_summary.empty:
        lines.extend(["", eve_sweep_summary.to_markdown(index=False)])

    lines.extend(
        [
            "",
            "## Shannon Entropy and Autocorrelation",
            "",
            "Shannon entropy measures uncertainty in the marginal bit distribution. It is useful for detecting biased generators, but it does not fully characterize randomness. High Shannon entropy alone does not imply randomness: a periodic 0101 sequence can have entropy close to one bit per symbol while remaining completely predictable due to correlations. Autocorrelation helps detect temporal structure and dependence, so entropy and autocorrelation should be treated as complementary diagnostics, not replacements for the statistical battery.",
        ]
    )
    if entropy_summary is not None and not entropy_summary.empty:
        display_columns = [
            "generator",
            "p0",
            "p1",
            "normalized_entropy",
            "lag1_autocorrelation",
            "max_abs_autocorrelation",
        ]
        lines.extend(["", entropy_summary[display_columns].to_markdown(index=False)])

    lines.extend(["", "## Quantum Circuit Demonstration", ""])
    if qiskit_status and qiskit_status.get("available"):
        lines.append(
            "The optional Qiskit demo constructed one-qubit BB84 and BB92 circuits. These circuits illustrate the state-preparation and measurement logic behind the efficient classical simulations used for large-scale statistical analysis."
        )
    else:
        reason = qiskit_status.get("reason") if qiskit_status else "RUN_QISKIT_DEMO is disabled by default."
        lines.append(
            f"The Qiskit demo is optional and was not run in this report ({reason}). Large-scale statistical analysis still uses efficient classical simulation."
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
