# RNG Statistical Test Battery Report

This report compares classical, intentionally flawed, and quantum-inspired binary sequence generators using a selected battery of tests inspired by NIST SP 800-22.

## Summary

| generator          |   tests_run |   tests_passed |   pass_rate |   min_p_value |   median_p_value |   total_execution_time |
|:-------------------|------------:|---------------:|------------:|--------------:|-----------------:|-----------------------:|
| BB92 ideal         |           7 |              7 |    1        |     0.373253  |         0.773295 |                1.29476 |
| BB84 no Eve        |           7 |              7 |    1        |     0.022233  |         0.557994 |                1.39155 |
| Python Mersenne    |           7 |              7 |    1        |     0.169769  |         0.536984 |                1.4982  |
| NumPy PCG64        |           7 |              7 |    1        |     0.0767679 |         0.454486 |                1.54935 |
| BB84 Eve 35%       |           7 |              7 |    1        |     0.0475993 |         0.363085 |                1.3382  |
| Periodic 0101      |           7 |              2 |    0.285714 |     0         |         0        |                1.42589 |
| Biased p(1)=0.70   |           7 |              1 |    0.142857 |     0         |         0        |                1.62606 |
| Block RNG          |           7 |              0 |    0        |     0         |         0        |                1.44551 |
| Markov p_stay=0.95 |           7 |              0 |    0        |     0         |         0        |                1.66269 |

The strongest overall result in this run is `BB92 ideal`, with 7/7 tests passed.

## Failed Tests

| generator          | test                 |     p_value |
|:-------------------|:---------------------|------------:|
| Biased p(1)=0.70   | Frequency (Monobit)  | 0           |
| Biased p(1)=0.70   | Block Frequency      | 0           |
| Biased p(1)=0.70   | Runs                 | 0           |
| Biased p(1)=0.70   | Longest Run of Ones  | 0           |
| Biased p(1)=0.70   | Non-overlap Template | 0           |
| Biased p(1)=0.70   | Maurer Universal     | 0           |
| Periodic 0101      | Runs                 | 0           |
| Periodic 0101      | Longest Run of Ones  | 0           |
| Periodic 0101      | Binary Matrix Rank   | 2.5105e-275 |
| Periodic 0101      | Non-overlap Template | 0           |
| Periodic 0101      | Maurer Universal     | 0           |
| Block RNG          | Frequency (Monobit)  | 0.000198579 |
| Block RNG          | Block Frequency      | 0           |
| Block RNG          | Runs                 | 0           |
| Block RNG          | Longest Run of Ones  | 0           |
| Block RNG          | Binary Matrix Rank   | 2.5105e-275 |
| Block RNG          | Non-overlap Template | 0           |
| Block RNG          | Maurer Universal     | 0           |
| Markov p_stay=0.95 | Frequency (Monobit)  | 3.23861e-18 |
| Markov p_stay=0.95 | Block Frequency      | 0           |
| Markov p_stay=0.95 | Runs                 | 0           |
| Markov p_stay=0.95 | Longest Run of Ones  | 0           |
| Markov p_stay=0.95 | Binary Matrix Rank   | 2.5105e-275 |
| Markov p_stay=0.95 | Non-overlap Template | 0           |
| Markov p_stay=0.95 | Maurer Universal     | 0           |

## BB84 / BB92 Metadata

Quantum-inspired generators are interpreted here as bit sources. BB84 QBER is reported as a diagnostic of simulated channel disturbance, not as the main object of study.

```json
{
  "BB84 no Eve": {
    "qber": 0.0,
    "protocol": "BB84-inspired efficient simulation",
    "eve_fraction": 0.0,
    "transmitted_qubits": 800000,
    "sifted_bits": 400253,
    "estimated_sifting_rate": 0.50031625
  },
  "BB84 Eve 35%": {
    "qber": 0.08769189954900165,
    "protocol": "BB84-inspired efficient simulation",
    "eve_fraction": 0.35,
    "transmitted_qubits": 800000,
    "sifted_bits": 399558,
    "estimated_sifting_rate": 0.4994475
  },
  "BB92 ideal": {
    "qber": 0.0,
    "protocol": "BB92-inspired efficient simulation",
    "transmitted_qubits": 1600000,
    "conclusive_events": 400345,
    "estimated_conclusive_rate": 0.250215625
  }
}
```

## Interpretation

Low p-values indicate that a sequence is unlikely under the ideal iid Bernoulli(1/2) model for the statistic considered. Flawed generators are included as negative controls: biased sources should fail balance-sensitive tests, periodic sources should fail structure-sensitive tests, and Markov/block sources should fail transition and compressibility tests.

## Sequence Length Dependence

Short sequences may produce less stable p-values because asymptotic approximations have less information to work with, and some tests require a minimum number of bits. Longer sequences provide more reliable statistical evidence, but passing a test battery does not prove true randomness.

