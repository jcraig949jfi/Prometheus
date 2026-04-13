# Project Prometheus — Summary
## 2026-04-13

---

## Background

Project Prometheus is a computational research project investigating whether different domains of mathematics share a common underlying structure. The central hypothesis is that mathematical objects across domains — elliptic curves, modular forms, number fields, L-functions — are "different cameras pointed at the same primitive," and that this primitive lives in the spectral data of L-function zeros.

The project operates under a strict falsification-first epistemology: every finding is assumed false until every kill path has been exhausted. Findings are tiered from Conjecture through Possible, Probable, Working Theory, and Validated. Only results that survive the full adversarial battery are taken seriously.

### Infrastructure

- **Charon**: DuckDB database (1.1 GB) containing 789K+ mathematical objects across 42 domains, including 31K+ elliptic curves with stored L-function zeros
- **LMFDB Postgres**: Live connection to devmirror.lmfdb.xyz (100M+ rows), providing access to 3.8M elliptic curves, 919K modular forms, and associated L-function data
- **Harmonia**: Tensor train exploration engine with 5 universal coordinate axes (Megethos, Bathos, Symmetria, Arithmos, Phasma), 4 coupling scorers, and an autonomous adversarial ecosystem running at 1.7 attacks/second
- **Adversarial battery**: F1-F38, a suite of 38 falsification tests calibrated against known truths and known falsehoods
- **Two independent machines** (M1/Skullport and M2/SpectreX5) running cross-validated analyses

### Verified Mathematics (not novel, but confirming instrument calibration)

| Theorem | Result | Sample Size |
|---------|--------|-------------|
| Modularity (Wiles et al.) | 100.000% | 971 pairs, 450 a_p coefficients |
| Parity conjecture | 100.0% | 3.8M curves |
| Mazur torsion theorem | 100.000% | 3,824,372 curves |
| Hasse bound | 100.000% | 150,000 curves |
| Conductor positivity | 100.000% | 3,824,372 curves |
| rank = analytic_rank (BSD) | 100.000% | 3,824,372 curves |

These serve as positive controls: the instrument can detect known structure at full precision.

---

## The Kill Count

**17 cross-domain claims killed.** Every proposed "novel bridge" between mathematical domains turned out to be either known mathematics or a statistical artifact.

| Kill | What Died | How It Died |
|------|-----------|-------------|
| 1-8 | Original adversarial controls | F1-F17 (rank-norm, monotonic, slicing, etc.) |
| 9 | Alpha as universal constant | Representation-dependent (1.57 vs 1.07 in different spaces) |
| 10 | Physics-math bridge | 6/8 kills, sparse data artifact (225 objects in 13/182 dims) |
| 11 | Phoneme NN transfer | F33: ordinal matching of small integers. Trivial 1D baseline (rho=0.95) beats phonemes (rho=0.76) |
| 12 | Curvature-obstructs-transfer | Curvature FACILITATES transfer (r=+0.27). Prediction was backwards. |
| 13 | Spectral features crack residual | +5.9% only. Summary stats see arithmetic dimly (rho<0.14) |
| 14 | Knot root GUE | Preprocessing artifact. Raw Alexander var=1.727 (ANTI-GUE) |
| 15 | Within-domain splits | TT-Cross bond = feature dimensionality, not semantic structure |
| 16 | EC-Artin bond | Matches null exactly (7 = 7.0, z=0.00) |
| 17 | 3-way interactions | 0/5 triples show 3-body effects beyond pairwise |

### The Negative Space (10 dimensions carved)

The primitive mathematical structure is:
1. NOT ordinal matching of small integers
2. NOT magnitude/size mediation
3. NOT distributional coincidence (Benford, range)
4. NOT preprocessing artifacts
5. NOT hand-crafted feature engineering
6. NOT group-theoretic tautologies
7. NOT prime-mediated confounds
8. NOT partial-correlation procedural artifacts
9. NOT within-domain feature-space splitting
10. NOT TT-Cross bond dimensions on invariant-level features

---

## Where the Path Points

