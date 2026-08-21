# PARADIGM P22 — Polynomial Method / Spectral on Signed Graphs (worked example + decision tree + code skeleton)

Aporia P90, 2026-08-21. Source: taxonomy P22 (round-2 addition; Huang
exemplar). Consumer: Learner corpus type C. Emitted to paradigm_trees.jsonl.

**The move**: CONSTRUCT a signed operator encoding the combinatorial
property; read the bound off its spectrum via interlacing (verb:
SIGN-AND-INTERLACE; payoff verb: COMBINATORIAL-BOUNDS-FROM-CONSTRUCTED-
SPECTRA). Distinct from P04 (spectrum GIVEN) — here the operator is built
for the job.

## 1. Worked example — EXECUTED (`paradigm_p22_worked_example.py`)

Huang's sensitivity-proof engine at small n, all four structural elements:

- **A.** B_n² = n·I verified EXACTLY (integer arithmetic) for n = 1..10 —
  the algebra that forces eigenvalues ±√n.
- **B.** Spectrum ±√n with equal multiplicities confirmed to 1e-9 (n ≤ 8).
- **C.** The interlacing bite: **200/200** random induced subsets of
  threshold size 2^(n-1)+1 (n = 4..8) satisfy BOTH consequences —
  λ_max ≥ √n and a vertex of underlying degree ≥ √n.
- **D.** SHARPNESS (the decline leg, with its derived value): the natural
  half-cube has size 2^(n-1) — one vertex fewer — and its λ_max equals
  **√(n−1) exactly** (verified to 1e-9 for n = 4..8), strictly below √n.
  The threshold is sharp, and the instrument exhibits the bound failing by
  a derived amount exactly where theory says it must.
  Verdict: **INTERLACING-BITES**.

## 2. Decision tree

- Q1: Is the target a COMBINATORIAL bound (degree, sensitivity, independence,
  discrepancy) on objects with a binary/parity property? — NO: this is the
  constructive-spectral hammer; wrong nail.
- Q1 YES — Q2: Can you CONSTRUCT an operator (signed adjacency, weighted by
  the property's parity) whose algebra forces a known spectrum (B² = cI
  class identities)? — NO: without forced spectra, interlacing gives nothing
  quotable; hunt the algebraic identity first — it IS the proof's engine.
- Q2 YES — Q3: Does interlacing (Cauchy, or eigenvalue majorization) connect
  the substructure you care about to the forced spectrum, with the
  combinatorial consequence extractable (λ_max ≤ max degree class)? — NO:
  a forced spectrum with no interlacing route is numerology with better
  algebra; exit.
- Q3 YES — EXECUTE: verify the algebra exactly, the spectrum numerically,
  the bite on random threshold substructures, AND the sharpness below
  threshold with its derived value — a bound demonstrated without its
  sharpness leg overclaims silently.

## 3. Code skeleton

```python
def signed_spectral_attack(build_B, n_range, threshold, derived_below):
    """P22 template. Exact algebra gate, spectrum check, threshold bite,
    and the sharpness leg with its DERIVED below-threshold value."""
    for n in n_range:
        B = build_B(n)
        assert exact_identity_holds(B, n), "algebra gate FAILS - no forced spectrum"
        assert spectrum_matches_forced(B, n)
        for sub in random_threshold_subsets(B, threshold(n)):
            assert bite_holds(sub, n), "interlacing consequence FAILS"
        assert abs(below_threshold_extremum(B, n) - derived_below(n)) < 1e-9, \
            "sharpness leg off its derived value"
    return "INTERLACING-BITES"
```

## 4. Catalog assignment

Primary: none of the current catalog rows are boolean-sensitivity shaped —
recorded honestly; the taxonomy's own note routes P22 at Boolean-function
probes downstream of the substrate's operator-output pairs (Prometheus-
internal). Recast-candidates: 0478 (a signed operator on the zero-gap
structure could encode near-degeneracy — speculative, typed as such).
Anti-assignment: analytic rows (0057-0065, 0165-0175) — no parity structure
to sign.

## Provenance and honesty

Huang 2019 is settled; the content is all four structural elements executed
(the exact algebra gate, the 200/200 bite, and above all the sharpness leg
landing on √(n−1) exactly — a decline value derived before measurement, the
P19 direction-discipline applied). Fifth empty primary, same family as
P06/P13: the constructive-spectral hammer awaits internal boolean targets.
