# PARADIGM P13 — Tropical / Degeneration Methods (worked example + decision tree + code skeleton)

Aporia P86, 2026-08-21. Source: taxonomy P13; no DR grounding in BACKCORPUS
(checked). Consumer: Learner corpus type C. Emitted to paradigm_trees.jsonl.

**The move**: replace smooth geometry with a piecewise-linear combinatorial
shadow at the boundary; the degeneration remembers enough to reconstruct
(verb: DEGENERATE-TO-SKELETON; payoff verb:
COMPUTE-COMBINATORIALLY-WHAT-WAS-GEOMETRIC).

## 1. Worked example — EXECUTED (`paradigm_p13_worked_example.py`)

Puiseux valuation degeneration — the paradigm at its root: for A(t) with
entries c_ij·t^(v_ij), the valuation of det A(t) as t→0 equals the TROPICAL
determinant (min over permutations of Σ v_i,σ(i)) whenever the minimizer is
unique. The smooth object (determinant) degenerates to a combinatorial one
(assignment problem) and the shadow remembers the leading behavior exactly.

- 2×2 hand gate PASSED; tropical determinant computed by its DEFINITION
  (brute force over permutations), measured valuation by a two-point exact
  slope (det is a polynomial in t — the lowest term dominates).
- 60 random 4×4 draws: **44/44 generic cases match EXACTLY** (slope rounds to
  the tropical determinant); **16 tie cases skipped WITH COUNT** — where the
  minimizing permutation is not unique, cancellation can occur and the
  correspondence honestly does not apply. The skip census is the example's
  most instructive part: degeneration theorems carry genericity hypotheses,
  and the instrument detects (from the tropical side alone) exactly when they
  fail. Verdict: **SHADOW-REMEMBERS**.

## 2. Decision tree

- Q1: Does the object live in a FAMILY with a boundary/limit (a parameter
  t→0, a toric degeneration, a valuation)? — NO: nothing to degenerate;
  tropicalizing a single rigid object is decoration.
- Q1 YES — Q2: Is there a CORRESPONDENCE THEOREM (or checkable identity)
  saying the combinatorial shadow computes the geometric quantity? — NO: the
  skeleton may amuse but proves nothing; treat shadow counts as conjecture
  generators only.
- Q2 YES — Q3: Can you DETECT the genericity hypotheses from the
  combinatorial side (unique minimizer, transverse intersections)? — NO:
  silent non-genericity is the paradigm's classic failure — the shadow lies
  precisely when you cannot tell; build the detector first.
- Q3 YES — EXECUTE: compute the shadow by definition, the geometric quantity
  independently, reconcile on generic instances, and CENSUS the non-generic
  skips — a correspondence verified only where it applies, with the boundary
  measured, is the honest form.

## 3. Code skeleton

```python
def degeneration_attack(samples, shadow_fn, geometric_fn, genericity_fn):
    """P13 template. Genericity detected from the shadow side BEFORE
    comparing; skips censused, never hidden."""
    matches = mismatches = skips = 0
    for s in samples:
        if not genericity_fn(s):
            skips += 1
            continue
        matches += (shadow_fn(s) == geometric_fn(s))
        mismatches += (shadow_fn(s) != geometric_fn(s))
    return {"matches": matches, "mismatches": mismatches, "skips": skips,
            "verdict": "SHADOW-REMEMBERS" if mismatches == 0 and matches else "SHADOW-FORGETS"}
```

## 4. Catalog assignment

Primary: none of the current catalog rows are degeneration-shaped — recorded
honestly (the second empty primary after P06; the taxonomy's own Prometheus
note points at tensor-degeneration INTERNAL targets, not catalog rows).
Secondary/enabler: 0334 (volume conjecture sits at a quantum-classical
degeneration boundary), 0026-class (Berkovich/log methods appear in modern
uniformity proofs — an enabler, not an instrument we run). Anti-assignment:
all pure-arithmetic and statistics rows (0057-0062, 0137, 0165, 0175,
0479-0485) — no family, no boundary (Q1=NO).

## Provenance and honesty

The valuation-degeneration identity is classical non-archimedean algebra; the
content is the definition-computed shadow, the two-point exact slope
measurement, and above all the genericity DETECTOR with its skip census — the
paradigm's classic failure mode (the shadow lying silently) made mechanically
visible. Second honest empty primary assignment; the pattern (flow, tropical)
suggests the geometry-native paradigms await the tensor-internal targets the
taxonomy anticipated.
