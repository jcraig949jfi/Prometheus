# Track D — Replication Across Pipelines

**Role:** Replicator (single-purpose)
**Delegated:** [pending]
**Status:** [pending]
**Expected deliverables:**
  - A clean-room second implementation of `NULL_BSWCD`
  - Execution of the F011 rank-0 residual audit under both implementations
  - Byte-for-byte agreement check of output tuples (or diff report if mismatched)
  - `REPLICATION_COMPLETE` sync message with verdict:
    AGREE_BYTE_FOR_BYTE | AGREE_NUMERICALLY | DISAGREE

---

## Paste-ready prompt

```
You are [Ergon (recommended — different model family from most Harmonia work)
 OR a fresh Harmonia session on a machine separate from where NULL_BSWCD
 was first implemented]. Role: Replicator. Single-purpose job: create an
independent second implementation of the block-shuffle-within-conductor-
decile null and replicate the F011 rank-0 residual audit on it, to test
whether the result depends on the specific code path rather than the
underlying math.

Working directory: Prometheus clone. Pull latest first.

Read first:
  docs/prompts/track_B_F011_unfolding.md        — the audit this replicates
  harmonia/memory/symbols/NULL_BSWCD.md          — v2 spec, defaults
  harmonia/memory/symbols/EPS011.md              — v2 value and audit status
  harmonia/memory/symbols/VERSIONING.md
  cartography/docs/F011_independent_unfolding_check.md  — sessionB's audit report
  cartography/docs/F011_independent_unfolding_results.json  — numerical output

Do NOT read first (important for clean-room):
  harmonia/nulls/block_shuffle.py               — the existing implementation
  harmonia/F011_independent_unfolding_check.py  — the existing audit script
  harmonia/wsw_F011_rank0_residual.py           — existing fit code

You may look at these AFTER you have produced your own working
implementation and confirmed its output against the published NULL_BSWCD@v2
signature. A diff at that point is evidence of divergence, not copying.

Task 1 — Clean-room NULL_BSWCD@v2 reimplementation:

Implement a function `bswcd_null_v2(...)` that matches the NULL_BSWCD@v2
signature exactly as documented in the symbol MD (not as documented in
the harmonia/nulls/block_shuffle.py file — only use the MD spec):

  INPUTS:
    data                DataFrame with conductor column + value column
    stratifier: str     column name to decile-bin (default "conductor")
    n_bins: int         number of strata (default 10)
    n_perms: int        permutations (default 300)
    seed: int           default 20260417
    statistic: Callable recomputed on each shuffle
    shuffle_col: str    column permuted within strata (default "value")

  OUTPUTS:
    null_mean           float64, 4 sig figs meaningful
    null_std            float64, 4 sig figs meaningful
    null_p99            float64
    observed            float64
    z_score             float64, 2 decimal places meaningful
    verdict             "DURABLE" if |z| >= 3 else "COLLAPSES"
    n_strata_used       int
    stratifier          str
    n_bins              int
    n_perms             int
    seed                int
    degeneracy_warning  str if dominant stratum > 20%; absent otherwise

Use your own language/library choices. Write in a different style from
what you would guess is in harmonia/nulls/block_shuffle.py (e.g. use
numpy groupby instead of pandas.qcut; or vice-versa). The goal is maximal
implementation divergence with identical contract.

Task 2 — Replicate the F011 audit:

Pull the same Q_EC_R0_D5 rank-0 data the original audit used (SQL spec in
the Q_EC_R0_D5@v1 symbol MD). Run three audits:
  (a) Canonical UF_CAT unfolding + your NULL_BSWCD[stratifier=conductor_decile, n_perms=300, seed=20260417]
  (b) Same as (a) but stratifier=torsion_bin (the stratifier in EPS011@v2)
  (c) Conductor-shuffle sanity: 50 permutations of conductor assignments, refit eps_0 under UF_CAT, report the 50 refitted values + std

Task 3 — Byte-for-byte comparison:

After your three audits produce their SIGNATURE@v1 tuples, compare them
to the ones in cartography/docs/F011_independent_unfolding_results.json
field-by-field:
  - n_samples: exact match required
  - observed: exact match required to 6 decimals
  - null_mean: match required to 4 sig figs
  - null_std: match required to 4 sig figs
  - z_score: match required to 2 decimals

Output:
  cartography/docs/track_D_replication_results.md with:
    - your implementation (as a committed Python module)
    - the three audit outputs
    - field-by-field comparison table
    - verdict:
        AGREE_BYTE_FOR_BYTE  — all fields exact within documented precision
        AGREE_NUMERICALLY   — fields match to documented precision but some
                              below-precision differences (acceptable)
        DISAGREE            — at least one field differs beyond documented
                              precision; investigate and report which path
                              has the bug

Constraints:
  - Do NOT copy or paraphrase the existing implementation
  - Do NOT modify the existing implementation; add a second one
  - If you find a bug in the original while reading it post-hoc, report it
    separately but do not "fix" it in the original — that is a conductor
    decision

Commit prefix: "Track D replication:"
Sync message type: REPLICATION_COMPLETE with verdict inline

Charter context: after Track B gave F011's residual a SURVIVES-narrow
verdict, the next threshold is replication across code paths. External
review has flagged this as the single most important missing piece: until
we have independent implementations agreeing, every +2 cell is provisional
in disguise. If the replication AGREES on F011, the residual moves from
"surviving candidate under one test" to "surviving candidate under one
test across two implementations" — still narrow, but the first step
toward genuinely scientific evidence. If it DISAGREES, we have caught a
real implementation bug we otherwise wouldn't have seen; that too is
durable progress.
```

---

## Background motivation

From external review of wave 2:

> *"Until you have independent implementations or independent data sources,
> you don't know if you're measuring math or your stack... even a few
> replicated cells become genuinely strong results... Right now, all
> results share a code path + data pipeline. Failures like F043 show how
> dangerous that is."*

After Track A (null discipline) and Track B (F011 audit status to SURVIVES-
narrow), the reviewer identified replication as the single highest-value
next move. It's not optional — without it, the tensor remains an
internally-consistent bookkeeping artifact rather than scientific evidence.

F011 is the right pilot specimen for Track D because:
- it is the only post-F043-retraction non-calibration non-tautology signal
- both outcomes (agree/disagree) are informative
- if F011 replicates, extending to other +2 cells is straightforward
- if F011 fails to replicate, we've caught a bug affecting everything

Narrowing Track D to F011 rather than all 13 correctly-audited +2 cells
is a pragmatic choice — if the pilot agrees, scaling is a trivial future
task; if it disagrees, we want to debug one specimen not thirteen.
