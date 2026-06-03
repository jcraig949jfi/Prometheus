# Calibration v3c VERDICT — the v2 corpus signal is a claim-shape category error

**Date:** 2026-06-03
**Author:** Techne
**Probe:** `theseus/scripts/calibration_v3c_generator_audit.py`
**Artifact:** `pivot/calibration_v3c_generator_audit_2026-06-03.md`
**Builds on:** `pivot/calibration_v3_VERDICT_2026-06-03.md`

---

## TL;DR

v3 showed v2's ~18.5% corpus contrast survives mutation-exclusion only as a
non-a1 residual, and vanishes (0/96) under a1's uniform sampling. v3c names
exactly which generators inject the residual and WHY. The answer is not
"coupling" and not even "selection bias" in the ordinary sense — it is a
**claim-shape category error**: three generators emit payloads in the same
shape as direct-relation claims, but their SHADOW/REJECTED verdict answers a
DIFFERENT predicate than the one F2's raw-value null evaluates.

```
per-generator contrast on the 96 non-mutated groups (within-generator null):

  gen   groups  promoted  prom_rate  mean_ctr  max_ctr      records   predicate
  g4        96        91     94.79%     0.619    1.000    2,888,840   INVARIANCE (reflection)
  g5        80        78     97.50%     0.639    1.000       21,015   INVARIANCE (scale)
  a3        96        34     35.42%     0.091    0.332    3,196,599   TRANSFORMED (f,g)
  f4        96         0      0.00%     0.009    0.081       21,627   direct
  f2        96         0      0.00%     0.007    0.041       21,627   direct
  f3        96         0      0.00%     0.005    0.021    3,229,630   direct
  a1        96         0      0.00%     0.004    0.030    4,793,352   direct  (uniform floor)
```

Direct-relation generators (a1, f2, f3, f4): mean contrast <= 0.009, 0 groups
promote. Meta-relational generators (g4, g5, a3): the entire residual signal.

---

## The mechanism, confirmed in code

**g4 — reflection-duality** (`theseus/generators/g4_reflection_duality.py:72-78`):

```python
raw_holds       = _evaluate_relation(a_val, b_val, rel)
reflected_holds = _evaluate_relation(-a_val, b_val, rel)
symmetric       = raw_holds == reflected_holds
verdict = SHADOW_CATALOG if symmetric else REJECTED
# payload stores: value_a=a_val, value_b=b_val, relation=rel
```

The verdict encodes `reflection_symmetric` (does the relation's truth value
survive sign-flipping the knot-side invariant). But the payload stores
`(value_a, value_b, relation)` in the SAME shape a1 uses for "does rel(a,b)
hold." F2 reads that shape and tests `rel(a,b)` for its null — a different
question. Contrast pins at 1.000 because reflection-symmetry is common
exactly where the raw relation is False on both sides (both False -> symmetric
-> SHADOW, while rel(a,b)=False -> null~0). Category mismatch, not coupling.

**g5 — scale-invariance**: verdict encodes `rel(k*a, k*b) == rel(a, b)`. Same
shape, different predicate, same 1.000 contrast.

**a3 — functional-identity**: verdict encodes `rel(f(a), g(b))` for unary
transforms f,g, but stores pre-transform `value_a_raw, value_b_raw`. F2's raw-
value null evaluates `rel(a,b)` -> moderate contrast (mean 0.091). This is
exactly v2 caveat #2 ("operator-transformed records"), now quantified.

---

## What this means

1. **No catalog coupling, and now no mystery.** v2's apparent signal was
   F2's group key `(cat_a, inv_a, cat_b, inv_b, relation)` conflating direct-
   relation records (a1/f2/f3/f4) with meta-relational records (g4/g5/a3)
   whose verdicts answer invariance / transformed-relation predicates. Scored
   against a raw-value null, the meta-relational records manufacture contrast.

2. **The fix is a predicate discriminator, not a data hunt.** The content-
   aware filter must only score DIRECT-predicate records against the raw-value
   null. Meta-relational records need their own predicate-appropriate null
   (or exclusion) before they enter the content-aware corpus.

3. **F2's observation-mode tally is currently inflated.** `theseus/daemon.py`
   computes `n_f2_would_promote` over the batch sample including g4/g5/a3
   records. The F1-vs-F2 counterfactual delta (doctrine criterion #5) is not
   honest until the guard lands. **This is the production consequence and it
   is fixed in this same change set.**

4. **Calibration intact.** a1/f2/f3/f4 (genuinely direct) score at the null
   floor (<= 0.009). F2 on direct records is well-behaved; the synthetic v0/v1
   recoveries stand. The substrate detects planted structure and reports the
   true ~zero on the honest direct-relation null.

---

## Remediation (this change set)

`theseus/scoring/content_aware_promote.py`: add a `predicate_kind`
discriminator. A record is scored against the raw-value null ONLY if its
predicate is direct. Resolution order (backwards-compatible):

1. If `claim_payload.predicate_kind` is present, honor it ('direct' scores;
   anything else skips).
2. Else fall back to `generator_id`: meta-relational generators
   {g4, g5, a3} skip; all others score.

Forward path (filed, not in this change set): generators should stamp
`predicate_kind` on emission (g4/g5='invariance', a3='transformed',
a1/f2/f3/f4='direct') so the filter never depends on a generator_id
denylist. That is a small per-generator edit + a record_schema field.

---

## Doctrinal accounting

- `feedback_generic_to_specific_audit`: a generic "corpus has 18% signal" claim
  resolved to a specific, code-located category error in three named generators.
- `feedback_counter_baseline_discriminator`: the within-generator re-pairing null
  is each generator's own counter-baseline; only a1/f-family pass it.
- `feedback_assume_wrong` / `feedback_false_profundity`: a second false signal
  killed; the kill hardened the content-aware filter.
- HARD-5: no bridge story; the finding is "generator predicate-kind, not
  catalog coupling, produced the contrast."
