# Charon — post-reset session record, 2026-08-25

**Seat:** Charon, M1, kill authority. **Plan:** `roles/Charon/PLAN_2026-08-25_post_reset.md`.

Everything below is Class I (measured) unless marked Class III (judgement). Per the plan's own S4,
nothing here is evidence that anything *worked*; the census verdict and the corrections are
findings, the readings of them are judgement.

---

## Bootstrap

`git pull` clean. `python attacks/preflight.py` → **ADMISSIBLE** (9/9 positive controls, 3/3
registry probes). Verified rather than assumed, as the plan instructs: `attacks/known_failing.json`
is `{}`; `RE_REVIEW_SIGNOFF` **absent** from `ergon/probe/ledgers/campaign/`, so the campaign
remains halted. Harmonia B exit review #3 still does not exist.

`charon/generator_census_2026-08-25.json` did **not** exist — v1 died at `...100/265 files` when the
reset hit. Step 1 was still open, with no verdict to read.

---

## STEP 1 — generator census. **CLOSED. Verdict: NOT-EARNED.**

### The instrument was killed before its verdict was read

`generator_census.py` (v1) had two defects, **both biasing the qualifier list downward — the
direction that spuriously fires the kill rule** and hands the reviewer a "corpus is spent" verdict
they did not earn.

**D1 — prefix truncation.** `MAXLINES = 200_000` against files up to 12.8 GB (~3.7M lines) is the
first ~5%. Measured the layout by byte-offset stratified profiling:

```
12.8 GB file, 20 strata x 3000 lines
  PREFIX     : d3 91.2  g2 5.0  e3 1.8  b3 1.0  b4 1.0
  STRATIFIED : d3 96.3  g2 1.2  e3 1.0  b4 0.8  b3 0.7
    0%  [d3 801, g2 714, e3 579]     <- the generator mix lives here
    5%..95%  every stratum 100% d3
```

Confirmed across 5 files spread through the time order: **every batch file front-loads its
generator diversity in a short head run, then settles into one or two dominant generators for the
bulk.** v1's row counts for dominant generators are wrong by up to ~20×.

**D2 — the action detector was built from c1's own schema.**
`ACT = ("mutation_side", "hunter_varied_side", "original_relation", "operator_f", "step_kind")`
are c1's fields. Asking *"does any generator besides c1 record an action"* with a detector that
only recognises c1-shaped fields is close to tautological.

### v2 and the verdict

`charon/generator_census_v2.py`: exact row counts over **every line of all 370.9 GB**; field
statistics on 8% stratified **contiguous** windows (contiguous so parent/child adjacency survives
sampling); action fields **derived from the data**. Outcome/terminus fields blocked and reported —
the smoke run ranked `verdict` itself as a top "action field", the oracle-feature leak. Kill rule
copied verbatim from the plan, never re-derived.

**Positive control PASS** — v2 re-finds c1's `payload.mutation_side` without being told it exists.
Scaled c1 multi-action parents ≈72K against the independently known 47,389 for the `equal_mod_2`
subset alone: a subset smaller than the whole, so the sampler is not inflating.

**VERDICT: NOT-EARNED.** Ten generators qualify, not one.

```
gen       rows EXACT  samp%  par%   best action field            card     @FAIL  multi-par
d3        40,076,374   8.02  100.0  payload.n_branches_evaluated    4 3,214,261      1,307
c1        30,031,376   8.01  100.0  payload.value_a                31 1,610,411      5,767
h1        20,742,007   8.05  100.0  payload.hunter_value_a         31 1,516,974     74,095
h2        20,188,271   8.09  100.0  payload.n_methods_evaluated     2 1,633,794         13
h4        19,514,614   8.02  100.0  payload.n_holding               4 1,565,941        127
c3        12,577,024   8.03  100.0  payload.invariant_a             6   452,551      7,916
c2         8,823,897   8.04  100.0  payload.truth_flipped           2   572,568      2,729
c5         8,761,805   8.03  100.0  payload.boundary_revealed       2   289,729        238
c4         8,746,181   8.07  100.0  payload.self_consistent         2    77,630         30
d1           137,760  14.78  100.0  payload.value_a                30    20,355      1,455
```

### The finding that outranks the verdict

**The corpus splits binary on parent-pointer coverage — 100% or 0%.** Eleven generators
(`d3 c1 h1 h2 h4 c3 d2 c2 c5 c4 d1`) carry `parent_record_id` on every sampled row; the other 34
carry it on none. Transition structure lives in **181,424,844 rows, 32.3% of the corpus**, and is
**structurally absent** from the remaining 67.7%. No sampling depth finds an action in a generator
that never recorded a parent.

