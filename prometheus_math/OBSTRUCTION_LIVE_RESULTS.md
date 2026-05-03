# OBSTRUCTION_LIVE_RESULTS

Live integration of `ObstructionEnv` against Charon's real cartography
data. The synthetic corpus at `_obstruction_corpus.py` planted the
OBSTRUCTION_SHAPE signature deterministically; this run swaps in the
real corpus assembled from `cartography/convergence/data/`.

## Live data shape

**Source files**
- `cartography/convergence/data/asymptotic_deviations.jsonl` — 1534 OEIS
  sequence rows, 701 of which are A14x walks (A148: 201, A149: 500)
  with parseable octant-walk step sets in their OEIS names.
- `cartography/convergence/data/battery_sweep_v2.jsonl` — 103 rows of
  battery-sweep verdicts. 100 carry a `seq_id`; the others are layer-2
  records without per-sequence kill verdicts (skipped by the loader).

**Schema (live data, as observed)**
- battery_sweep_v2 row: `{layer, source, seq_id, delta_pct, verdict,
  kill_tests}` where `verdict ∈ {"KILLED","SURVIVES"}` and
  `kill_tests` is a list of test IDs that fired
  (e.g. `F1_permutation_null`, `F6_base_rate`,
  `F9_simpler_explanation`, `F11_cross_validation`,
  `F14_phase_shift`, `F3_effect_size`, `F13_growth_rate_filter`, ...).
- asymptotic_deviations row: `{seq_id, name, n_terms, known_count,
  short_rate, long_rate, delta_pct, flagged, best_model,
  best_model_aic, best_model_bic, regime_change}`. The OEIS-style
  `name` field embeds the step set as
  `{(dx,dy,dz), (dx,dy,dz), ...}`.

**Live corpus after join (the env's view)**
- `n_total = 701` entries (A148+A149 only, parseable step sets only)
- `n_killed = 6` (unanimous F1+F6+F9+F11)
- `kill_rate = 0.86%`
- `n_steps` distribution: `{4: 78, 5: 623}`
- `has_diag_neg`: `{False: 606, True: 95}`
- `has_diag_pos`: `{False: 658, True: 43}`
- OEIS A-prefix coverage: `A148` (201), `A149` (500)

**The kill_verdict definition** matches Charon's
`UNANIMOUS_BATTERY = {F1_permutation_null, F6_base_rate,
F9_simpler_explanation, F11_cross_validation}` from
`sigma_kernel/a149_obstruction.py`. A row is `kill_verdict=True` iff
all four fired.

## Did Charon's 54x replicate?

**Yes — exactly, then more.** Two ways to read it.

**On Charon's exact A149-only slice** (`a149_obstruction.py` step [4],
re-running his script verbatim):
- 5 OBSTRUCTION_SHAPE matches, 100% unanimous-kill rate
- 54 non-matches, 1.9% unanimous-kill rate
- **lift = 54x** ← Charon's reported number

