"""Central execution engine for the statistical test battery."""

from __future__ import annotations

import time
from typing import Any, Callable, Dict

import numpy as np
import pandas as pd

from src.config import ALPHA
from src.tests.block_frequency_test import block_frequency_test
from src.tests.frequency_test import frequency_test
from src.tests.longest_run_test import longest_run_test
from src.tests.matrix_rank_test import matrix_rank_test
from src.tests.maurer_test import maurer_universal_test
from src.tests.runs_test import runs_test
from src.tests.template_matching_test import template_matching_test

TestFunction = Callable[[np.ndarray], Dict[str, Any]]


def _named_test(name: str, function: TestFunction) -> TestFunction:
    """Attach a stable display name to a configured test callable."""
    setattr(function, "battery_name", name)
    return function


def default_tests(alpha: float = ALPHA) -> list[TestFunction]:
    """Return the selected NIST-inspired test battery."""
    return [
        _named_test("Frequency (Monobit)", lambda bits: frequency_test(bits, alpha=alpha)),
        _named_test("Block Frequency", lambda bits: block_frequency_test(bits, block_size=128, alpha=alpha)),
        _named_test("Runs", lambda bits: runs_test(bits, alpha=alpha)),
        _named_test("Longest Run of Ones", lambda bits: longest_run_test(bits, alpha=alpha)),
        _named_test("Binary Matrix Rank", lambda bits: matrix_rank_test(bits, rows=32, cols=32, alpha=alpha)),
        _named_test(
            "Non-overlap Template",
            lambda bits: template_matching_test(bits, template="001", block_size=1_024, alpha=alpha),
        ),
        _named_test("Maurer Universal", lambda bits: maurer_universal_test(bits, alpha=alpha)),
    ]


def run_battery(sequences: dict[str, np.ndarray], alpha: float = ALPHA) -> pd.DataFrame:
    """Run every statistical test on every named binary sequence."""
    records: list[dict[str, Any]] = []
    for generator_name, bits in sequences.items():
        for test in default_tests(alpha):
            start = time.perf_counter()
            try:
                result = test(bits)
                error = None
            except Exception as exc:
                result = {
                    "test_name": getattr(test, "battery_name", getattr(test, "__name__", "unknown")),
                    "statistic": np.nan,
                    "p_value": np.nan,
                    "passed": False,
                    "alpha": alpha,
                    "details": {},
                }
                error = str(exc)
            elapsed = time.perf_counter() - start
            records.append(
                {
                    "generator": generator_name,
                    "test": result["test_name"],
                    "statistic": result["statistic"],
                    "p_value": result["p_value"],
                    "passed": result["passed"],
                    "alpha": result["alpha"],
                    "execution_time": elapsed,
                    "details": result.get("details", {}),
                    "error": error,
                }
            )
    return pd.DataFrame.from_records(records)
