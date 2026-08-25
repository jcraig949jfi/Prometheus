# Preregistration — P4, the Z → A* local-intervention neighbourhood assay

**Ergon (driver) · SKULLPORT (M1) · 2026-08-25 · written BEFORE any P4 measurement exists.**

Executing P4 of `roles/Ergon/RESUME_ergon_2026-08-25.md` under the REDESIGN ruling of
2026-08-25. **No number in this file exists yet.** Every quantity below is either a property of
committed code and data (stated with how it was obtained) or a threshold fixed in advance.

**Conflict of interest.** I am the driver, and P4 is the measurement that could close or reopen
the failure-residue thesis that my own campaign depends on. The objective, the thresholds, the
sample sizes, and the four-way partition are fixed here, before collection, for that reason.

---

## 1. What is being measured, and what is not

The ruling: *"You do not want `I(Z;F)`. You want recoverability of `A*` from `Z` under genuine
local interventions."*

- **Not measured:** corpus entropy, channel capacity, `I(Z;F)`, or any further characterisation
  of how much information the residue contains. The ruling states these will not choose the
  branch, and the resume file carries an explicit prohibition against running another one.
- **Measured:** given a recorded failure `Z`, (Q1) does a better nearby action `A*` exist, and
  (Q2) can `Z` predict *which* one it is.

**No LLM is called anywhere in P4** — not as solver, not as judge, not as feature extractor.
Every alternative is executed exactly by table lookup. This is the ruling's seat-time order
point 6 applied literally: *"if the design space is enumerable you already possess the
mechanism — compile facts from it, do not estimate them from its prose."* It is enumerable, so
it is compiled.

---

## 2. The population, and why this one

**Source:** `theseus/corpus/*.jsonl.gz`, 265 batch files, records with `verdict == "REJECTED"`.

**Generator strata.** Rejected-record counts, measured over the three most recent batch files
(a sample, and labelled as one — the full-corpus figure is 132,312,039 rejected rows from the
committed `corpus_scan`):

```
a1 1,155,282   f2 1,018,746   a2 780,533   f3 629,135   a3 590,019
c1   406,708   d2   214,376   g5  46,512   g4  30,966   d1    907   b4 446   b3 346
```

**Admission criterion for a stratum — fixed now.** A generator enters P4 only if its
`claim_payload` exposes the generator's decisions as structured fields whose admissible domains
can be enumerated **from the generator source and the catalogs**, so that a one-field change can
be re-executed exactly. Verified true today for the `a1`/`f2` family:

```
claim_payload = {catalog_a, invariant_a, object_a,
                 catalog_b, invariant_b, object_b,
                 relation, holds, region_coverage_at_emit}
RELATIONS = ("equal", "equal_mod_2", "divides", "abs_diff_le_3")   # a1_catalog_cross_product.py:49
knots catalog  =   52 entries        elliptic-curve catalog = 1,000 entries
```

**Sampling is STRATIFIED, never prefix.** Reading `files[:N]` previously hid 137 of 141
relations and 5 of 8 edge-bearing generators in this very corpus. P4 draws a fixed quota per
generator stratum with a fixed seed, and the inventory is enumerated **before** any sampling.

**Excluded, pre-committed:** `step_trace`. It is a measured STRUCTURAL-ZERO channel (0.551 bits,
82.8% of mass in one value) and it is `None` on the records inspected. **No P4 arm may use it.**

---

## 3. `Z` — the recorded failure representation

Named from the live schema, not from memory. A corpus record carries:

```
batch_id · canonical_claim_text · claim_kind · claim_payload · convergence_status
diversity_score · emitted_at · extras · generator_id · info_density · kill_pattern
kill_vector · method · novelty_estimate · parent_record_id · precision_dps
record_id · sigma_claim_id · sigma_symbol_ref · step_trace · training_weight · verdict
```

**`Z` is defined as exactly:** `kill_pattern`, `kill_vector`, `claim_kind`, `method`,
`canonical_claim_text`, `info_density`, `precision_dps`, and `claim_payload` **with the
intervened field masked**.

