"""Run the complete RNG statistical test battery."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis.battery_runner import run_battery
from src.analysis.entropy_analysis import run_entropy_analysis
from src.analysis.eve_sweep import run_eve_sweep
from src.analysis.length_sweep import run_length_sweep
from src.analysis.statistics import export_tables, generate_markdown_report, summarize_results
from src.analysis.visualization import create_all_figures
from src.config import BASE_SEED, FIGURES_DIR, REPORTS_DIR, SEQUENCE_LENGTH, TABLES_DIR
from src.generators.bb84_rng import simulate_bb84_rng
from src.generators.bb92_rng import simulate_bb92_rng
from src.generators.classical_rng import numpy_rng, python_random_rng
from src.generators.flawed_rng import biased_rng, block_rng, markov_rng, periodic_rng
from src.generators.qiskit_demo import run_qiskit_demo

RUN_LENGTH_SWEEP = True
RUN_EVE_SWEEP = True
RUN_ENTROPY_ANALYSIS = True
RUN_QISKIT_DEMO = False


def build_sequences(n: int = SEQUENCE_LENGTH) -> tuple[dict[str, object], dict[str, dict]]:
    """Generate all sequences and retain metadata for quantum-inspired sources."""
    bb84_clean = simulate_bb84_rng(n, eve_fraction=0.0, seed=BASE_SEED + 10)
    bb84_eve = simulate_bb84_rng(n, eve_fraction=0.35, seed=BASE_SEED + 11)
    bb92 = simulate_bb92_rng(n, seed=BASE_SEED + 12)

    sequences = {
        "NumPy PCG64": numpy_rng(n, seed=BASE_SEED),
        "Python Mersenne": python_random_rng(n, seed=BASE_SEED + 1),
        "Biased p(1)=0.70": biased_rng(n, p_one=0.70, seed=BASE_SEED + 2),
        "Periodic 0101": periodic_rng(n, pattern="0101"),
        "Block RNG": block_rng(n, block_size=16, seed=BASE_SEED + 3),
        "Markov p_stay=0.95": markov_rng(n, p_stay=0.95, seed=BASE_SEED + 4),
        "BB84 no Eve": bb84_clean["bits"],
        "BB84 Eve 35%": bb84_eve["bits"],
        "BB92 ideal": bb92["bits"],
    }
    metadata = {
        "BB84 no Eve": {"qber": bb84_clean["qber"], **bb84_clean["metadata"]},
        "BB84 Eve 35%": {"qber": bb84_eve["qber"], **bb84_eve["metadata"]},
        "BB92 ideal": {"qber": bb92["qber"], **bb92["metadata"]},
    }
    return sequences, metadata


def main() -> None:
    sequences, quantum_metadata = build_sequences()
    results = run_battery(sequences)
    summary = summarize_results(results)

    export_tables(results, summary, TABLES_DIR)
    qber_table = pd.DataFrame(
        [{"generator": name, "qber": values["qber"]} for name, values in quantum_metadata.items()]
    )
    qber_table.to_csv(TABLES_DIR / "qber_summary.csv", index=False)
    create_all_figures(results, summary, qber_table, FIGURES_DIR)

    length_sweep_summary = None
    eve_sweep_summary = None
    entropy_summary = None
    qiskit_status = {"available": False, "reason": "RUN_QISKIT_DEMO is disabled by default."}

    if RUN_LENGTH_SWEEP:
        print("Running sequence length sweep...")
        _, length_sweep_summary = run_length_sweep()

    if RUN_EVE_SWEEP:
        print("Running BB84 Eve fraction sweep...")
        _, eve_sweep_summary = run_eve_sweep()

    if RUN_ENTROPY_ANALYSIS:
        print("Running Shannon entropy and autocorrelation analysis...")
        entropy_summary = run_entropy_analysis(sequences)

    if RUN_QISKIT_DEMO:
        print("Running optional Qiskit circuit demo...")
        qiskit_status = run_qiskit_demo()

    generate_markdown_report(
        results,
        summary,
        quantum_metadata,
        REPORTS_DIR / "rng_battery_report.md",
        length_sweep_summary=length_sweep_summary,
        eve_sweep_summary=eve_sweep_summary,
        entropy_summary=entropy_summary,
        qiskit_status=qiskit_status,
    )

    print("RNG battery completed.")
    print(f"Results table: {TABLES_DIR / 'rng_battery_results.csv'}")
    print(f"Summary table: {TABLES_DIR / 'rng_battery_summary.csv'}")
    print(f"Figures: {FIGURES_DIR}")
    print(f"Report: {REPORTS_DIR / 'rng_battery_report.md'}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
