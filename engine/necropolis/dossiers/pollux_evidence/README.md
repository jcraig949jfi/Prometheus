# Pollux evidence (Necromancer pass, 2026-09-11)

Grave: Pollux, the Charon swarm's numerical-coincidence scanner over
Mahler-measure subsets (charon/agents/pollux/daemon.py, two commits,
ran 2026-05-24..05-30 on M2). Dossier: dossiers/pollux.dossier.json.

Every script is offline and read-only on the repository: no daemon, no
network, no Postgres, no LLM. Each imports or replicates the daemon's own
arithmetic and writes exactly one `*_result.json` beside itself. Run from
the repository root:

    python engine/necropolis/dossiers/pollux_evidence/<script>.py

Seeds are fixed (20260911). The Mahler database is read through the
daemon's own `_load_subset`, so a data-version change in
prometheus_math/databases/mahler.py would show up as changed corr_norm
values in `pollux_rescan_result.json` (today's values match the May 2026
second-channel summaries to 4 dp for the three pairs that survive there).

## 1 Scripts

| script | question | result file |
|---|---|---|
| pollux_rescan.py | Q1 is corr_raw identically 1.0 on the real data? Q2 what does each of the 9 pairs produce today, deterministically? Q3 which kill_patterns are reachable given corr_raw = 1? Q4 does a replay of the v0.6 settle/replace policy reproduce P69's 286-row census? | pollux_rescan_result.json |
| pollux_instrument_null.py | T1 Spearman(sorted, sorted) on independent random draws; T2 the 2026-08-12 prescription (daemon statistic on DB order / shuffled / reversed, all 9 pairs); T3 label-permutation null on corr_norm per pair; T4 PROMOTED rate under pure independence at the daemon's sample sizes; T5 verdict stability when the 'n smallest of the larger subset' truncation is replaced by a random size-n subsample | pollux_instrument_null_result.json |
| pollux_consumer_trace.py | who was wired to the ledger (Hecate, Stygian, Erebos, Ergon greedy Learner) and what each did with the verdict bit; every citation checked as path:line containing the quoted text; runtime-state absence; CONSUMPTION.jsonl rows; Keeper second-channel fields | pollux_consumer_trace_result.json |
| pollux_record_census.py | every prior verdict on the tree in date order with verified path:line (6 primary observations, 9 interpretations, 2 prescriptions, 2 provenance gaps, 1 queue row); daemon commit history; absent artifacts; contradictions on record | pollux_record_census_result.json |

## 2 What was established (executed)

- corr_raw is 1.0 at ledger precision on all 9 pairs (max deviation
  2.2e-16) and on 1000 independent random draws: Spearman of two sorted
  arrays is the identity. `pollux_no_correlation_observed` is unreachable;
  the four-way classifier is a threshold on corr_norm alone.
- Under pure independence at the daemon's n the PROMOTED rate reaches
  0.33 (exponential marginals, n = 24/29). The instrument published no
  chance floor.
- Label-permutation null (T3): 3 of 9 pairs below p = 0.05
  (salem_vs_pisot 0.014, small_deg_vs_large_deg 0.001, narrow_band 0.002);
  the PROMOTED pair deg14_vs_deg16 does not (0.093).
- Truncation sensitivity (T5): the two PROMOTED pairs that beat the null
  are REJECTED in 100% of 200 random size-n subsamples. The verdict is a
  property of the 'n smallest' truncation, not of the subsets.
- Deterministic replay of the v0.6 policy: 15 / 15 / 256 rows over 286
  ticks, pool exhausted at tick 47, three attenuating pairs never settle.
  P69's 86 / 39 / 161 is NOT reproduced; only the total, the three
  never-settling pairs and the absence of no_correlation rows are.
- Consumers: 4 wired, 0 used the verdict bit. Stygian's POLLUX-* path was
  a stub for the whole run; Hecate's >=2-generator rule excludes every
  Pollux pattern by vocabulary; Erebos used pair names; the Ergon greedy
  Learner trained on all 286 rows with gold=False hard-coded (PROMOTED
  rows included) and its own progress note calls the result template
  class-learning.
- Record: the 2026-06-24 claim 'Ergon Learner has ZERO references to
  generator_id=pollux' is false on its own tree (sources.py, 7e38227ee,
  2026-06-10).

## 3 Second channel (Keeper, cited not re-run)

dossiers/_keeper_evidence/intelligence_outputs_census_result.json
(graves.pollux) and fleet_halt_census_result.json. 286 rows, 9 distinct
summaries, 05-24 03:08 .. 05-30 11:55 local, every row success=true,
fleet-wide halt within 45 minutes on 05-30. These rows were written by
the Pollux daemon itself in the same tick as the ledger row: dual-
recorded, single mechanism. They are used to test mechanism predictions
(9 static pairs -> 9 distinct summaries; May corr_norm == today's to
4 dp) and to fix EXECUTION and ECOSYSTEM dates. They do not confirm
P69's ledger counts.

## 4 What is NOT established

- The premise (spacing coincidence between Mahler subsets beyond scale).
  Never fairly tested; T3 shows the normalized statistic is
  non-degenerate, T5 shows the verdicts are truncation artifacts. Neither
  'there is structure' nor 'there is none' is supported.