After 17 kills eliminated every invariant-level and feature-level cross-domain claim, everything converges on one object: **the zeros of L-functions.** Invariants (conductor, torsion, class number) are lossy projections. Features derived from them are shadows of shadows. The zeros encode the full arithmetic-analytic-spectral structure at 8-digit precision.

---

## Surviving Signals

Two signals survived the full adversarial battery and entered the kill protocol.

### Signal A: Spectral Tail Encodes Isogeny Structure

**Claim**: The spacing between the first and second zeros of an elliptic curve L-function correlates with the isogeny class size, after controlling for conductor, rank, local reduction type, CM status, and semistability.

**Data**: 31,073 elliptic curves with 5+ stored zeros, conductor <= 50,000

#### Decisive Test

- Conductor-controlled Spearman correlation: rho = -0.134, p = 3.0e-159
- Shuffled null (500 permutations within conductor bins): z = -25.7, empirical p = 0.000

#### Local Reduction Conditioning

Regression knockout controlling for conductor + bad primes (split multiplicative, nonsplit multiplicative, additive) + rank + CM + semistable:

- Residual rho = -0.1134, p = 1.89e-86
- The signal is **global**, not explained by local Euler factors

#### Survivor Kill Protocol (8 tests)

| Test | Result | Key Finding |
|------|--------|-------------|
| Prime reindexing | SURVIVES | Signal increases 8% after conditioning on a_p distribution |
| Low-zero ablation | SURVIVES | Spacing(gamma_2 - gamma_1) is the primary carrier (rho = 0.134), 3x stronger than any individual zero |
| CM vs non-CM split | PARTIAL | Present in both CM (rho = -0.155) and non-CM (rho = -0.149) with similar strength |
| Low-zero coupling | SURVIVES | Signal strengthens 28% after conditioning on neighboring zero statistics |
| Fine conductor bins (50 bins) | SURVIVES | z = -29.3, 500 permutations |
| Local reduction | SURVIVES | rho = -0.1134, p = 1.89e-86 |
| Twist stability | CONSISTENT | Isogenous curves share identical zeros (range = 0.000000); signal is class-level |
| Asymptotic scaling | DECAYS | alpha = 0.464, close to RMT N^(-1/2) finite-size scaling |

Key observations:
- **Zero repulsion is the carrier.** The gap between gamma_1 and gamma_2 carries the signal, not individual zero positions. Larger isogeny classes correlate with wider zero gaps.
- **Conditioning strengthens the signal.** Removing independent noise sources (a_p stats, neighboring zeros, local factors) increases the measured correlation. This is the signature of a real latent variable partially masked by noise.
- **The signal decays as N^(-0.464).** This exponent is close to 1/2, the characteristic scaling of random matrix theory finite-size corrections, suggesting an underlying exact relationship visible only through fluctuations at finite conductor.
- **Present in both CM and non-CM curves.** Rules out Sato-Tate convergence as the mechanism.

#### Factorization Confound Test

Conditioning on conductor factorization features (omega, Omega, largest prime factor, primality, squarefreeness):

- Signal reduces 28% but survives: rho = 0.096, p = 1.4e-64
- Signal is stronger for conductors with fewer prime factors (omega=1: rho=0.331, omega=5: rho=0.072), consistent with simpler Euler products giving a cleaner spectral signal

#### Synthetic Null Test (Pipeline Validation)

Four synthetic models tested, 200 trials each. **0.0% false positive rate across all models.**

| Synthetic Model | Mean rho | False Positive Rate |
|----------------|----------|---------------------|
| GUE zeros + randomly permuted class_size | -0.000 | 0.0% |
| Real zeros + conductor-predicted class_size | +0.001 | 0.0% |
| Real zeros + factorization-predicted class_size | -0.020 | 0.0% |
| GUE-resampled spacing + real class_size | -0.001 | 0.0% |

The pipeline does not hallucinate. Both the real zeros AND the real class sizes are required to produce the signal. Replacing either side with synthetic data — even conductor-correlated synthetic data — destroys it completely.

### Signal B: Congruence Graph Communities Predict Rank

**Claim**: Communities in a graph where modular forms are connected by a_p congruences (mod 7) correlate with analytic rank.

