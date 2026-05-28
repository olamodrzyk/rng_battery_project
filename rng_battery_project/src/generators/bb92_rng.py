"""Efficient BB92-inspired bit source."""

from __future__ import annotations

import numpy as np

from .utils import rng


def simulate_bb92_rng(n: int, seed: int | None = None) -> dict:
    """Simulate simplified BB92 key extraction with inconclusive outcomes.

    Alice encodes 0 as |0> and 1 as |+>. Bob randomly tests with a measurement
    that can conclusively identify one of the two non-orthogonal states. The
    accepted outcomes form a sparse, but statistically balanced, key source.
    """
    generator = rng(seed)
    collected: list[np.ndarray] = []
    trials = 0
    conclusive = 0

    while sum(len(chunk) for chunk in collected) < n:
        batch = max(8 * (n - sum(len(chunk) for chunk in collected)), 20_000)
        alice_bits = generator.integers(0, 2, batch, dtype=np.uint8)
        bob_test = generator.integers(0, 2, batch, dtype=np.uint8)

        # If Bob chooses the test incompatible with Alice's state, a conclusive
        # result occurs with probability 1/2 for ideal BB92 states.
        compatible_for_conclusive = bob_test != alice_bits
        accepted = compatible_for_conclusive & (generator.random(batch) < 0.5)
        key_bits = alice_bits[accepted]
        collected.append(key_bits)
        conclusive += int(accepted.sum())
        trials += batch

    bits = np.concatenate(collected)[:n].astype(np.uint8)
    return {
        "bits": bits,
        "qber": 0.0,
        "metadata": {
            "protocol": "BB92-inspired efficient simulation",
            "transmitted_qubits": trials,
            "conclusive_events": conclusive,
            "estimated_conclusive_rate": conclusive / trials if trials else 0.0,
        },
    }


def qiskit_bb92_demo() -> None:
    """Optional demonstration placeholder for small Qiskit BB92 circuits."""
    try:
        from qiskit import QuantumCircuit  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError("Install qiskit to run this optional demo.") from exc

    circuit = QuantumCircuit(1, 1)
    circuit.h(0)
    circuit.measure(0, 0)
    return circuit