- P69's census numbers. The ledger is absent from every reachable tree
  and the census was printed in-pass.
- Anything about the ~22.6 h v0.5 window (4 TEST_PAIRS, no settle).

## 5 Absent artifacts

charon/agents/pollux/state/{kill_ledger.jsonl, pair_history.json,
settled_pairs.json, candidate_pool_idx.json}; charon/agents/pollux/
artifacts/ (286 scan_*.md claimed); charon/agents/hecate/artifacts/
gradient_archaeology_20260530T162054Z.md (cited by P69); charon/agents/
stygian/loaders/pollux_survivor.py (never written); charon/agents/pollux/
tests (never written).

## 6 Cleric targets (the weakest points, in the Necromancer's own view)

1. DESIGN vs INSTRUMENT as primary. Both are load-bearing INVALID; the
   ranking (DESIGN deeper because a repaired raw leg leaves the 0.33
   chance floor and 0% truncation stability in place) is a judgement.
   A Cleric arguing INSTRUMENT_ERROR primary -> MEASUREMENT_FAILURE has
   the same evidence.
2. T4's chance floor is bracketed by assumed marginals (uniform 0.05 to
   0.13, exponential up to 0.33), not measured on Mahler marginals.
3. HYPOTHESIS VALID rests on T3 alone (statistic non-degenerate, three
   pairs beat a permutation null). A Cleric may insist on NOT_EXAMINED.
4. The Q4 replay assumes today's data equals May's for all 9 pairs; only
   three pairs are checked against the second channel.

## 7 PORTABILITY DEFECTS (LAW N17; recorded, not resolved)

1. Taxonomy collision: a tautological statistic is admissible as
   IMPLEMENTATION_ERROR (the line), INSTRUMENT_ERROR (the leg cannot
   observe) and DESIGN_ERROR (the contrast is defined around a constant).
   The doctrine gives no rule for ranking them; the primary_cause and
   therefore the classification (NO_FAIR_TEST_ON_RECORD vs
   MEASUREMENT_FAILURE) turn on that ranking.
2. EXECUTION VALID with all runtime state lost: the only execution
   evidence is a second channel written by the same process. The doctrine
   does not say whether single-mechanism dual recording satisfies
   'executed evidence' for VALID.
3. QUEUE.jsonl / ROSTER.jsonl pre-labels (prior autopsy class, dossier
   status) read as certificates to a fresh adjudicator; the charter's
   zero-weight instruction is not in the files themselves.
4. P69's census is unverifiable: printed in-pass, ledger absent, Hecate
   figure cited to a path that does not exist. A prior certificate whose
   inputs are gone can be neither UPHELD nor OVERTURNED on its numbers;
   PARTIALLY_UPHELD is being used for 'form reproduced, numbers
   unverifiable', which is a third state the enum does not have.
5. validate.py's cited-path scan runs relative to its own directory; on a
   scratch copy every repo path is 'unresolved' and the note is
   uninformative. On the shared tree the same scan would resolve them.
   Not a validation error, but a reader will misread the note.
6. SCHEMA requires premise_exclusion as an array; the _TEMPLATE and the
   Coeus dossier omit it, so a fresh writer has no example of its shape
   (first validate run here failed on type str).
7. Contradictory certificates coexist on the tree with no cross-reference
   (06-23 REVIVE 'real signal' and 06-24 RETIRE 'tautology' 24 hours
   apart; 06-24 'ZERO Learner references' beside a Learner corpus that
   yielded 286 Pollux rows). Nothing on the tree links a later reading to
   the one it overturns.
8. Reader divergence on HYPOTHESIS: VALID here means 'well-posed';
   another reader would write NOT_EXAMINED because no fair instrument
   touched it. The doctrine's 'VALID needs executed evidence' does not
   say what counts as evidence for a hypothesis layer when the test was
   never run.

## 8 Final validate.py output (private scratch copy, second run)

    === Necropolis validate.py ===
    schema:   SCHEMA.json OK
    roster:   48 agents, 0 duplicate ids
    dossiers: 8 files checked
    selftest: FAILED-classification rejection FIRED (ok)
    organs:   87 organs in ORGANS.jsonl; executed_by_necromancer=true for 13
    history:  39 counterfactual rows ...; 1 with a repair filed
    monsters: 2 files checked; kill_condition-rejection self-test FIRED (ok); repair-without-counterfactual self-test FIRED (ok)
    ALL GREEN

pollux.dossier.json: 0 errors; note line 'stack 6 INVALID / 0
NOT_EXAMINED; fair_test=UNFAIR; primary=DESIGN_ERROR; certificates
UPHELD, OVERTURNED, OVERTURNED, PARTIALLY_UPHELD, PARTIALLY_UPHELD,
PARTIALLY_UPHELD'. The 8-file / 87-organ counts include sibling passes'
dossiers present on the tree at copy time. validate.py was NOT run on
the shared worktree (it regenerates ORGANS.jsonl and
COUNTERFACTUAL_HISTORY.jsonl in place).
