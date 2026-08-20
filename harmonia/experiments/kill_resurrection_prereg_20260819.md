# Pre-registration — Kill-Resurrection Retrodiction (re-keyed on REPRESENTABILITY)

**Author:** Harmonia_M2_C · **Date:** 2026-08-19 · **Status:** BINDING, written before measurement
**Assigned by:** James, reassigned from Aporia deliberately (base-rate question over an
archive; A is conflicted because the router thesis is A's own).
**Source of the ask:** `D:\Prometheus\aporia\docs\META_SYNTHESIS_2026-08-12_v1.md` §5
(v4 correction: keyed on REPRESENTABILITY, not entails-closure, after Harmonia D killed
the closure test as a timeout detector).

---

## 1. The question

Of the program's historical kills, what fraction were **ROUTING ARTIFACTS** — records
that failed to promote because their claim's KIND could not be expressed/dispatched —
rather than **CONTENT FAILURES**, where the claim was evaluated and genuinely did not hold?

## 2. Pre-committed readings (from the ask, not negotiable after seeing data)

- **Resurrects nothing** → the router thesis is dead for this corpus, the nulls were
  real, and the program should face that rather than repair around it.
- **Resurrects a measurable fraction** → a year of nulls is partly instrument-blindness,
  and every downstream conclusion drawn from those kills needs a corpus-scale taint check.

## 3. Reference class (defined before counting, per feedback_base_rate_null_for_pattern_claims)

**Population:** Theseus substrate terminal records. Population-level verdict distribution
is known from `D:\Prometheus\theseus\corpus_health_report.md` (2026-05-18, 394,623 unique
records): REJECTED 255,375 (64.7%) / SHADOW_CATALOG 125,222 (31.7%) / INCONCLUSIVE 14,026 (3.6%).

**The corpus itself is ABSENT on this host** (`theseus/corpus/` contains only `.gitkeep`).
The only per-record sample available is
`D:\Prometheus\pivot\promoted_triage_sample.jsonl` (176 records, 4 strata).

**KILL := verdict == REJECTED.** SHADOW_CATALOG is analysed separately and is NOT counted
as a kill: it is a content-PASS that was never promoted, which is a different failure.

**Denominator discipline:** the sample is stratified with unknown inclusion probabilities,
so only the `S3_random` stratum supports unbiased extrapolation. Headline rates are
reported for S3_random separately from the pooled sample. No population extrapolation is
claimed from the purposive strata (S1/S2/S5).

## 4. Operational definitions

For each killed record, re-evaluate the claim **independently from the stored values**,
using a re-implementation of the relation semantics written from the relation NAME, not
copied from the generator, and never consulting the stored `holds` flag:

- **CONTENT_FAILURE** — independent re-evaluation confirms the relation is violated.
  The kill was correct. Not resurrectable.
- **ROUTING_ARTIFACT (resurrection)** — the claim is representable and independently
  re-evaluates as TRUE, yet the record was killed. This is the class the retrodiction hunts.
- **UNREPRESENTABLE** — cannot be re-evaluated from stored fields (missing operand,
  relation not expressible). Scored `unrepresentable`, **explicitly NOT `resurrected`**
  — this is D's standing test: a meter must not score "cannot decide" as "novel".
- **DISAGREEMENT** — my re-evaluation contradicts the stored `holds` flag. Reported
  separately as an instrument defect regardless of direction.

## 5. Thresholds

- `resurrection_rate = ROUTING_ARTIFACT / KILLS`.
- `resurrection_rate == 0` on n ≥ 50 kills → "resurrects nothing" reading fires. The
  95% upper bound on a zero-count is ~3/n, reported as the honest ceiling rather than
  claiming exactly zero.
- `resurrection_rate > 1%` → "measurable fraction" reading fires; corpus-scale taint
  check becomes owed.
- Between 0 and 1%: report as **inconclusive at this sample size**; do not round to zero.

## 6. Declared prior and conflict

**I predict near-zero resurrection, and I am declaring it before measuring** because I
have already read `theseus/generators/a1_catalog_cross_product.py:183` —
`Verdict.SHADOW_CATALOG.value if holds else Verdict.REJECTED.value` — which ties the
verdict to a content predicate at emit time. 43 of 48 generators contain the same
verdict-on-predicate construction. If the measurement returns near-zero, it is therefore
**weak confirmation of something I already suspected**, and the informative outcome would
be a non-zero rate.

**Conflict note:** I am the seat that killed A's dispositional claim with a base rate
(`REVIEW_20260812_harmonia_C.md` §3). That is a prior in the anti-router direction and
should be weighed against any finding of mine that the router thesis is dead.

## 7. What would falsify the measurement itself

- If REJECTED records carry no evaluable operands, the audit measures nothing and must
  report NOT_EXAMINED rather than zero.
- If the 176-record sample is unrepresentative of the 255K REJECTED population in a way
  I cannot bound, the population claim must be withheld — sample-level only.
- If kill_pattern strings are post-hoc narration rather than the actual gate decision,
  then agreement between kill_pattern and my re-evaluation proves consistency of
  bookkeeping, not correctness of the gate. This is the main threat and is reported in
  the weaknesses.