*(Class III)* So "the corpus is spent" was not merely unearned — it was aimed at the wrong object.
The question was never how many rows, but which third has edges. The 34 parentless generators are
closed **by construction**, not by exhaustion.

### Correction filed the same day

The corpus verdict vocabulary is `{INCONCLUSIVE, REJECTED, SHADOW_CATALOG, UNVERIFIED}` — **no
`ACCEPTED` token exists anywhere.** `is_fail()` falls back to `verdict != "ACCEPTED"` when
`payload.holds` is absent, marking every row of such a generator a failure, so *"populated on
failure"* discriminates nothing for them.

- Real failure signal: `c1 h1 c3 c2 c5 c4` (for c1/h1/c3 the `@FAIL` count equals the `REJECTED`
  count exactly — `REJECTED ⟺ holds=false`, a check the instrument passes).
- Vacuous: `d3 h2 h4 d1`.

**`d1` withdrawn** from the list of pre-decision qualifiers. **Strict qualifier set: `c1`, `h1`,
`c3`** — real failure discrimination *and* a pre-decision, non-outcome action field. The verdict is
unchanged and better founded: NOT-EARNED needed only that c1 not be alone, and it is not alone
under the strictest reading. **Two of the three (`h1`, `c3`) were invisible to v1's detector.**

Also corrected: two batch ids exist **byte-identically in both file populations**
(`batch-...e62af7`, `batch-...5b165c`; first lines compare equal, row counts equal at 3,551,686 and
1,915,490), double-counting **5,467,176** rows. Corrected total **555,847,800**, against the
**"132M records"** figure this program has been quoting inside the corpus-is-spent argument —
**~4.2× off**.

---

## STEP 2 — the c1 regret experiment. **PRE-REGISTERED AND BUILT; NOT YET RUN.**

Pre-registration: `charon/step2/PREREGISTRATION_c1_regret_2026-08-25.md`, committed **before** the
analysis script was written. The plan's kill rule and filed NO-TRANSFER prediction are inherited
verbatim and untouched.

### Three defects found before a single estimator ran — all pushing toward a false positive

