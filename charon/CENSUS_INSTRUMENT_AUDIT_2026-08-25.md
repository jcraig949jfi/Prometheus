# Instrument audit — generator_census.py (v1) is KILLED before its verdict was read

**Charon, M1, 2026-08-25.** Class I where marked (measured), Class III where marked (judgement).

Post-reset bootstrap ran clean: `git pull` up to date, `python attacks/preflight.py` → **ADMISSIBLE**
(9/9 positive controls, 3/3 registry probes). Verified rather than assumed, per the plan's own
instruction: `attacks/known_failing.json` is `{}`; `RE_REVIEW_SIGNOFF` is **absent** from
`ergon/probe/ledgers/campaign/`, so the campaign remains halted.

`charon/generator_census_2026-08-25.json` did **not** exist. `generator_census_console.log` stops at
`...100/265 files` — v1 died mid-run at the context reset. So there was no verdict to read, and the
plan's step 1 was still open.

Before re-running v1 I audited it. **It has two defects, and both bias the qualifier list DOWNWARD —
the direction that spuriously fires the kill rule and hands the reviewer a "corpus is spent" verdict
they did not earn.** Corrections that run in the program's favour get audited first, not last.

---

## D1 — Prefix truncation (measured)

v1 caps every file at `MAXLINES = 200_000`. The corpus is **370.9 GB** across 265 files
(100 `.jsonl.gz` = 44.9 GB, 165 `.jsonl` = 326.0 GB) at ~3.4 KB/record. Individual files reach
**12.8 GB (~3.7M lines)**. 200K lines is therefore the first **~5%** of the largest file.

That would be survivable if files were homogeneous. They are not. Byte-offset stratified profiling
of the 12.8 GB file, 20 strata × 3000 lines:

```
  PREFIX     : d3 91.2  g2 5.0  e3 1.8  b3 1.0  b4 1.0
  STRATIFIED : d3 96.3  g2 1.2  e3 1.0  b4 0.8  b3 0.7
    0%  [d3 801, g2 714, e3 579]      <- the generator mix lives here
    5%  [d3 3000]
   ...   every stratum 5%..95% is 100% d3
```

Checked across 5 files spread through the time-ordered list — the layout is **general**:

```
batch-...e62af7  12.8GB   b3b4d3e3g2  d3  d3  d3  d3  d3  d3  d3  d3  d3
batch-...202ce7   2.2GB   b1b2d4e5f4  d4f4 d4f4 d4f4 d4f4 d4f4 d4f4 d4f4 d4f4 d4f4
batch-...1300bc   0.0GB   d4q1v1y1z1  d4  d4  d4  d4  d4  d4  d4  d4  d4
batch-...872cd0   0.0GB   d4g2m1n1w1  d4g2n1 d4g2 d4g2 d4g2 d4g2 d4g2 d4g2 d4 d4
batch-...c2cd2c   0.5GB   a1  a1  a1  a1  a1  a1  a1  a1  a1  a1
```

**Every batch file front-loads its generator diversity in a short head run, then settles into one or
two dominant generators for the bulk.** Consequences for v1:

- Its per-generator **row counts are wrong by up to ~20×** for the dominant generators — and those
  are precisely the numbers that get quoted as corpus totals. This is drift guard #3 live, in the
  instrument rather than in the prose.
- The action / parent-pointer statistics for every dominant generator were computed on a head slice
  only, so a generator whose sibling structure appears in its block tail is invisible to v1.

## D2 — The action-field detector was built from c1's own schema (measured)

v1 tests a hardcoded tuple:

```python
ACT = ("mutation_side", "hunter_varied_side", "original_relation", "operator_f", "step_kind")
```

Those five names are **c1's fields**. The question the kill rule asks is *"does any generator besides
c1 record an action on failure?"* A detector that can only recognise c1-shaped fields cannot answer
it — a negative result is close to guaranteed by construction. The census's stated premise is that
the generator list must be **derived from the data**; the same must hold for the action definition,
or the derivation is cosmetic.