The mask is load-bearing. Q2 asks whether the stored failure representation predicts the right
intervention; leaving the field visible would let a predictor read the answer off the input, and
the resulting number would measure nothing. Masking is applied per-candidate, not per-record.

**`generator_id` is EXCLUDED from `Z`.** Raw `kill_pattern` embeds it, so a predictor given both
can identify the stratum and score well by learning the stratum's modal answer. `kill_pattern`
is used with the generator prefix stripped, by the same `GEN_PREFIX` rule the committed
`corpus_scan_full.py` already applies.

---

## 4. The intervention neighbourhood

For a sampled rejected record, the neighbourhood is every record obtainable by changing
**exactly one** `claim_payload` field to another value in its admissible domain:

| field | domain | size |
|---|---|---|
| `relation` | `RELATIONS` minus the current | 3 |
| `invariant_a` | invariants present on catalog A's entries | enumerated from the catalog |
| `invariant_b` | invariants present on catalog B's entries | enumerated from the catalog |
| `object_a` | other entries of catalog A | 51 for knots |
| `object_b` | other entries of catalog B | 999 for elliptic curves |

**Admissibility is the generator's own, not mine.** A candidate is admitted only if the
generator could itself have emitted it: the invariant must exist on that object in that catalog,
and the relation must be one of the four. A candidate whose invariant lookup is missing is
**dropped and counted**, never imputed.

**Exact execution.** Each candidate is evaluated by looking the two invariant values up in the
committed catalogs and applying the relation. No estimation, no model, no sampling.

**Neighbourhood cap.** `object_b` alone has 999 alternatives. Each field is capped at **200
candidates**, drawn with a fixed seed *from the whole domain*, and the cap **and the drawn
fraction are reported** with every result. A silent cap reads as "we searched the
neighbourhood"; this one is stated because it means the assay measures a **sampled** local
neighbourhood, and Q1's answer is a **lower bound** on whether an improving action exists.

---

## 5. THE OBJECTIVE — predetermined, continuous, and per-relation

Fixed now, before any measurement. The objective is a **margin**: how far the claim is from
holding. Larger is better; `≥ 0` means the relation holds.

```
equal          m = -|a - b|
abs_diff_le_3  m =  3 - |a - b|
divides        m = -(|a| mod |b|)          undefined if b == 0 -> candidate dropped, counted
equal_mod_2    m = -((a - b) mod 2)
```

`A*` is the admissible one-field change **maximising `m`**. `improvement = m(A*) - m(Z)`.

**Continuous, not the verdict flip.** The binary `holds` outcome is the thing the corpus already
records; a continuous surrogate is required first, and a binary objective would make "did it
improve" unanswerable for the majority of records that stay false.

**Never pooled across relations.** The four margins live on different scales and different
populations, so combining them is the naive-score-combination error. Every P4 statistic is
reported **per relation**, and a cross-relation figure may not be computed.

**`equal_mod_2` is reported but excluded from the headline.** Its margin takes two values, so
"improvement" is a coin flip in disguise and its `n` is the number of *cells*, not rows.

---

## 6. The two questions, and the thresholds

### Q1 — does an improving `A*` usually exist nearby?
Statistic: the share of sampled records whose neighbourhood contains a candidate with
`improvement > 0`, per relation.

**Threshold, fixed now: "usually" = ≥ 0.50.** The standard error is computed **before** the
comparison and reported beside it; if the interval straddles 0.50, the answer is **UNDECIDED**
and re-measured at a larger quota, never rounded to a side. Quota per stratum is set so that
`SE ≤ 0.02` at `p = 0.5`, i.e. **n ≥ 625 records per relation per generator**, and the attainable
range is checked so the threshold is reachable on the actual data before the result is read.

### Q2 — can `Z` predict which intervention it is?
Task: rank the neighbourhood by predicted improvement, using `Z` only (with the intervened field
masked). Metric: **top-1 accuracy at identifying `A*`**, plus **mean rank of `A*`**.

**The baseline is not chance.** It is the strongest of:
1. uniform random over the neighbourhood;
2. the **stratum's modal intervention** — the field/value that most often produces `A*` in
   training, ignoring `Z` entirely;
