# ARCHAEON v0

    READ FOSSILS -> FIND A POSSIBLE WEAK STRUCTURE -> PROPOSE A PROBE
    and when there is no weak structure: EXPLORE

Archaeon is not a claim judge. See `roles/Archaeon/CHARTER.md`.

    PEW / SFE fossils -> Archaeon -> PostgreSQL experiment queue -> Vivarium
      -> SFE / worlds / players -> PEW -> Archaeon

Archaeon owns one arrow: fossils -> queue.

---

## 1. Detector definitions and thresholds

Six detectors. All arithmetic, no model, every threshold a named constant in
`archaeon/config.py` and written verbatim into each proposal's provenance.

| # | detector | unit | fires when |
|---|---|---|---|
| D1 | `REPEATED_SMALL_DEVIATION` | `(player, region)` cell | effect in `[0.10, 1.00]` family SDs, **block-wise** sign agreement over 4 blocks, `t >= 2.5`, Bonferroni-corrected p over all eligible cells |
| D2 | `SIGN_INSTABILITY` | player-pair × neighbouring region-pair | deltas oppose in sign, both `>= 0.30` family SDs (materiality) **and** both Welch-resolved under Bonferroni (resolution) |
| D3 | `LOCAL_VARIANCE_ANOMALY` | region | `var(region)/var(k=4 nearest)` outside `[0.333, 3.0]`, in **either** direction, with `n>=8` and neighbourhood `n>=16` |
| D4 | `PLAYER_ORDER_REVERSAL` | player-pair × related region-pair | ordering reverses, both margins `>= 0.25` family SDs **and** both Welch-resolved under Bonferroni |
| D5 | `REPEATED_OUTLIER_REGION` | `(family, region, coord bin)` | `>= 3` observations at robust‑z `>= 3.5` off a **median+MAD** family baseline |
| D6 | `BOUNDARY_TRANSITION_HINT` | adjacent bin pair on one axis | gap `<= 0.10`, jump `>= 1.5` pooled SDs, **and** jump `>= 4x` the axis's own median adjacent step |

Design rules the thresholds embody:

* **A cell is never part of the baseline it is judged against.** D1 excludes the
  cell from its family baseline; D3 excludes the region from its neighbourhood.
  Otherwise a large cell drags the baseline toward itself and hides the very
  deviation being looked for.
* **Robust baselines where outliers are the target.** D5 uses median+MAD, since
  a mean/SD baseline is inflated by the rows it is meant to flag.
* **Multiplicity is corrected.** A corpus holds many cells; Archaeon proposes
  once per *corpus*, so the corpus-level false-alarm rate is the one that
  matters. D1/D2/D4 apply Bonferroni over their eligible unit count.
* **Materiality and resolution are separate requirements.** A family-SD
  threshold says nothing about whether a difference of *means* is resolvable at
  the available n. Both are required.

### Eligibility is reported separately from firing

Every detector returns `Eligibility` alongside its signals: how many units of
the corpus could have fired it, and a `blocked_reason` when the answer is zero.
"Nothing fired" and "nothing could have fired" are different facts, and
`archaeon/detectors/__init__.py::eligibility_census` carries both into the
queue record so the second is never read as the first.

---

## 2. How PEW/SFE data are queried

`archaeon/fossils.py`. Structured queries only; no prose is read anywhere.

**SFE** (`var/engine.db`, SQLite schema 6) — `observations JOIN experiments JOIN
worlds`, ordered by `observations.created_seq DESC`. Only observed experiments
count: an experiment with no observation has not happened yet. Ordering is by
the ledger anchor, never by `ts` — wall clock is informational, and ordering by
it would silently reorder the corpus under clock skew.

**PEW** (`ew.fossil_players LEFT JOIN ew.fossil_worlds`, PostgreSQL) —
`namespace='prod'` by default, so `synthetic` and `test` fixtures cannot enter
a production read.

A **CoordinateChart** maps raw fields to `(region, coords, player, metric)`.
It is data, not code, so a new substrate is a new chart rather than a new
detector. Two ship:

    sfe.candidate_score.v0   region=world_id, coords=(spec.candidate,),
                             metric=content.score, player=None
    pew.phenotype_score.v0   region=sfe_world_id, metric=phenotype.score,
                             player=player_id

Every row keeps its anchors (`obs_id`, `exp_id`, `work_id`, `spec_hash`,
`committed_seq`, or `sfe_entry_hash` on the PEW side), so a proposal is
traceable to immutable evidence. `Corpus.corpus_hash()` fingerprints the ordered
row ids **and their metric values**, so "re-run on the same corpus" is checkable
rather than hoped for.

---

## 3. Experiment-generation algorithm