---

## v2 — `charon/generator_census_v2.py`

- **Row counts EXACT.** Every line of all 370.9 GB scanned, generator read by byte-regex (no JSON
  parse), 12 workers, largest files first.
- **Field statistics on stratified CONTIGUOUS windows** — 4000 lines every 50000 (~8%), spread over
  the whole file. Contiguous, not strided, so parent/child adjacency survives sampling.
- **Action fields derived from the data**, generator-agnostically: a top-level or `claim_payload`
  field that is (a) categorical, 2–32 distinct scalar values; (b) populated on **failure** rows, not
  only success; (c) takes ≥2 distinct values among rows sharing a `parent_record_id`. (c) is what
  makes an action navigable rather than a label — *the same state was left by two different doors*.
- **Outcome fields blocked and reported, never silently dropped.** The first smoke run surfaced
  `verdict` itself as a top-ranked "action" — the oracle-feature leak. Terminus features (`verdict`,
  `kill_pattern`, `holds`, `*_correct`, `*_score`, …) are known only *after* the step and can never
  be the action. Under this census's directionality a qualifier FOUND is treated as proven, so
  leakage is the dangerous direction; each generator's best blocked field is retained in the record
  under `best_outcome_like_field_BLOCKED` for audit.

**The kill rule itself is NOT re-derived.** It is fixed by the plan and copied verbatim into the
script's docstring, so the verdict does not depend on anyone reading the plan.

### Directionality of the rule under sampling (the honest limit)

Conjuncts (a) and (b) are per-row properties; an 8% stratified sample bounds them tightly.
Conjunct (c) is an **adjacency** property — a contiguous window sees a sibling pair only if both
siblings land in it — so multi-action-parent counts are **LOWER BOUNDS**. Therefore:

- a qualifier **found** is proven (existence survives sampling) → **NOT-EARNED may fire**;
- a qualifier **absent** is not disproven → EARNED is the weaker half of the rule.

Generators meeting (a)+(b) with zero in-window multi-action parents are reported as **NEAR-MISS**,
not dropped. They are the follow-up population.

### Positive control (measured — PASS)

Per the standing posture that a mis-aimed instrument is not protected by its controls, v2 must
re-find the one qualifier known independently. On `batch-20260519T135527Z-a03302.jsonl.gz`
(398 MB gz, 3,642,599 rows exact):

```
c1   rows=1,921,286   ACTION-CANDS  payload.value_a (card 31, 106102 @FAIL, 245 multi-par)
                                    payload.mutation_side (card 2, 106102 @FAIL, 236 multi-par)
     BLOCKED(outcome) verdict, payload.holds
```

**PASS** — `mutation_side` is recovered by a detector that was never told it existed. `value_a`
ranking alongside it is consistent with the plan's own scope stamp for c1 (*binary-side action space
enriched by object choice*).

The same file also shows **`d1`** carrying a non-outcome action candidate on failure with 84
in-window multi-action parents. That is the NOT-EARNED direction, on one file, from the sample — not
yet a verdict, but it is why the census had to be repaired instead of re-run.

---

## Ruling

**v1 is killed as an instrument.** Its verdict field must not be quoted, and had it completed, its
most likely output — `EARNED — c1 is the only qualifier` — would have been an artefact of D1+D2
rather than a fact about the corpus. It stays in the tree as the audited-and-superseded record.

This audit is Class I where it reports measurements and Class III where it judges. It is **not**
evidence that anything worked. The census verdict lands in
`charon/generator_census_2026-08-25.json`, written by v2.

---

# VERDICT — step 1 census, run on v2

`charon/generator_census_2026-08-25.json`, written by `generator_census_v2.py`.
370.9 GB, 265 files, 12 workers, exact row counts + 8% stratified contiguous windows.

**POSITIVE CONTROL: PASS** — c1 re-found as a qualifier by a data-derived detector.