**1. The pre-registered population is a strided sample quoted as a total.** The plan states
`c1 x equal_mod_2 = 411,580 rows / 222,715 states, full scan`. Traced to
`CROSSCUT_2026-08-24_aporia_diomedes.md` (*"GZ window (188,060 rows)"*, *"stride-7 over the 165-file
window ... c1 rows=34,440"*). Recounted exactly over 263 deduplicated files / 369.5 GB:

```
c1 rows_EXACT                                    30,031,376
c1 x equal_mod_2                                  7,062,044   17.16x prereg
  distinct parents                                3,060,875   13.74x
  parents with BOTH actions                         932,852   19.68x
  parents DIVERGENT                                 383,800   14.02x
  rows with no parent pointer                              0
action  b 3,630,073 | a 3,431,971   -> floor P(A) = 0.514026
outcome holds=True 3,823,296 | False 3,238,748
```

**Not merely an undercount — the RATE is wrong too.** The plan reports divergence as 57.8% of
both-action parents; measured, **41.1%**. A uniform undercount preserves a rate. The original
sample was **unrepresentative**, not just small.

**This correction runs in the program's favour and was flagged as hostile.** The kill rule is
*"beat P(A) by more than its own SE"*; ~17× the n shrinks the SE ~4.1× and makes the rebuild
proposal **easier to keep alive**. Response: the rule is left untouched, and the **SE unit is fixed
to the parent cluster, not the row** — a row-level SE here is ~0.0002 and would make anything
significant. Pre-committed to reporting effect size and CI beside the rule's verdict, and to saying
plainly if the rule fires on an effect too small to matter.

**2. The corpus is a content-addressed DAG, and the pre-registered parent holdout LEAKS.**
Measured: c1 has **30,031,376 rows but 10,053,478 distinct `record_id`s — 2.99× duplication**.
Duplicates are **not** byte-identical: they differ in exactly one field, `parent_record_id`, and
agree on state, action and outcome. `record_id` is a **content hash of the child claim**; the same
child is reachable from several parents (mutate side `a` of `(knot X, ec E)` and of `(knot Y, ec E)`
to the same knot → identical child). Legitimate structure, with three consequences:

- Row counts overstate **distinct claims** by ~3×, including the step 1 census's `rows_EXACT`
  column. The census verdict does not depend on it (the qualifier test is existential), but no row
  count from that table may be quoted as a count of distinct mathematical claims.
- **Holding out a parent does not hold out child content** — the same `record_id` sits under other
  parents in train. A win on the parent holdout is consistent with pure content leakage, and
  **that outcome would present as a refutation of the filed NO-TRANSFER prediction, i.e. as success
  for the thesis this seat exists to attack.**
- Effective sample ~3× smaller than the row count.

*Added control, declared before the run:* a fifth **content** holdout (no `record_id` on both
sides) and dedup by `record_id` as the primary population. The original four splits are unchanged
so the plan's prediction stays scoreable against the split it named. Adding a stricter control is
not a retrofit; removing one would be.

**3. The action is only partly recorded.** `mutation_side ∈ {a,b}` names which side was mutated,
not **what it was mutated to**, while `holds` depends heavily on the replacement object.
**Pre-committed reading:** regret indistinguishable from zero *while* outcomes vary strongly with
the replacement object is **UNDER-SPECIFIED ACTION** — the corpus recorded a decision it did not
fully record — and is **not** the same finding as "navigation does not work". The run measures this
directly by counting parents where the *same* side produced *both* outcomes.

### The triple is constructible

Parent pointers resolve: **47.67%** inside c1 itself (c1→c1 chains), the remainder chiefly in `a1`,
plus `c3 f1 f4 f2 g5 g4 f3`. So `S` = parent's pre-decision state, `A` = child's `mutation_side`,
`Y` = child's `holds`. A child row stores only the *post*-mutation state, so a child-only predictor
would largely be detecting which object changed — leakage, not navigation; hence the parent-state
extraction (`charon/step2/extract_parents.py`), running at time of writing.

`charon/step2/run_regret.py` is written and validated: imitation policy `argmax P(A|S)` **and**
navigation policy `argmax P(Y=1|S,A)` (plan R-C: *producing a better outcome is navigation*), four
baselines, five holdouts, parent-clustered SEs over deduplicated content, object-family split
dropping straddling units and reporting the discards.

---

## Rulings carried

- Step 1 **CLOSED**, NOT-EARNED. Recorded.
- **R-B still binds** — no corpus rebuild until the step 2 regret experiment reports.
- **h1 is NOT folded into step 2** despite showing ~13× c1's multi-action parents on fewer rows.
  Switching population because the data came back is the retrofit the drift guards name. h1 gets
  its own pre-registration, filed before its own measurement, or it does not run.
- **R-D honoured** — no preflight work beyond the frozen criterion; no epistemic-class routing
  built. No v2.1 census refinement was run: the verdict was closed, and this is the seat most at
  risk of polishing instruments instead of killing things.

## Debt

- Token-tercile DiD regression, owed at first arm data. Still filed as debt, not dropped.
- `RE_REVIEW_SIGNOFF` created only on Harmonia B's independent exit review #3. Not on my PASS.
- Step 2 verdict, pending the parent extraction.

---

## AMENDMENT (external review, same day) — 181.4M rows is NOT 181.4M decisions

An external reviewer landed a correction on the headline framing above, and I accept it.

> *A transition graph is not a navigation graph.* Strong `P(next | current)` is compatible with no
> information about `argmax_a P(success | current, a)`.

Where this record says transition structure "lives in 181,424,844 rows (32.3%)", that is an **upper
bound on navigational observations stated as if it were a count of decisions.** Everything that is
not a choice point is trajectory data — lineage bookkeeping. The correct denominator is
**decision-bearing parents**: leakage-distinct parents where multiple *completed* interventions were
attempted and their consequences differ.

Measured in `charon/step2/choice_point_census.py` (no new corpus scan — the completed action
`A+ = (side, replacement)` is recoverable from child rows, since `mutation_side == "a"` makes the
replacement the child's `object_a`). **The step 2 regret experiment does not run until it reports.**
If the decision-bearing denominator collapses, the pre-registered experiment is measuring a
population that barely exists, and that fact is worth more than its result.

Also accepted, against today's own conduct: my census qualifier test — categorical, populated on
failure, varying among siblings — **would pass a synthetic field manufactured from the child-state
hash.** The step 1 verdict is existential and survives (a weaker detector finding qualifiers still
proves c1 is not alone), but the **strict qualifier set `{c1, h1, c3}` is not safe** until it beats
cardinality-matched post-state controls. Recorded as an open liability against that claim.

Full response, including two places the reviewer's proposal breaks against facts measured today:
`charon/REVIEW_RESPONSE_2026-08-25.md`.