1. Read the corpus (deterministic window, recorded).
2. Run all six detectors; build the eligibility census.
3. Rank (`archaeon/rank.py`):
   * **Merge** signals sharing a probe target. D2/D4 and D3/D5 overlap by
     construction, and two detectors reading the same rows is one observation
     looked at twice — counting them separately would let the suite's
     composition decide which probe wins.
   * **Score** `= w[intent] + w[effect]*effect_norm + w[support]*support_norm`,
     with `DISCRIMINATE 3.0 > REFINE_BOUNDARY 2.5 > REPLICATE 1.0`. Support
     saturates so volume alone cannot outrank a better probe.
   * Ties break on `(intent rank, detector order, signal_id, target_key)` — all
     fixed. Same corpus, same proposal.
4. Build the spec from a fixed detector→probe table (`archaeon/propose.py`):

       D1 -> REPLICATE_AT_COORDINATE (+ nearby control)
       D2 -> INTERPOLATE_BETWEEN      (midpoint: the sign changes in between)
       D3 -> RESAMPLE_REGION          (dispersion needs n)
       D4 -> CROSS_REPLICATE          (both players, both regions)
       D5 -> REPEAT_OUTLIER_CELL      (+ nearby control)
       D6 -> BISECT_BOUNDARY          (halve the interval)

The score is a **scheduling** number: not evidence strength, not a p-value, not
a confidence.

---

## 4. Exploration fallback

`archaeon/explore.py`. Coverage-biased, never uniform — uniform RNG re-samples
dense regions in proportion to their density, the opposite of what archaeology
wants.

1. Enumerate legal `(region, player)` cells from the fossil record. Archaeon
   does **not** invent worlds or players: it cannot check legality of a
   combination the substrate has never instantiated.
2. Count observations per cell.
3. Never-sampled cells win outright; else cells at or below the 25th percentile
   of the occupied-count distribution.
4. Choose with a PRNG seeded from `sha256(corpus_hash | utc_day)`.

`seed`, `seed_inputs`, `candidate_set_hash`, `candidate_count` and `pool_kind`
are all recorded, so the choice is re-derivable: the hash pins the candidate set
the seed indexed into, making a later corpus that would have produced a
different set detectable rather than silently different.

No literature and no semantic prior touches this. The only inputs are counts.

---

## 5. Cadence enforcement

**Six per UTC day, four hours apart, unevadeable by concurrent instances.**
Enforced in PostgreSQL (`archaeon/migrations/`), by three independent
mechanisms so a bug in any one does not lift the limit:

* **(a)** `day_ordinal` 0–5 with `CHECK` and a partial unique index on
  `(lane, utc_day, day_ordinal) WHERE source_reason IN ('weak_signal','exploration')`.
  A seventh proposal has no ordinal to take; two instances racing for one
  ordinal collide on the index. This holds *even if the application code is
  wrong*.
* **(b)** `archaeon.cadence_gate`, taken `FOR UPDATE` first in every enqueue
  transaction, serializing concurrent instances.
* **(c)** an explicit four-hour check against `max(created_at)`, evaluated in
  that serialized transaction using the **database clock**.

Two machines have two system clocks and one database, so only `now()` in
PostgreSQL can order them. `archaeon/clock.py` bans naive datetimes: the M1/M2
local offset is 4–5 hours, the same order as the boundary being policed.

**Autonomy is keyed on `source_reason`, not on a `created_by` name.** A second
Archaeon under a different handle must consume the same quota, or the cap is
evaded by renaming. Human rows (`source_reason='human'`) carry no ordinal and
are outside all three mechanisms by construction.

**Idle Vivarium is not a reason to relax anything.** Nothing in the cadence path
reads queue depth or runner state, and a test enforces that over the parsed AST.

Every decision including refusals is written to `archaeon.cadence_log`: a
refusal that leaves no trace is indistinguishable from a cycle that never ran.

---

## 6. Provenance written into the queue

`source_evidence` is `NOT NULL` and answers, from the row alone:

| question | field |
|---|---|
| which fossils triggered it | `triggering_rows[].anchors` |
| which detector fired | `detector`, `detector_version` |
| what values crossed | `values_at_threshold` / `thresholds_applied` |
| what else was considered | `candidates_considered[]` |
| why this one | `selection{rule, score, score_terms}` |
| signal or exploration | `mode`, plus the `source_reason` column |
| what seed | `exploration.seed`, `seed_inputs`, `candidate_set_hash` |
| against which corpus | `corpus{hash, window, source, coordinate_scales}` |
| under which rules | `rules.config_fingerprint`, `thresholds_version` |
| could anything have fired | `eligibility_census` |

Plus a standing `authority` disclaimer stored in the row rather than assumed.

**Negative authority is enforced mechanically** at the write boundary
(`archaeon/queue.py::assert_no_negative_authority`), not at the point of
generation — guarding at generation leaves every future call site free to
forget. A record containing "exhausted", "disproven", "nothing interesting",
"proves that", "dead end" and similar cannot reach the queue regardless of who
built it.

---

## 7. Synthetic calibration results

Full report: `archaeon/docs/CALIBRATION.md`. 200 seeds per cell.

