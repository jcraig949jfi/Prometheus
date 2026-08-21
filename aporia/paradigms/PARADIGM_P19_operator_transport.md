# PARADIGM P19 — Cross-Region Operator Transport (worked example + decision tree + code skeleton)

Aporia P89, 2026-08-21. Source: taxonomy confirmation line (P19 accepted
Tier-1); full definition recovered from
`aporia/docs/prometheus_pivot_research_batch1/report_10_oss_math_substrate_landscape.md`
(operators carried between regions as first-class, signature-keyed objects —
the substrate primitive no external database has). Consumer: Learner corpus
type C. Emitted to paradigm_trees.jsonl.

**The move**: carry an operator from its home region to a foreign region as a
first-class act, with calibration that survives — or fails — measurably
(verb: TRANSPORT-THE-OPERATOR; payoff verb:
REUSE-CALIBRATION-ACROSS-WORLDS).

## 1. Worked example — EXECUTED (`paradigm_p19_worked_example.py`)

The PNT instrument transported from integers to F₂[x]:

- Foreign ground truth by TWO routes: the Gauss/Möbius formula vs brute-force
  factorization census — **12/12 degrees exactly equal** (2, 1, 2, 3, 6, 9,
  18, 30, 56, 99, 186, 335).
- CORRECT transport (the measure transported too: x ↔ 2ⁿ, ln x ↔ n·ln 2):
  prediction 2ⁿ/n; ratio at n=20: **0.999012**.
- NAIVE transport (home formula applied blind): fails by a constant DERIVED
  BEFORE measurement — measured 0.692462 vs derived ln 2 = 0.693147 (0.1%).
  The decline leg fails by a number theory hands you in advance.
- DIRECTION LESSON (the pass's instrument-first catch, on my own derivation):
  the first draft derived the failure constant in the naive/true direction
  (1.4427) while the code measured true/naive (ln 2) — magnitude right,
  orientation wrong. Even decline constants need direction discipline; the
  convention-flip doctrine applies to the paradigm's own certificates.
  Verdict: **TRANSPORT-CALIBRATES**.

## 2. Decision tree

- Q1: Does the operator have a well-defined ANALOG of its inputs in the
  foreign region (a dictionary: primes↔irreducibles, zeros↔eigenvalues)?
  — NO: transport without a dictionary is metaphor; record the missing
  dictionary entries as the gap.
- Q1 YES — Q2: Does the MEASURE/normalization transport too (the ln x ↔
  n·ln q class of correspondences)? — NO: naive transport fails by exactly
  the untransported factor — DERIVE that factor first; it becomes your
  decline constant (with its DIRECTION stated).
- Q2 YES — Q3: Is foreign ground truth computable by an independent route
  (exact formula, census) to calibrate against? — NO: transported readings
  are hypotheses; mark provisional and route to the falsification battery.
- Q3 YES — EXECUTE: calibrate home, transport with the measure, verify
  against foreign ground truth, AND run the naive transport as the decline
  leg — a transport that cannot fail measurably was never calibrated.

## 3. Code skeleton

```python
def transport_attack(operator, dictionary, measure_map, foreign_truth,
                     derived_failure_constant, direction="true/naive"):
    """P19 template. The naive-transport decline leg with its DERIVED,
    DIRECTION-STATED failure constant is mandatory."""
    correct = operator.transported(dictionary, measure_map)
    naive = operator.transported(dictionary, measure_map=None)
    r_c = foreign_truth / correct
    r_n = foreign_truth / naive
    assert abs(r_c - 1) < 0.02, f"measure-transported operator off: {r_c}"
    assert abs(r_n - derived_failure_constant) / derived_failure_constant < 0.02, \
        f"decline leg off its derived constant ({direction}): {r_n}"
    return {"correct_ratio": r_c, "decline_ratio": r_n}
```

## 4. Catalog assignment

Primary: CAT-MATH-0151 (Chowla — the function-field analog IS proven
(Sawin-Shusterman class); transport of the integer instruments to F_q[t] is
the canonical modern move), 0057/0058 (function-field Goldbach/twins as
calibration foreign regions), 0482 (form representability transports to
polynomial forms). Prometheus-internal: THE substrate primitive per
report_10 — the signature-keyed transport tensor is the program's
differentiator, making this tree the closest to the north star. Secondary:
0062/0175 (zeros↔eigenvalues dictionary — the RMT bridge). Anti-assignment:
rows with no known foreign dictionary (0129/0154/0316).

## Provenance and honesty

N(n) = (1/n)Σμ(d)qⁿ/ᵈ is Gauss; the content is the two-route foreign ground
truth, the derived-in-advance decline constant with its direction lesson, and
the recovered definition now written down where the taxonomy only had a
confirmation line — this artifact doubles as P19's missing definition page.
