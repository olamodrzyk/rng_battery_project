# RNG Statistical Test Battery

This project is an academic-style Python implementation for comparing binary random number generators using a selected battery of statistical tests inspired by NIST SP 800-22.

The main subject is random number generation and statistical testing. BB84 and BB92 are included only as quantum-inspired sources of bit sequences, not as full quantum cryptography protocol studies.

## What the Battery Does

A randomness test battery evaluates whether a binary sequence behaves consistently with an ideal iid Bernoulli(1/2) source. Each test targets a different property: global balance, local balance, run structure, long runs, linear dependence in binary matrices, template frequency, and compressibility.

The implemented tests are:

- Frequency (Monobit)
- Block Frequency
- Runs
- Longest Run of Ones
- Binary Matrix Rank
- Non-overlapping Template Matching
- Maurer Universal Statistical Test

Each test returns a structured result containing the statistic, p-value, pass/fail decision, alpha level, and details.

## Generators Compared

Classical generators:

- NumPy PCG64
- Python `random` / Mersenne Twister

Intentionally flawed generators:

- Biased Bernoulli source
- Periodic source
- Constant block source
- Highly persistent Markov source

Quantum-inspired generators:

- Efficient BB84-style sifted key source with optional eavesdropping and QBER diagnostic
- Efficient BB92-style source with inconclusive measurements

Flawed generators are included as negative controls. A useful test battery should reject sequences with obvious statistical defects.

## Installation

```bash
pip install -r requirements.txt
python main.py
```

## Outputs

Running `python main.py` creates:

- `results/tables/rng_battery_results.csv`
- `results/tables/rng_battery_summary.csv`
- `results/tables/rng_battery_summary.json`
- `results/tables/qber_summary.csv`
- `results/tables/length_sweep_results.csv`
- `results/tables/length_sweep_summary.csv`
- `results/tables/eve_sweep_results.csv`
- `results/tables/eve_sweep_summary.csv`
- `results/tables/entropy_summary.csv`
- `results/figures/pvalue_heatmap.png`
- `results/figures/pass_fail_matrix.png`
- `results/figures/pvalue_histogram.png`
- `results/figures/passed_tests_per_generator.png`
- `results/figures/qber_comparison.png`
- `results/figures/pass_rate_vs_length.png`
- `results/figures/min_p_value_vs_length.png`
- `results/figures/qber_vs_eve_fraction.png`
- `results/figures/pass_rate_vs_eve_fraction.png`
- `results/figures/min_p_value_vs_eve_fraction.png`
- `results/figures/shannon_entropy_by_generator.png`
- `results/figures/lag1_autocorrelation_by_generator.png`
- `results/figures/autocorrelation_selected_generators.png`
- `results/reports/rng_battery_report.md`

## Additional Analyses

`main.py` includes simple flags controlling optional analyses:

```python
RUN_LENGTH_SWEEP = True
RUN_EVE_SWEEP = True
RUN_ENTROPY_ANALYSIS = True
RUN_QISKIT_DEMO = False
```

The sequence length sweep compares pass rates and p-values for 1,000, 10,000, and 100,000 bit sequences. Short sequences can produce less stable p-values, while longer sequences provide stronger statistical evidence. Passing a finite battery still does not prove true randomness.

The BB84 Eve fraction sweep varies the intercept-resend fraction and records QBER alongside statistical-test outcomes. Eve should increase QBER, but NIST-style randomness tests are not equivalent to eavesdropping detection: QBER measures protocol disturbance, while randomness tests measure properties of the extracted bit sequence.

The entropy analysis computes binary Shannon entropy, normalized entropy, lag-1 autocorrelation, and maximum absolute autocorrelation over selected lags. High Shannon entropy alone does not imply randomness. For example, a 0101 periodic sequence may have almost one bit of entropy per symbol because zeros and ones are balanced, while remaining completely predictable due to correlations.

## Optional Qiskit Demo

The optional Qiskit demo in `src/generators/qiskit_demo.py` builds minimal one-qubit circuits illustrating BB84 and BB92 state preparation and measurement. It is intentionally separate from the large-scale statistical analysis, which uses efficient classical simulation to generate long bit sequences.

Qiskit is not required by `requirements.txt`. To enable the circuit demo, install Qiskit separately and set:

```python
RUN_QISKIT_DEMO = True
```

If available, the demo attempts to save:

- `results/figures/bb84_example_circuit.png`
- `results/figures/bb92_example_circuit.png`

## Extending the Project

To add a generator, implement a function returning a NumPy array of 0/1 bits and register it in `main.py`.

To add a statistical test, create a module under `src/tests/`, return the standard dictionary format, and add the function to `default_tests()` in `src/analysis/battery_runner.py`.

## References

NIST SP 800-22 Rev. 1a, *A Statistical Test Suite for Random and Pseudorandom Number Generators for Cryptographic Applications*.