3. a **magnitude-only** predictor using nothing but the two invariant values' orders of
   magnitude.

**Q2 is positive only if the `Z`-using predictor beats all three**, on held-out records, by more
than the reported SE. Baseline 3 exists because a prior finding established that this corpus's
outcome variable largely measures **magnitude compatibility** rather than mathematics; if `Z`
only recovers that, it must show as a null against baseline 3, not as a win against chance.

**Held-out split is by GENERATOR and by OBJECT**, not by row. Rows from one generator share a
template, and a row-level split would let the predictor memorise 14 constants — the exact defect
that retracted the h4 ranking positive.

---

## 7. The four-way partition — the decision, fixed in advance

| Q1 | Q2 | conclusion |
|---|---|---|
| actions exist | `Z` cannot distinguish them | **recording is broken** |
| actions usually do not exist | — | **generation is broken** |
| actions exist | `Z` predicts them | **the corpus is more navigational than the entropy work suggested** |
| neither | — | **both layers need replacement** |

Prior stated in the ruling, **to be tested and not assumed**: generation is at least as
important as recording.

**Anticipated trivial outcome, recorded now so it cannot later be sold as a discovery:** the
most likely `A*` is "swap in an invariant of comparable magnitude." If Q1 is positive and Q2 is
carried entirely by baseline 3, then improving actions exist and are **units arithmetic**, and
that is a result about the objective, not about mathematics. It is written here in advance
precisely because it is the outcome most flattering to a positive-sounding headline.

---

## 8. Gate-fire — required BEFORE any real record is read

Per the generalized gate-fire rule, each conclusion must be produced on a constructed world
where it is known in advance. **P4 does not run on the corpus until all four pass.**

1. **Recording-broken world.** `A*` exists by construction; `Z` is randomised. The assay must
   report Q1 positive, Q2 null, and print **recording is broken**.
2. **Generation-broken world.** `Z` is fully informative but every neighbourhood is constructed
   with no improving candidate. Must report Q1 negative and **generation is broken**.
3. **Navigable world.** `A*` exists and is a deterministic function of a `Z` field. Must report
   both positive. **This is the positive control Charon's Ruling 4 requires**, and the assay
   failing it invalidates every reading, including the ones I would prefer.
4. **Magnitude-only world.** `A*` is determined solely by magnitude compatibility. Must report
   Q2 as a **null against baseline 3** — not a win. This is the constructed world for the
   conclusion I least want to mis-report.

---

## 9. Relationship to P3, and the standing constraints

**P3 is not superseded.** P3 is a dose-response ladder on the *arm apparatus*; P4 is an assay on
the *corpus*. They answer different questions, and the resume's ordering — P3 before
*interpreting* P2 or P4 — stands. **P4 may be built and gate-fired before P3 exists; its
corpus results may not be interpreted before P3 reports.**

Standing constraints that apply:

- **HARD RULE.** No statistic implemented by me triggers a terminal verdict until an independent
  implementation, or an independently generated positive/negative control, has exercised the
  exact inference path. §8's four worlds are the controls; they are *necessary, not sufficient*,
  because I wrote them too. An independent implementation of the margin function is requested.
- Read-only on `theseus/corpus/`. P4 writes only to `ergon/probe/ledgers/p4_neighbourhood/`.
- Every number carries executor / host / model / time. Rows ship in the same commit as any
  verdict computed from them.
- Nothing in P4 costs money or a free-lane call.

---

## 10. Acceptance criteria for P4

- The four gate-fire worlds pass, committed, before the first real record is read.
- The inventory is enumerated before sampling; strata and quotas are reported with the drawn
  fraction and the neighbourhood cap.
- Q1 and Q2 are reported **per relation**, each with its SE, each against its three baselines.
- The partition in §7 is answered with committed rows, or the reason it cannot be is recorded.
- No LLM appears anywhere in the pipeline.

---

*Ergon · SKULLPORT · 2026-08-25 · written before the data, by the party the data would unblock.*
