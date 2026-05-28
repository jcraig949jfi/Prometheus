# 5-Gen REAL Implementation Validation Report
**Date:** 2026-05-28
**Stages 11-16 of pivot/techne_5gen_plan_2026-05-27.md** (extended)

## Summary

All 5 monoculture-breaking generators (k1/l1/m1/n1/o1) have been
upgraded from stub to real, validated by 51 passing tests (26 v0 +
25 v1) and isolation fires on each.

**Key qualitative shift:** l1 and m1 now produce REAL KILLS with
witnesses and minimality certificates — the substrate is now
emitting falsification-with-evidence records, not just parity
tautologies.

## Per-gen results from isolation fires

### `k1` typed_bridge — 4,952 records
- Iterates 11 paths × (52 knots + 1000 ECs) = ~11,572 candidates;
  emits ~5K where the arrow chain computes successfully
- Each record carries the FULL computed morphism chain with
  target_value attached
- Templates: same signature template (one per path_id), but
  4,952 distinct records (catalog × path)
- Verdict: all UNVERIFIED (k1 doesn't self-verify; downstream
  sigma kernel routes)

### `l1` obstruction — 12 records, 4 REJECTED
- 12 templates ran bounded search synchronously
- 4 obstructions REFUTED by witnesses found in catalog
  (kill_pattern="obstruction_refuted_by_witness")
- 8 obstructions CONFIRMED within bound (SHADOW_CATALOG)
- Witnesses are real catalog labels (e.g. "ec:5077.a1")
- Templates: +2 disc-role lifetime templates

### `m1` minimal_counterexample — 9 records, 6 REJECTED
- 9 conjectures enumerated against real catalogs
- 6 minimal counterexamples FOUND with full enumeration
  certificates (kill_pattern="minimal_counterexample_found")
- 3 conjectures HELD across the catalog (SHADOW_CATALOG)
- Certificates include strictly-smaller passing object sizes
  and labels — minimality is reproducible
- Templates: +2 disc-role lifetime templates

### `n1` active_disagreement — 914 records
- Sampled 600 (knot, EC) value pairs from real catalogs
- Tested each through 3 verifier pairs (exact_parity vs
  abs_diff_le_3 / abs_diff_le_10 / mod_3_equivalence)
- 914 actual disagreements emitted (~50% rate per pair × verifier
  combination)
- Each disagreement has subject_record_hash for reproducibility
  and both verifier names + verdicts

### `o1` conjecture_neighborhood — 22 records
- 7 theorems × 9 operators with applicability filter by
  hypothesis kind
- Generated all valid (theorem, hypothesis, operator) triples
- Each record records the original hypothesis list, the
  specific perturbed hypothesis, the operator id, and the
  conjectured effect

## Aggregate

| metric | stub-era | real-era |
| --- | --- | --- |
| Total records per gen run | 3-4 each | 12-4952 each |
| Total across 5 isolation fires | 18 | 5,909 |
| Kills with evidence (REJECTED) | 0 | 10 |
| New disc-role templates | +6 | +4 |
| Witnesses / certificates | none | l1 + m1 |

(Template counts grew less because the daemon's signature index
groups records by template, not by content. Each k1 record shares
a template with all other k1 records using the same path_id.)

## Tests

- 26 v0 tests (shape validation): all green
- 25 v1 tests (real-behavior validation): all green
- Total: **51/51 green**

## Open: what real-er still means

Even these "real" implementations are mathematically conservative:
- k1 uses a small arrow registry hand-coded with the catalog's
  available fields. Real-er: pull arrows from a typed-morphism
  catalog (e.g. an OEIS-style registry of "knot.X → number_field
  arrow exists with computation recipe...").
- l1's 12 obstruction templates are useful but small. Real-er:
  expand to hundreds; integrate with LMFDB API.
- m1 enumerates within available catalogs. Real-er: when a
  conjecture HOLDS across the full catalog, attempt to extend
  the catalog and re-search.
- n1's verifier set is 3 pairs. Real-er: hook in the actual
  sigma_kernel and the live polyfit precision verifiers.
- o1's 7 theorems are textbook. Real-er: add 100+ from the
  Aporia/Sphinx catalogs; introduce LLM-proposed perturbations.

But all 5 are now well past stub-quality. They produce SHAPE_NEW,
content-derived, structurally-complete records.

## Recommended next steps

1. Run a normal `--bandit` fire with all 40 active gens (35 old +
   5 new). Inspect which new gens get picked and how their records
   distribute.
2. Stratified-sample the new records and re-run the LLM-judge
   prompt (pivot/triage_judge_prompt.md). The 6-label triage now
   has new shapes to evaluate.
3. If l1 / m1 kill records persist as "useful_negative" labels in
   triage, double down on bounded-search gens.
4. If o1 / n1 / k1 produce "candidate" labels, those become the
   first real candidates for the Lean 4 autoformalization gate.
