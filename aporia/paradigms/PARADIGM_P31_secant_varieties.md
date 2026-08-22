# PARADIGM P31 — Secant Variety Geometry (worked example + decision tree + code skeleton)

Aporia P97, 2026-08-21. Source: taxonomy P31 (tensor round; Alexander-
Hirschowitz/Terracini exemplar; catalog refs #5, #18, #21, #26-35, #38-42).
Consumer: Learner corpus type C. Emitted to paradigm_trees.jsonl.
**Tier 30/30 — the taxonomy's final paradigm.**

**The move**: rank-r objects form the r-th secant variety; dimension and
defectivity decide identifiability, and Terracini's lemma makes dimensions
computable from tangent spans (verb: MEASURE-THE-SECANT; payoff verb:
IDENTIFIABILITY-FROM-TANGENT-DIMENSIONS).

## 1. Worked example — EXECUTED (`paradigm_p31_worked_example.py`)

Veronese secants of P² measured by Terracini in EXACT integer arithmetic:

- Tangent blocks built two routes — finite differences of the
  parametrization AND the analytic d·l^(d-1)·m construction — gated to span
  the same 3-space; ranks then computed by Fraction Gaussian elimination
  (no tolerance anywhere in the measurement).
- **A.** Nine (d, r) cases: measured dimension == min(3r, N) exactly.
- **B.** THE decline leg: the Clebsch/Alexander-Hirschowitz exception
  (d=4, r=5) measures **14 on all five draws** against naive 15 — deficit
  exactly 1, direction stated: generic ternary quartics are NOT sums of
  five 4th powers though naive counting says they should be.

**Three instrument-first catches, each mechanism-diagnosed** — the example's
real teaching: (1) the integer point sampler drew PROPORTIONAL triples
(same projective point → coinciding tangents → rank deficit 3) — fixed with
a genericity detector (the P13 lesson applied to this paradigm's own
sampler); (2) FD tangents at larger points made sv-cutoffs scale-fragile —
fixed by exact integer tangents; (3) the two-route gate itself used
matrix_rank's ABSOLUTE tol below the FD noise floor, reading noise as a 4th
dimension while the routes agreed entrywise — relative thresholds only.
Even gates need gates. Verdict: **TERRACINI-MEASURES**.

## 2. Decision tree

- Q1: Is the question about RANKS AS A FAMILY (identifiability, generic
  rank, defectivity) rather than one tensor's rank? — NO: single-tensor
  ranks belong to P15/P29.
- Q1 YES — Q2: Is the variety's tangent space COMPUTABLE at points (a
  parametrization to differentiate)? — YES for Segre/Veronese always —
  build the tangent two routes and gate them against each other.
- Q2 YES — Q3: Is the point sampler GENERIC (distinctness/properness
  detectors on the construction side — proportional points, coincident
  factors)? — NO: fix the sampler; Terracini at non-generic points
  measures the wrong variety silently.
- Q3 YES — EXECUTE: measure dimensions in exact arithmetic where scale
  permits; compare against expected min-counts; treat DEFICITS as the
  signal (defective cases are the theorems — AH's list is exactly the
  exceptions this measurement finds).

## 3. Code skeleton

```python
def secant_attack(parametrization, cases, defective_expected):
    """P31 template. Two-route tangents, genericity-detected sampling,
    exact ranks, deficits read as signal."""
    gate_two_route_tangents(parametrization)
    results = {}
    for (params, r) in cases:
        pts = sample_generic(params, r)          # detector-enforced
        results[(params, r)] = exact_rank(stack_tangents(pts))
    deficits = {k: expected(k) - v for k, v in results.items() if v < expected(k)}
    assert set(deficits) == set(defective_expected), "unexpected (non-)defectivity"
    return {"dims": results, "deficits": deficits}
```

## 4. Catalog assignment

Primary: tensor_open_problems_v1.md #5 (border rank of M⟨n⟩ via secant
defectivity), #26-35, #38-42 (taxonomy refs); pairs with P29 as the dual
framework (variety-theoretic vs scheme-theoretic — either can give a bound
the other cannot, per the taxonomy's own distinction note). The substrate's
identifiability discipline (Kruskal-class certificates, P15's Q4) is the
internal consumer. Anti-assignment: all triage MATH rows.

## Provenance and honesty

Terracini 1911, AH 1995; the content is the tolerance-free measurement
pipeline (exact tangents, Fraction elimination), the deficit-as-signal
reading with the classic exception confirmed five-for-five, and three
mechanism-diagnosed catches — including a gate that needed its own gate.
