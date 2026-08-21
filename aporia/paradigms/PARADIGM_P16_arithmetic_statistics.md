# PARADIGM P16 — Modular / Arithmetic Statistics (worked example + decision tree + code skeleton)

Aporia P88, 2026-08-21. Source: taxonomy P16; DR grounding 00053 (Bhargava-
Shankar arithmetic statistics — opened, headline read: Selmer distributions,
average ranks, geometry-of-numbers). Consumer: Learner corpus type C.
Emitted to paradigm_trees.jsonl.

**The move**: lift mod-p local data to global conclusions via density and
distribution (verb: DISTRIBUTE-THE-FROBENIUS; payoff verb:
READ-GLOBAL-STRUCTURE-FROM-LOCAL-STATISTICS).

## 1. Worked example — EXECUTED (`paradigm_p16_worked_example.py`)

Sato-Tate at data scale, with the decline leg built in:

- Non-CM forms 11.2.a.a and 37.2.a.a: normalized traces a_p/(2√p) over 167
  good primes match the DERIVED semicircle CDF (endpoint-gated) at
  KS 0.042 / 0.052, beating uniform (0.099 / 0.108). **CONFIRMS.**
- CM forms 32.2.a.a and 27.2.a.a: zero-fraction **0.521** — the
  supersingular half of CM theory arriving as a raw observable — and
  KS_semicircle 0.26. The instrument **DECLINES**, agreeing with the
  mirror's own is_cm flags without having consulted them for the verdict.
- Hasse gate |a_p| ≤ 2√p asserted on every one of 668 primes (a violation
  would be data-integrity, not statistics). Verdict: **ST-DISCRIMINATES**.

## 2. Decision tree

- Q1: Does the object have LOCAL avatars indexed by primes (reductions,
  Frobenius data, congruences)? — NO: nothing to distribute.
- Q1 YES — Q2: Is there a PREDICTED distribution from theory (Sato-Tate
  class, Chebotarev, Cohen-Lenstra/Bhargava heuristics)? — NO: empirical
  distributions are exploration, not tests; route to hypothesis generation.
- Q2 YES — Q3: Are the arithmetic-integrity gates available (Hasse-class
  bounds, exact ranges) to certify the data BEFORE statistics? — NO: local
  data of unknown integrity poisons every downstream density; gate first.
- Q3 YES — EXECUTE: derived comparator with endpoint gates, two-ensemble
  discrimination (the P04 rule), and a DECLINE leg — a class of objects
  where theory says the distribution differs, verified to differ (a test
  that cannot decline never confirmed anything).

## 3. Code skeleton

```python
def arithmetic_stats_attack(objects, local_data, predicted_cdf, null_cdf,
                            integrity_gate, decline_class):
    """P16 template. Integrity gates before statistics; decline leg mandatory."""
    for cls, expect_match in [(objects, True), (decline_class, False)]:
        for obj in cls:
            xs = []
            for p, val in local_data(obj):
                assert integrity_gate(p, val), f"integrity violation at {obj}, p={p}"
                xs.append(normalize(val, p))
            ks_pred, ks_null = ks_stat(xs, predicted_cdf), ks_stat(xs, null_cdf)
            matched = ks_pred < ks_null and ks_pred < 0.15
            assert matched == expect_match, f"{obj}: expected match={expect_match}"
    return "DISCRIMINATES"
```

## 4. Catalog assignment

Primary: CAT-MATH-0067 (Artin densities — attacked P59-class, this tree
formalizes it), 0479/0483 (race densities ARE Frobenius statistics),
0482 tranche B (Chebotarev densities — batch-4 native), 0063 (rank
statistics per report 00053's Bhargava program). Secondary: 0036/0130
(automorphic statistics), 0057/0058 (singular series are local-density
products). Anti-assignment: 0129/0154/0316 (no prime-indexed local
structure).

## Provenance and honesty

Sato-Tate for these forms is proven (CHT-class) and the CM dichotomy is
classical; the content is the derived endpoint-gated comparator, the per-prime
integrity gate at data scale, and the decline leg agreeing with the mirror's
own CM flags WITHOUT consulting them — two independent routes to the same
classification, which doubles as a small mirror-consistency certificate.
