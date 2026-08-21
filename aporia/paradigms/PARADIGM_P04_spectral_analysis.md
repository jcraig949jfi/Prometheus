# PARADIGM P04 — Spectral Analysis (worked example + decision tree + code skeleton)

Aporia P82, 2026-08-21. Source: taxonomy P04; DR grounding 00049 (L-function GUE
statistics, read not re-fired). Consumer: Learner corpus type C. Emitted to
paradigm_trees.jsonl.

**The move**: study the eigenvalues of an operator associated with the object
instead of the object itself (verb: SPECTRALIZE; payoff verb:
READ-STRUCTURE-FROM-EIGENVALUE-STATISTICS).

## 1. Worked example — EXECUTED (`paradigm_p04_worked_example.py`)

Montgomery-Odlyzko at entry scale: first 1,000 zeta zeros (mpmath, 20/20
archive-anchor gate at zero drift), unfolded by the Riemann counting function
N(T) = (T/2pi)log(T/2pi) - T/2pi + 7/8, nearest-neighbor spacings vs the Wigner
GUE surmise. Result: mean unfolded spacing **1.0000**, KS vs Wigner-GUE
**0.0432** vs KS-Poisson **0.3224** — **GUE-CONSISTENT** (7.5x discrimination).

**Two instrument bugs caught by the pre-stated gates, in order** — the pass's
real teaching:
1. The first unfolding dropped the -T/2pi term; the mean-spacing gate (must be
   ~1) read 1.2239 and localized the fault BEFORE any ensemble comparison.
2. The first comparator CDF was a Rayleigh-type formula, not the integral of
   the stated GUE density; against a by-then-correctly-unfolded sample it read
   KS 0.24 — a broken yardstick reads a straight rod as bent. Deriving the CDF
   from the density (erf(2s/sqrt(pi)) - (4s/pi)exp(-4s^2/pi)) dropped KS to 0.043.

Spectral statistics have TWO instruments — the unfolding and the comparator —
and each needs its own gate.

## 2. Decision tree

- Q1: Is there a natural OPERATOR whose spectrum encodes the object (Laplacian,
  adjacency, Hecke, transfer, linearization)? — NO: construct one or exit;
  spectra of arbitrary matrices are numerology.
- Q1 YES — Q2: Can you UNFOLD (mean spectral density known/estimable)? — NO:
  raw spacings mix density with correlations; any ensemble comparison is
  confounded (feedback_scale_vs_shape: normalize FIRST). Exit until the density
  is known.
- Q2 YES — Q3: Does the unfolded sample pass its own sanity gate (mean spacing
  ~= 1)? — NO: the unfolding is wrong; fix before comparing (bug 1's gate).
- Q3 YES — Q4: Is the comparator CDF derived/verified (integrates the claimed
  density; endpoints 0 at 0, 1 at infinity)? — NO: derive it; never transcribe
  (bug 2).
- Q4 YES — EXECUTE: compare against AT LEAST two ensembles (target + null) —
  a fit to one ensemble without discrimination against another is unreadable.

## 3. Code skeleton

```python
def spectral_attack(eigs, counting_fn, target_cdf, null_cdf):
    """P04 template. Gates in order: unfold sanity, comparator sanity,
    then two-ensemble discrimination — never a single-ensemble fit."""
    unfolded = counting_fn(eigs)                    # N(E): eigenvalue -> index scale
    s = np.diff(unfolded)
    assert abs(s.mean() - 1.0) < 0.05, f"unfolding broken: mean {s.mean():.4f}"
    for cdf in (target_cdf, null_cdf):              # comparator endpoint sanity
        assert abs(cdf(np.array([1e-9]))[0]) < 1e-6
        assert abs(cdf(np.array([50.0]))[0] - 1) < 1e-6
    ks_t, ks_n = ks_stat(s, target_cdf), ks_stat(s, null_cdf)
    return {"ks_target": ks_t, "ks_null": ks_n,
            "verdict": "TARGET" if ks_t < ks_n else "NULL-OR-BROKEN"}
```

## 4. Catalog assignment

Primary: CAT-MATH-0062/0175 (pair correlation IS this paradigm), 0165
(Keating-Snaith moments), 0478 (multiplicity via spacing floor), 0348-class
(symmetry-type spectra), 0370/0060 (density hypothesis / RH via zero
statistics). Secondary: 0476/0477 (zeta-derivative moments live on the same
zeros). Anti-assignment: 0026/0193 (torsion is discrete-group data, no operator
spectrum in reach — Q1=NO), 0137 (finite congruence checks).

## Provenance and honesty

GUE-consistency of low zeta zeros is a celebrated known; the pass's content is
the anchored, gated, two-ensemble instrument and the two comparator-side bugs
it caught — both now template lessons. n=1000 low zeros carry known
finite-height deviations; KS 0.043 != 0 partly reflects that, stated not hidden.