**On the full A14x corpus** (env's default scope, A148+A149):
- 5 OBSTRUCTION_SHAPE matches, 100% unanimous-kill rate
- 696 non-matches, 0.14% unanimous-kill rate
- **lift = 696x**

Same 5 matches in both cases — exactly the anchors Charon named:
`A149074, A149081, A149082, A149089, A149090`. The two numbers differ
because the broader A14x corpus contains the A148 family (201 mostly
clean sequences) which dilutes the non-match kill rate by ~14×. Both
are correct; both pin the same finding. No discrepancy — the env's
`obstruction_signature_lift_on_live` reproduces Charon's signal at the
sequence level.

The synthetic corpus had ~5% match rate (8/150) with ~100% / ~2% kill
rates → ~50× planted lift. Live data has 0.71% match rate (5/701) but
the lift floor is **higher** because the live non-match population is
much cleaner. So the lift signal an RL agent has to climb is at least
as steep on live data as on synthetic — the *finding* is more concentrated.

## REINFORCE vs random on live data — the experiment

Same harness (`prometheus_math.demo_obstruction.train_random_obstruction`,
`train_reinforce_obstruction`), 1000 episodes per run, 3 seeds:

| Seed | Random mean reward | Random OBSTRUCTION_SHAPE rediscoveries | REINFORCE mean reward | REINFORCE OBSTRUCTION_SHAPE rediscoveries | First REINFORCE rediscovery |
|------|-------------------:|--------------------------------------:|----------------------:|-----------------------------------------:|----------------------------:|
| 100  | 0.000              | 0                                     | 0.000                 | 0                                        | (never)                     |
| 101  | 0.800              | 3                                     | 48.900                | 0                                        | (never)                     |
| 102  | 0.450              | 2                                     | 90.600                | 897                                      | episode **86**              |
| **mean** | **0.417**      | 5 across 3000 eps                     | **46.500**            | 897 across 3000 eps                      |                             |

**Mean lift (REINFORCE / random) = 111.6x.**

When REINFORCE locks onto OBSTRUCTION_SHAPE (seed 102), it rediscovers
it at episode 86 and re-fires the rediscovery on 89.7% of subsequent
episodes — the policy collapses onto the optimal predicate and stays
there. The match A-numbers logged on the first tagged discovery (seed
102):

```
['A149074', 'A149082', 'A149089', 'A149090', 'A149081']
```

— **Charon's exact 5 anchors, by OEIS ID, on the live data.**

## Honest framing

**This is discovery-grade behavior on real data — but with seed
variance that wasn't visible on synthetic.**

What's harder about live vs synthetic:
1. **Sparser signal.** Synthetic corpus had 8 OBSTRUCTION matches in 150
   records (5.3%); live has 5 in 701 (0.71%). The REINFORCE policy needs
   to find a 4-conjunct predicate `{n_steps=5, neg_x=4, pos_x=1,
   has_diag_neg=True}` whose non-empty-match probability under uniform
   action sampling is `(1/61)^4 ≈ 7e-8`. With a sparser positive
   class, the gradient signal is rarer and luck of early exploration
   matters more.
2. **One signature, not two.** Synthetic planted both
   OBSTRUCTION_SHAPE and SECONDARY_SIGNATURE. Live data only has the
   one. So the policy has half as many basins of attraction.
3. **Held-out variance.** The held-out test split (30%) catches at most
   2 of the 5 OBSTRUCTION matches. When the test slice happens to
   contain only the easy non-matches, lift saturates the 1e6 floor;
   when it contains a match, the bonus fires. The 30/70 split is
   coarse for a 5-positive corpus.
4. **Seed dependence.** On synthetic, REINFORCE rediscovered
   OBSTRUCTION_SHAPE on seed 3 at episode 210/1000 (fast, reliable).
   On live, **1 of 3 seeds nails it; 2 of 3 don't converge in 1000
   episodes.** Seed 100 ends with mean reward 0 — REINFORCE explored
   randomly the whole time and never tasted the bonus.

What worked anyway:
- The **manual-rediscovery path is clean.** When we walk the action
  sequence by hand, the env tags `REDISCOVERED_OBSTRUCTION_SHAPE` and
  populates `match_sequence_ids` with the OEIS A-numbers. Substrate-grade.
- **Replication is exact.** The signature finds Charon's 5 anchors,
  no extras, no misses. The features-of dispatch matches `sigma_kernel/a149_obstruction.py::features_of` byte-for-byte.
- **Skip-clean.** Tests degrade gracefully if the data dir isn't
  present (verified — `test_edge_missing_*_file_raises_filenotfound`).

So: the **architecture earns its claim** — the same env, with the
synthetic corpus swapped for the live one, rediscovers Charon's
finding by RL on at least one of three seeds. The 5x bar from
synthetic does not transfer (we got 111x mean lift — but it's driven
by one seed). The discovery happened; it was just less robust than
the planted version.

## Discrepancies and follow-ups

- The **synthetic 5x acceptance bar doesn't apply here.** We measured
  111x mean lift on live data, but with high seed variance (one of
  three seeds got 0). For a clean acceptance criterion on live data,
  we'd want either (a) more seeds (10+) to bound the variance, (b) a
  higher-bandwidth policy that explores faster, or (c) a curriculum
  that warm-starts from synthetic before running live.
- **The held-out lift hits the floor cap of 1e6** when a test slice
  has matches but no non-match kills. This is a feature-of-the-data,
  not a bug, but it caps the discriminative power of the lift signal
  past a threshold. For future runs we should either use a
  log-transformed reward or a finer-grained tie-breaker (e.g. n_match
  in the bonus).
- **The A148 family is mostly silent.** 201 sequences, but only 1
  (`A149312` is in the A149 prefix; A148 has 0 unanimous-kills in our
  corpus). If we want to grow the live battery into a dataset that
  REINFORCE can train on robustly, we need more positive examples —
  Charon's next sweeps over different sequence prefixes (A150*+,
  non-octant walks, etc.) would help here.