**Data**: 5,000 weight-2 dimension-1 newforms, level <= 5,000

#### Decisive Test

- Prime-only graph (a_2, a_3, a_5, a_7, a_11 mod 7): chi2 = 128.2, p = 6.8e-24, z = 32.4 vs shuffled null
- Composite-only graph (a_4, a_6, a_8, a_9, a_10): chi2 = 6.9, p = 0.032, z = 2.7
- **Prime/composite ratio = 12x.** The signal lives specifically at prime indices, where automorphic structure resides. The composite graph is essentially noise.

---

## Current Assessment

### What we can say with confidence

1. **The spectral tail signal is statistically real** in our dataset. 29 sigma from null, survives every conditioning test, 0% synthetic false positive rate.
2. **It lives in zero spacing (repulsion), not individual zero positions.** This places it in random matrix theory territory.
3. **It connects algebraic structure (isogeny class size) to analytic structure (zero repulsion)** at the level of isogeny classes.
4. **It decays as approximately N^(-1/2)**, consistent with a finite-size spectral effect.

### What we cannot yet say

1. **Whether the signal persists at large conductor.** Our data is limited to conductor <= 50,000 (DuckDB), mostly <= 5,000. The N^(-1/2) scaling predicts it weakens but doesn't vanish. This needs verification at conductor > 50,000.
2. **Whether this is a new phenomenon or a known consequence** of existing number theory. The connection between isogeny class size and zero spacing may follow from known results about the relationship between isogenies and L-functions that we haven't identified yet.
3. **Whether the signal constitutes a theorem-level discovery.** We have robust empirical evidence and RMT-consistent scaling, but no theoretical mechanism.

### Honest verdict

- Not noise
- Not trivial
- Not yet a theorem-level discovery
- Most likely: a finite-size spectral effect linked indirectly to arithmetic structure, not a new invariant controlling zeros
- Worth pushing further

---

## Remaining Work

### Critical next steps

1. **Extend conductor range.** Query LMFDB Postgres for conductor > 50,000. Confirm N^(-1/2) decay continues and signal doesn't collapse or flip sign.
2. **Independent replication.** Test against Cremona database (different computation pipeline) to rule out database-specific artifacts.
3. **Theoretical hook.** Identify whether existing results (e.g., Katz-Sarnak, isogeny-L-function correspondence) predict the observed coupling and scaling exponent.

### Open questions

1. Does the congruence graph signal (Signal B) survive the same depth of kill protocol applied to Signal A?
2. Is the alpha = 0.464 decay exponent exactly 1/2, or does it converge to a different value at larger conductor?
3. Can the spectral tail signal be connected to known results about isogeny graphs and Hecke operators?

---

## Repository Structure

```
D:\Prometheus\
  charon/data/charon.duckdb           # 1.1 GB, 789K+ objects, 42 domains
  harmonia/
    src/                               # Engine, phonemes, coupling, adversarial
    scripts/                           # Analysis scripts
      survivor_kill_protocol.py        # 5-test kill protocol
      survivor_kill_twist.py           # Twist stability + scaling law
      synthetic_null_test.py           # 4-model pipeline validation
      extended_conductor_range.py      # Factorization confound test
      decisive_test.py                 # Decisive test on both signals
      run_decisive.py                  # Original decisive test
    results/                           # JSON results from all tests
      survivor_kill_protocol.json
      survivor_kill_twist_scaling.json
      synthetic_null_test.json
      extended_conductor_factorization.json
      decisive_test.json
      local_reduction_control.json
    docs/                              # Documentation
      survivor_kill_results.md         # Detailed kill protocol writeup
      survivor_kill_protocol.md        # Protocol specification
      spectral_research_agenda.md      # Research roadmap
      frontier_update_hour14.md        # State dump at hour 14
    paper/                             # LaTeX paper (v4)
  cartography/                         # Domain-specific data and scripts
```

---

*Last updated: 2026-04-13*
*Machines: M1/Skullport, M2/SpectreX5*
*Data sources: Charon DuckDB (local), LMFDB Postgres (devmirror.lmfdb.xyz)*