```
detector                    null    hit   worst-control   separation
-------------------------------------------------------------------
REPEATED_SMALL_DEVIATION   0.040  0.335       0.065        +0.270
SIGN_INSTABILITY           0.000  0.780       0.000        +0.780
LOCAL_VARIANCE_ANOMALY     0.000  0.955       0.040        +0.915
PLAYER_ORDER_REVERSAL      0.000  1.000       0.000        +1.000
REPEATED_OUTLIER_REGION    0.000  1.000       0.000        +1.000
BOUNDARY_TRANSITION_HINT   0.000  1.000       0.020        +0.980
```

**Calibration found four real defects in the first build**, all shipped fixed:

1. **D1's effect band was structurally EMPTY.** `t = effect_sd * sqrt(n)`, so
   `t >= 3.0` needs `effect_sd >= 3/sqrt(n)` — 1.50 at n=4, against a cap of
   1.00. No input could satisfy both. It fired on 43% of *null* corpora (only
   cells with anomalously low internal scatter got through) and 15% of planted
   ones. Fixed: the detector now computes its own attainable floor and reports
   `EMPTY_BAND` as NOT ELIGIBLE; thresholds moved to `min_t=2.5, min_runs=16`.
2. **D1's consistency requirement got harder as evidence accumulated.**
   Requiring every observation to share a sign has probability 0.0086 at n=20
   for a real 0.8σ effect — backwards for a repetition detector. Fixed: sign
   agreement is over **block means**.
3. **D2 and D4 thresholded on family SD, which does not constrain a difference
   of means.** At n=6, σ=0.1, the 0.30-family-SD bar is 0.52 standard errors —
   inside the noise. Null rates were 0.983 and 1.000. Fixed: Welch resolution
   test with Bonferroni, alongside the materiality bar.
4. **D6 could not tell a boundary from a gradient**, firing on 83% of smooth
   trends carrying the same end-to-end change. Fixed: the step must exceed the
   axis's own **median adjacent step** by 4x.

Every planted test is paired with a control of identical structure and no
effect; D6 additionally has a *gradual* control with the same total change.

---

## 8. Known blind spots

1. **Three of six detectors are NOT ELIGIBLE on the live SFE corpus.** Measured
   2026-09-05 over 3241 rows: `spec.owner` is NULL on 2934/2934 joined rows, so
   there is **no player identity anywhere in the corpus**. D1, D2 and D4 cannot
   form their unit. This is a fact about the substrate, not a finding — but it
   means half the detector suite is currently untested against production data
   and only qualified synthetically.
2. **PEW's fossil corpus carries almost no observables.** 12,006 encounters:
   0 with `players`, 0 with `ecology`, 0 with `resources_used` in `prod`. Of
   6006 `prod` player fossils only 2 have a non-null `phenotype.score`, both
   0.5 — zero variance. The PEW chart is therefore structurally unable to fire
   any detector today. Archaeon reads SFE for real work.
3. **D1 is weak.** Peak power ~0.34, and its curve is non-monotone — it *drops*
   above 0.9σ because effects approaching `d1_max_effect_sd=1.00` are truncated
   by its own upper bound. D1 sees a bounded window `[0.625, 1.00]` SDs and is
   blind above it (D5 covers that range instead). Reported, not hidden.
4. **`spec.candidate` is a hash-like integer, not a physical parameter.**
   Coordinate adjacency on the live chart is therefore close to meaningless,
   which makes D2's neighbour radius and D6's boundary hints much weaker than
   the synthetic results suggest. A chart over a real parameter is needed.
5. **Exploration cannot propose an unobserved combination.** Legal cells come
   from the fossil record, so a never-instantiated world/player pair is
   unreachable until something else instantiates it. Archaeon cannot bootstrap
   coverage of a space nothing has entered.
6. **Bonferroni is conservative.** With many correlated units it costs real
   power (visible in D1). A step-down or FDR procedure would recover some, at
   the cost of being harder to audit by hand.
7. **The negative-authority guard is a regex over strings.** It catches the
   listed phrasings; it cannot catch a verdict expressed in novel wording or
   encoded numerically. It is a backstop for the charter, not a proof of it.
8. **`Corpus.corpus_hash` pins what was READ, not what EXISTS.** Two runs at
   different times see different windows and produce different, correctly
   different, proposals. It does not detect that the underlying ledger changed
   beneath a fixed window.
9. **No SFE ledger-integrity re-verification.** Archaeon reads `engine.db`
   directly and does not re-verify the `prev_hash`/`entry_hash` chain, so it
   asserts rather than checks that the record was not altered
   (`SFE_ARCHAEOLOGY_SCHEMA.md` §2).
10. **Vivarium does not exist yet.** The queue's consumer side
    (`status`, `claimed_by`, `result_ref`) is specified and unexercised.

---

## 9. Running it

```
python -m archaeon.run --migrate        # apply archaeon/migrations/*.sql
python -m archaeon.run --census-only    # eligibility census, writes nothing
python -m archaeon.run --dry-run        # full plan, writes nothing
python -m archaeon.run --enqueue        # plan + cadence-checked write
python -m archaeon.calibrate --seeds 200 --power
python -m pytest archaeon/tests/ -q
```
