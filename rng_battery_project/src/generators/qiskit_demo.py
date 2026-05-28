"""Optional minimal Qiskit demonstrations for BB84 and BB92 state logic."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.config import FIGURES_DIR


def _load_qiskit() -> Any:
    try:
        from qiskit import QuantumCircuit  # type: ignore
    except ImportError as exc:
        raise ImportError("Qiskit is optional. Install qiskit to run the circuit demo.") from exc
    return QuantumCircuit


def bb84_single_qubit_circuit(bit: int, alice_basis: str, bob_basis: str):
    """Create a one-qubit BB84 encode/measure circuit.

    Alice encodes bit 0/1 in either Z basis (|0>, |1>) or X basis (|+>, |->).
    Bob measures in Z directly, or in X by applying H before measurement.
    """
    QuantumCircuit = _load_qiskit()
    alice_basis = alice_basis.upper()
    bob_basis = bob_basis.upper()
    if bit not in (0, 1) or alice_basis not in ("Z", "X") or bob_basis not in ("Z", "X"):
        raise ValueError("Use bit in {0,1}, alice_basis in {'Z','X'}, bob_basis in {'Z','X'}.")

    circuit = QuantumCircuit(1, 1)
    if alice_basis == "Z" and bit == 1:
        circuit.x(0)
    elif alice_basis == "X":
        circuit.h(0)
        if bit == 1:
            circuit.z(0)
    circuit.barrier()
    if bob_basis == "X":
        circuit.h(0)
    circuit.measure(0, 0)
    return circuit


def bb92_single_qubit_circuit(bit: int, measurement_type: str):
    """Create a one-qubit BB92 illustrative circuit.

    The demo encodes 0 as |0> and 1 as |+>. Measurement type can be "Z" or
    "X", showing how non-orthogonal states lead to inconclusive information.
    """
    QuantumCircuit = _load_qiskit()
    measurement_type = measurement_type.upper()
    if bit not in (0, 1) or measurement_type not in ("Z", "X"):
        raise ValueError("Use bit in {0,1} and measurement_type in {'Z','X'}.")

    circuit = QuantumCircuit(1, 1)
    if bit == 1:
        circuit.h(0)
    circuit.barrier()
    if measurement_type == "X":
        circuit.h(0)
    circuit.measure(0, 0)
    return circuit


def _save_circuit(circuit: Any, path: Path) -> bool:
    try:
        figure = circuit.draw(output="mpl")
        figure.savefig(path, dpi=180, bbox_inches="tight")
        return True
    except Exception as exc:
        print(f"Qiskit circuit was created, but diagram export failed: {exc}")
        return False


def run_qiskit_demo() -> dict[str, Any]:
    """Run optional circuit construction and save diagrams when possible."""
    try:
        bb84 = bb84_single_qubit_circuit(bit=1, alice_basis="X", bob_basis="X")
        bb92 = bb92_single_qubit_circuit(bit=1, measurement_type="Z")
    except ImportError as exc:
        print(str(exc))
        return {"available": False, "reason": str(exc)}

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    bb84_saved = _save_circuit(bb84, FIGURES_DIR / "bb84_example_circuit.png")
    bb92_saved = _save_circuit(bb92, FIGURES_DIR / "bb92_example_circuit.png")
    print("Qiskit demo completed.")
    return {"available": True, "bb84_diagram_saved": bb84_saved, "bb92_diagram_saved": bb92_saved}