**VERDICT: NOT-EARNED.** The kill rule (fixed by the plan, not re-derived) fires only if c1 is the
sole generator carrying an action field populated on failure. It is not. Ten generators qualify:

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

(d2, 11,825,535 rows, carries parent pointers but shows zero in-window multi-action parents.
34 further generators are listed in the JSON; all have 0% parent-pointer coverage.)

## The finding that matters more than the verdict

**The corpus splits cleanly on parent-pointer coverage, and the split is binary — 100% or 0%.**
Eleven generators (`d3 c1 h1 h2 h4 c3 d2 c2 c5 c4 d1`) carry `parent_record_id` on every sampled
row. The other 34 carry it on none. Transition structure exists in **181,424,844 rows, 32.3% of the
corpus**, and is structurally absent from the remaining 67.7% — no sampling depth will find an
action in a generator that never recorded a parent.

So "the corpus is spent" is not merely unearned, it was aimed at the wrong object: the question was
never *how many rows* but *which third of them has edges*. The 34 parentless generators are closed
by construction, not by exhaustion.

## Corrections against the program's own quoted numbers

- **Double counting, found and fixed.** Two batch ids exist in *both* file populations and are
  byte-identical (`batch-...e62af7`, `batch-...5b165c`; first lines compare equal, row counts equal
  at 3,551,686 and 1,915,490). The v2 total of **561,314,976** therefore double-counts
  **5,467,176** rows. **Corrected corpus total: 555,847,800 rows.**
- **The "132M records" figure quoted across this program is off by ~4.2×** against an exact
  every-line count. That figure has been load-bearing in the "corpus is spent" argument. It is not
  yet clear whether 132M was a failure-only subset or a truncated scan; v2.1 settles it by counting
  verdicts exactly rather than by sampling.
- **Instrument sanity check.** c1's in-window multi-action-parent count is 5,767 at 8.01% sampling,
  scaling to ~72K across all relations. The independently known full-scan figure is 47,389 for the
  `equal_mod_2` subset alone. A subset smaller than the whole — consistent, so the sampler is not
  inflating.

## What I do NOT yet claim (the outcome-leak caveat)

Six of the ten qualifiers win on a field that is plainly **post-hoc**, not pre-decision:
`n_branches_evaluated`, `n_methods_evaluated`, `n_holding`, `truth_flipped`, `boundary_revealed`,
`self_consistent`. My outcome blocklist caught `verdict`, `holds`, `kill_*`, `*_correct` and missed
these. That is the leak direction I declared dangerous, so those six are **not** counted as
established.

**The verdict does not depend on that judgement.** Three generators qualify on fields that are
unambiguously *choices made before the outcome* — `h1` on `hunter_value_a` (74,095 in-window
multi-action parents), `c3` on `invariant_a` (7,916), `d1` on `value_a` (1,455) — alongside c1
itself. NOT-EARNED survives even the strictest reading of the blocklist. v2.1 stores the full ranked
candidate list per generator so the six leaking cases can be re-adjudicated on their runner-up
fields rather than guessed at.

## A result that must NOT be allowed to rewrite step 2

**h1 shows 74,095 in-window multi-action parents against c1's 5,767 — roughly 13× — on fewer rows.**
On the numbers, h1 looks like a better regret population than c1.

The plan pre-registered the regret experiment on **c1**, before this census existed. Switching the
population now, because the data came back, is precisely the retrofit the plan's drift guards name.
**Step 2 runs on c1 as pre-registered.** h1 is filed here as a separate, independently pre-registered
replication target, to be committed with its own kill rule *before* it is measured — not folded into
the c1 result as a convenient upgrade.

## Ruling

- Step 1 is **CLOSED**. The reviewer's "the corpus is spent" verdict is **NOT EARNED** and is
  recorded as such.
- Per plan §5 ordering, the census being incomplete blocked the rebuild decision; it is now complete
  and **R-B still binds** — no rebuild is authorised until the step 2 regret experiment reports.
- Proceed to step 2 on c1.
