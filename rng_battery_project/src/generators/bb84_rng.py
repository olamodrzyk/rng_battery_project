"""Efficient BB84-inspired bit source.

This module treats BB84 only as a mechanism that can yield a binary sequence.
It is not a full cryptographic security simulation; the goal is to provide a
quantum-inspired source for the statistical test battery.
"""

from __future__ import annotations

import numpy as np

from .utils import rng


def simulate_bb84_rng(n: int, eve_fraction: float = 0.0, seed: int | None = None) -> dict:
    """Simulate BB84 sifting until n raw key bits are obtained.

    Alice chooses random bits and bases. Bob independently chooses bases and
    measures. Positions where bases agree are sifted into the key. Optional
    intercept-resend eavesdropping is modeled on a fraction of transmitted
    qubits; when Eve uses the wrong basis, matching Alice/Bob bases suffer a
    50% disturbance, giving the familiar BB84 QBER signature.
    """
    if not 0.0 <= eve_fraction <= 1.0:
        raise ValueError("eve_fraction must lie in [0, 1].")

    generator = rng(seed)
    collected: list[np.ndarray] = []
    errors = 0
    sifted_total = 0
    rounds = 0

    while sum(len(chunk) for chunk in collected) < n:
        batch = max(4 * (n - sum(len(chunk) for chunk in collected)), 10_000)
        alice_bits = generator.integers(0, 2, batch, dtype=np.uint8)
        alice_bases = generator.integers(0, 2, batch, dtype=np.uint8)
        bob_bases = generator.integers(0, 2, batch, dtype=np.uint8)

        bob_bits = alice_bits.copy()
        eve_present = generator.random(batch) < eve_fraction
        eve_bases = generator.integers(0, 2, batch, dtype=np.uint8)
        disturbed = eve_present & (eve_bases != alice_bases) & (bob_bases == alice_bases)
        bob_bits[disturbed] = generator.integers(0, 2, disturbed.sum(), dtype=np.uint8)

        sift_mask = alice_bases == bob_bases
        sifted_alice = alice_bits[sift_mask]
        sifted_bob = bob_bits[sift_mask]
        errors += int(np.count_nonzero(sifted_alice != sifted_bob))
        sifted_total += int(sift_mask.sum())
        collected.append(sifted_bob)
        rounds += batch

    bits = np.concatenate(collected)[:n].astype(np.uint8)
    qber = errors / sifted_total if sifted_total else 0.0
    return {
        "bits": bits,
        "qber": float(qber),
        "metadata": {
            "protocol": "BB84-inspired efficient simulation",
            "eve_fraction": eve_fraction,
            "transmitted_qubits": rounds,
            "sifted_bits": sifted_total,
            "estimated_sifting_rate": sifted_total / rounds if rounds else 0.0,
        },
    }


def qiskit_bb84_demo() -> None:
    """Optional demonstration placeholder for small Qiskit BB84 circuits."""
    try:
        from qiskit import QuantumCircuit  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError("Install qiskit to run this optional demo.") from exc

    circuit = QuantumCircuit(1, 1)
    circuit.h(0)
    circuit.measure(0, 0)
    return circuit