- **Sequence_id is now first-class evidence.** When REINFORCE tags a
  rediscovery on live data, the env logs the OEIS A-numbers in the
  match group. This is the substrate-grade artifact: a paper or
  followup can cite "REINFORCE-discovered structural signature
  matched A149074, A149081, A149082, A149089, A149090 — the same five
  Charon's a149_obstruction.py named — at episode 86 of seed 102,
  starting from random initialization."

## Files added / changed

- **NEW** `prometheus_math/_obstruction_corpus_live.py` (~440 LOC) —
  Live adapter: reads battery_sweep_v2.jsonl + asymptotic_deviations.jsonl,
  parses OEIS step sets, joins on seq_id, materializes
  `LiveCorpusEntry` objects with the same shape as `CorpusEntry` plus
  `sequence_id`. Exports `load_live_corpus`, `live_corpus_summary`,
  `obstruction_signature_lift_on_live`, `get_corpus_or_skip`.
- **MODIFIED** `prometheus_math/obstruction_env.py` —
  Added `corpus_source: Literal["synthetic","live"]` constructor flag
  (default `"synthetic"` — backwards-compatible). Live mode loads
  Charon's data automatically. Episode records now carry
  `match_sequence_ids` (OEIS A-numbers caught by the predicate); the
  info dict surfaces them.
- **NEW** `prometheus_math/tests/test_obstruction_env_live.py` (~370
  LOC, 19 tests) — Authority/Property/Edge/Composition coverage on
  live data. All 18 fast tests pass; 1 slow test (REINFORCE-vs-random)
  measures and reports honestly without asserting a fixed lift bar.
- **NEW** `prometheus_math/OBSTRUCTION_LIVE_RESULTS.md` — this file.

The synthetic corpus at `_obstruction_corpus.py` is **untouched** and
remains the default for all existing tests; the synthetic test suite
(`test_obstruction_env.py`) still passes 22/22.

## Bottom line

- Live data file: `cartography/convergence/data/battery_sweep_v2.jsonl`
  (joined with `asymptotic_deviations.jsonl`).
- Live corpus: 701 entries, 6 unanimous-kills, 0.86% baseline.
- Charon's 54x: replicates exactly on his A149-only slice; reads as
  696x on the broader A14x corpus (same 5 anchors, denser
  non-matches). No discrepancy.
- REINFORCE mean reward (3 seeds × 1000 eps) = 46.5; random = 0.42; lift = 111x.
- OBSTRUCTION_SHAPE rediscovered on seed 102 at episode 86, match
  group = `['A149074', 'A149082', 'A149089', 'A149090', 'A149081']`
  — Charon's exact 5 anchors.
- **Discovery-grade on real data, with seed variance.** 1 of 3 seeds
  converged; 2 of 3 didn't reach the bonus in 1000 episodes. The
  finding survives the live integration; the RL learner needs more
  seeds or a curriculum to be robust.
