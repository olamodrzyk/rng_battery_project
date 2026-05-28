"""Visualization utilities for RNG battery outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _save_current(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_pvalue_heatmap(results: pd.DataFrame, output_dir: Path) -> None:
    pivot = results.pivot(index="generator", columns="test", values="p_value")
    fig, ax = plt.subplots(figsize=(12, 6))
    image = ax.imshow(pivot.values, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    fig.colorbar(image, ax=ax, label="p-value")
    ax.set_xticks(np.arange(len(pivot.columns)), labels=pivot.columns, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(pivot.index)), labels=pivot.index)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.iloc[i, j]:.3f}", ha="center", va="center", color="white", fontsize=7)
    plt.title("P-value heatmap")
    _save_current(output_dir / "pvalue_heatmap.png")


def plot_pass_fail_matrix(results: pd.DataFrame, output_dir: Path) -> None:
    pivot = results.pivot(index="generator", columns="test", values="passed").astype(int)
    _, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(pivot.values, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(pivot.columns)), labels=pivot.columns, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(pivot.index)), labels=pivot.index)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, str(pivot.iloc[i, j]), ha="center", va="center", color="black", fontsize=8)
    plt.title("Pass/fail matrix")
    _save_current(output_dir / "pass_fail_matrix.png")


def plot_pvalue_histogram(results: pd.DataFrame, output_dir: Path) -> None:
    plt.figure(figsize=(9, 5))
    for generator, group in results.groupby("generator"):
        plt.hist(group["p_value"].dropna(), bins=12, alpha=0.35, label=generator)
    plt.axvline(0.01, color="black", linestyle="--", linewidth=1, label="alpha=0.01")
    plt.title("Distribution of p-values")
    plt.xlabel("p-value")
    plt.legend(fontsize=7, ncol=2)
    _save_current(output_dir / "pvalue_histogram.png")


def plot_passed_tests(summary: pd.DataFrame, output_dir: Path) -> None:
    ordered = summary.sort_values("tests_passed", ascending=False)
    plt.figure(figsize=(9, 5))
    plt.barh(ordered["generator"], ordered["tests_passed"], color="#4C78A8")
    plt.gca().invert_yaxis()
    plt.xlabel("Number of passed tests")
    plt.ylabel("Generator")
    plt.title("Passed tests per generator")
    _save_current(output_dir / "passed_tests_per_generator.png")


def plot_qber(qber_table: pd.DataFrame, output_dir: Path) -> None:
    plt.figure(figsize=(8, 4))
    plt.bar(qber_table["generator"], qber_table["qber"], color="#F58518")
    plt.ylim(0, max(0.30, float(qber_table["qber"].max()) * 1.2))
    plt.ylabel("QBER")
    plt.xlabel("Generator")
    plt.title("BB84/BB92 diagnostic QBER")
    _save_current(output_dir / "qber_comparison.png")


def create_all_figures(results: pd.DataFrame, summary: pd.DataFrame, qber_table: pd.DataFrame, output_dir: Path) -> None:
    """Generate all requested visual summaries."""
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "ggplot")
    plot_pvalue_heatmap(results, output_dir)
    plot_pass_fail_matrix(results, output_dir)
    plot_pvalue_histogram(results, output_dir)
    plot_passed_tests(summary, output_dir)
    plot_qber(qber_table, output_dir)