|   length | generator          |   tests_run |   tests_passed |   pass_rate |   min_p_value |   median_p_value |
|---------:|:-------------------|------------:|---------------:|------------:|--------------:|-----------------:|
|     1000 | BB84 Eve 35%       |           7 |              4 |    0.571429 |  0.0664271    |     0.572419     |
|     1000 | BB84 no Eve        |           7 |              3 |    0.428571 |  0.0010532    |     0.238606     |
|     1000 | BB92 ideal         |           7 |              4 |    0.571429 |  0.301707     |     0.623992     |
|     1000 | Biased p(1)=0.70   |           7 |              0 |    0        |  0            |     1.36148e-28  |
|     1000 | Block RNG          |           7 |              0 |    0        |  0            |     7.71575e-30  |
|     1000 | Markov p_stay=0.95 |           7 |              0 |    0        |  6.88808e-171 |     3.23014e-11  |
|     1000 | NumPy PCG64        |           7 |              4 |    0.571429 |  0.615349     |     0.753052     |
|     1000 | Periodic 0101      |           7 |              2 |    0.285714 |  1.79583e-219 |     0.5          |
|     1000 | Python Mersenne    |           7 |              4 |    0.571429 |  0.338137     |     0.821306     |
|    10000 | BB84 Eve 35%       |           7 |              7 |    1        |  0.158902     |     0.556114     |
|    10000 | BB84 no Eve        |           7 |              7 |    1        |  0.129101     |     0.37439      |
|    10000 | BB92 ideal         |           7 |              7 |    1        |  0.0372219    |     0.0909002    |
|    10000 | Biased p(1)=0.70   |           7 |              1 |    0.142857 |  0            |     5.84569e-148 |
|    10000 | Block RNG          |           7 |              0 |    0        |  0            |     5.36228e-160 |
|    10000 | Markov p_stay=0.95 |           7 |              1 |    0.142857 |  0            |     1.60806e-138 |
|    10000 | NumPy PCG64        |           7 |              7 |    1        |  0.0139531    |     0.499621     |
|    10000 | Periodic 0101      |           7 |              2 |    0.285714 |  0            |     1.75881e-124 |
|    10000 | Python Mersenne    |           7 |              7 |    1        |  0.120605     |     0.499621     |
|   100000 | BB84 Eve 35%       |           7 |              7 |    1        |  0.0638702    |     0.615277     |
|   100000 | BB84 no Eve        |           7 |              7 |    1        |  0.0465473    |     0.543264     |
|   100000 | BB92 ideal         |           7 |              7 |    1        |  0.176908     |     0.627039     |
|   100000 | Biased p(1)=0.70   |           7 |              1 |    0.142857 |  0            |     0            |
|   100000 | Block RNG          |           7 |              1 |    0.142857 |  0            |     0            |
|   100000 | Markov p_stay=0.95 |           7 |              1 |    0.142857 |  0            |     0            |
|   100000 | NumPy PCG64        |           7 |              7 |    1        |  0.0513392    |     0.770086     |
|   100000 | Periodic 0101      |           7 |              2 |    0.285714 |  0            |     0            |
|   100000 | Python Mersenne    |           7 |              7 |    1        |  0.20423      |     0.51202      |

## BB84 Eve Fraction Dependence

Eve should increase QBER in the BB84 simulation because intercept-resend measurements disturb Alice/Bob correlations. Classical randomness tests may not detect Eve directly: QBER measures protocol security and correlation disturbance, while NIST-style tests measure statistical properties of the extracted bit sequence. These diagnostics are related, but not identical.

|   eve_fraction |      qber |   tests_run |   tests_passed |   pass_rate |   min_p_value |   median_p_value |
|---------------:|----------:|------------:|---------------:|------------:|--------------:|-----------------:|
|           0    | 0         |           7 |              7 |           1 |     0.310948  |         0.723104 |
|           0.1  | 0.0252821 |           7 |              7 |           1 |     0.296693  |         0.474426 |
|           0.2  | 0.0502583 |           7 |              7 |           1 |     0.0349706 |         0.422689 |
|           0.3  | 0.0748921 |           7 |              7 |           1 |     0.0973067 |         0.53216  |
|           0.35 | 0.0869204 |           7 |              7 |           1 |     0.0658098 |         0.39241  |
|           0.4  | 0.100755  |           7 |              7 |           1 |     0.269298  |         0.697093 |
|           0.5  | 0.124055  |           7 |              7 |           1 |     0.0437707 |         0.480306 |

## Shannon Entropy and Autocorrelation

Shannon entropy measures uncertainty in the marginal bit distribution. It is useful for detecting biased generators, but it does not fully characterize randomness. High Shannon entropy alone does not imply randomness: a periodic 0101 sequence can have entropy close to one bit per symbol while remaining completely predictable due to correlations. Autocorrelation helps detect temporal structure and dependence, so entropy and autocorrelation should be treated as complementary diagnostics, not replacements for the statistical battery.

| generator          |       p0 |       p1 |   normalized_entropy |   lag1_autocorrelation |   max_abs_autocorrelation |
|:-------------------|---------:|---------:|---------------------:|-----------------------:|--------------------------:|
| NumPy PCG64        | 0.501765 | 0.498235 |             0.999991 |           -0.00166749  |                0.00412834 |
| Python Mersenne    | 0.498465 | 0.501535 |             0.999993 |            0.00233561  |                0.00682599 |
| Biased p(1)=0.70   | 0.29961  | 0.70039  |             0.880814 |           -0.00248567  |                0.00401972 |
| Periodic 0101      | 0.5      | 0.5      |             1        |           -1           |                1          |
| Block RNG          | 0.49584  | 0.50416  |             0.99995  |            0.938105    |                0.938105   |
| Markov p_stay=0.95 | 0.50973  | 0.49027  |             0.999727 |            0.900192    |                0.900192   |
| BB84 no Eve        | 0.50172  | 0.49828  |             0.999991 |            0.000973183 |                0.00559936 |
| BB84 Eve 35%       | 0.50088  | 0.49912  |             0.999998 |            0.00384193  |                0.00570717 |
| BB92 ideal         | 0.49996  | 0.50004  |             1        |           -0.000375008 |                0.00446039 |

## Quantum Circuit Demonstration

The Qiskit demo is optional and was not run in this report (RUN_QISKIT_DEMO is disabled by default.). Large-scale statistical analysis still uses efficient classical simulation.