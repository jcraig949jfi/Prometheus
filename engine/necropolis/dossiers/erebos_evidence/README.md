# Erebos -- Necromancer evidence

Grave: Erebos (Charon swarm composer, 25 generator archetypes, May 2026).
Investigator: Rhadamanthus (Necromancer fork). Branch rhadamanthus/native-trial-2026-09-11.
Evidence baseline: e17934d9a82855b6e0ae1c0bf54c0cce569b7795. Dossier: ../erebos.dossier.json.

Run from repo root: `python engine/necropolis/dossiers/erebos_evidence/<script>.py`.
Every script resolves the repo root from `__file__`; none talks to the network,
Postgres or a model provider; all write `<script>_result.json` beside themselves.
Pure ASCII throughout. Six executed artefacts (five scripts here plus one rerun
of a repo script), which is above the brief's 2-4 -- see defect D14.

Labels used in the dossier: `[EXECUTED ...]` = number produced by a script in
this directory; `[EXECUTED-BY-KEEPER ...]` = number from the Keeper's agora
census, cited not re-queried; `[QUOTED ...]` = historical number, not
re-measured; `[READ ...]` = code or prose inspected, not executed.

## 1. Primary sources

| kind | path | what it is |
|---|---|---|
| code | charon/agents/erebos/daemon.py | ErebosAgent.run_tick; `_enqueue_to_stygian` writes the stygian_priority row |
| code | charon/agents/erebos/generators/ (25), `_quarantine.py`, `review.py`, `sprint1/verdict.py`, `sprint1/phase3/` | REGISTRY, loader-debt cap, health runner, Sprint-1 kill rule (>=4/10 fails), Phase-3 harnesses |
| code | charon/agents/stygian/daemon.py L197-207; executor.py L151-215; loaders/_composition.py; loaders/composition_*.py (29) | the consumer side of the seam |
| code | charon/agents/_base.py L303-305 | swarm host instantiates ErebosAgent by name |
| tests | charon/agents/erebos/tests (39 files + sprint1/ 11); charon/agents/stygian/tests/test_composition_*.py (14) | |
| prose (May) | pivot/erebos_* (43 docs); pivot/sprint1/phase3/*.md (7 verdict docs) | author's own findings, reclassification, doctrine |
| prose (Jun) | charon/CHARON_SESSION_2026-06-03.md; charon/CHARON_SESSION_2026-06-15.md | Phase 3.K verdict; program reset / pause |
| certificates | engine/ledger/AGENT_AUTOPSIES.jsonl (Erebos row, P57 2026-08-21); pivot/COMPONENT_DOSSIERS_2026-06-24.md; pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md row 33; engine/ledger/AUTOPSY_TAXONOMY.md cluster 5; engine/necropolis/QUEUE.jsonl | all reviewed in dossier `death_certificates` |
| second channel | engine/necropolis/dossiers/_keeper_evidence/intelligence_outputs_census_result.json; fleet_halt_census_result.json | Keeper's census of agora.intelligence_outputs (M1), from Atalanta comms #98; DUAL-RECORDED, SINGLE-MECHANISM: rows written by the Erebos daemon itself |
| absent | charon/agents/erebos/{state,artifacts,logs}, charon/agents/{stygian,pollux}/state, charon/agents/_shared_queues/*.jsonl | gitignored; not in this worktree, the main worktree, or the data backup (history census) |

## 2. BUILT / RAN / OBSERVED

BUILT (executed today): 25 generators; 29 composition loaders that register and resolve
daemon-shaped rows for 14/25 plugins; the 11 loaderless plugins are exactly the 11
quarantined by `_quarantine.py`; queue-row keys cover every key the loaders read;
813 tests pass offline (608+1 skip, 59, 146).

RAN (Keeper census + git log): 213 `erebos_tick_complete` rows, all success=true,
2026-05-26 02:32 .. 2026-05-30 11:59 local, 213 distinct cycle_id, every summary
`enqueued=True`, heartbeat online at the last row; 39 commits on the agent dir
2026-05-26..06-03 (ITER numbers in subjects up to 83; ITER-84 named in the 06-03
triplet claim); 19 loader commits 05-26..05-30. Stopped with the fleet: 15 May agents
wrote their last row 11:40-12:25 on 05-30 (stygian 12:03, pollux 11:55, hecate 12:20).

OBSERVED (quoted, not re-measurable -- ledgers gone): ITER-5 tally "7 composition
loaders, 2 PROMOTED, 4 REJECTED at expected kill pattern, 1 UNVERIFIED"; author's
05-27 reclassification of those findings to catalog/substrate tier; Phase 3.K
(06-03): observed=2 deltas vs pair-aware counter, null p95=2, p=0.105, 7-seed mean
0.102, N=699 rows, 200 permutations, seed 1789 -> STATISTICALLY UNDERDETERMINED;
triplet claim observed 1 vs null ~14 -> FALSIFIED. 234 composed_claim artefacts
counted by P57 on 2026-08-21 (vs 213 ticks -- gap recorded, not reconciled).

## 3. Scripts and headline results

| script | one question | headline (from *_result.json) |
|---|---|---|
| erebos_seam_census.py | Does the compose->falsify seam exist and resolve for daemon-shaped rows? | REGISTRY 25; executor force-imports 29 loader modules, 29 register, 0 import failures; find_loader hits 14/25 plugins; 0 loaders == 11 quarantined (exact set match); loader keys missing from daemon rows: []; non-erebos control row resolves: False; both short-circuit strings present |
| erebos_tests_offline.py | Do the tests run and pass today, offline? | erebos 608 passed 1 skipped (1.1s); sprint1 59 passed (0.6s); stygian composition 146 passed (32.2s); 0 network-library imports in the packages grepped |
| erebos_external_refs.py | Does P57's "zero external references" reproduce, and what did its scope exclude? | P57 scope, case-sensitive EREBOS: 3 files, all autopsy/queue ledgers (self-hits) -> reproduces; same scope -i: 14 files; tracked tree -i excluding own dirs: 198 files (charon/agents/stygian 53 incl. 29 loaders; harmonia 19; pivot 37; aporia 34); code importers outside the agent: _base.py, stygian/executor.py, stygian test_phase0_integration.py, harmonia/primitives/test_baseline_costume_parity.py, roles/Polyhymnia tesserae.jsonl |
| erebos_history_census.py `<data-backup-root>` | How long did it run, which ITER, was ITER-100 executed, what did "0 perm-null survivors" measure, where are the artefacts? | 39 commits 05-26..06-03, max ITER in subjects 83; loader commits 19 (05-26..05-30); ITER-100 named 5 times, all as the FUTURE pre-committed kill, never as reached; Phase 3.K numbers quoted (2 vs 2, p 0.105, N_PERM 200, SEED 1789); KILL_RULE_MAX_FAILS=4; runtime paths absent in 3 roots (only `_shared_queues/__init__.py` exists) |
| erebos_null_instrument_calibration.py | Is "observed=2, p=0.105" a property of the data or of the instrument? | committed harness run unchanged on synthetic 699-row ledgers: NULL x3 -> observed 0, null_p95 1, p 1.0; PLANTED strong partner-conditioned linkage x3 -> observed 0/1/0, p 1.0/0.345/1.0, detected 0/3; every run's own verdict STATISTICALLY_UNDERDETERMINED; smallest count clearing p<0.05 = 2-3 |
| scripts/composed_claim_consumer_audit.py (repo script, rerun) | Are ComposedClaim fields consumed downstream? | 16 fields, 14 with consumers, zero-use = information_gain_nats, reuse_value_count (May 28: 4 zero-use; the two cost fields gained consumers since) |

## 4. Hunt log

Hits:
- H1 executor `EREBOS-` branch + 29 forced loader imports (seam census).
- H2 11 zero-loader plugins == 11 quarantined (seam census) -- loader debt was capped by design, not hidden.
- H3 P57's grep reproduces exactly in its own scope (3 self-hits), so the certificate's error is scope, not fabrication (refs A).
- H4 53 Stygian files and 19 Harmonia files name Erebos; Harmonia B (2026-06-15, commit 2905c5659, read) imports `_cross_cell_motif` and the phase3 harnesses -- an external consumer of Erebos CODE (refs B).
- H5 ITER-100 appears only as a future kill; max ITER 84 (history census).
- H6 Pair-aware delta statistic sits at its floor on 699-row ledgers in both NULL and PLANTED worlds (calibration).
- H7 213 ticks, all success, ending at the fleet-halt minute (Keeper census, cited).
- H8 Two cost fields that were zero-use on 05-28 have consumers at baseline (consumer audit rerun).

Misses (looked for, not found):
- M1 Any Stygian-side record of DEQUEUING an Erebos row: `_shared_queues/*.jsonl` absent everywhere; Stygian's agora output_summary rows are not in the Keeper census; no `EREBOS-` problem_id string anywhere outside code, tests and pivot prose (git grep).
- M2 The 234 composed_claim artefacts on any host reachable here (three roots checked).
- M3 The 699-row real ledger behind Phase 3.K (needed to re-execute the triplet FALSIFIED verdict; not re-executed).
- M4 Any Erebos kill condition that fired: Sprint-1 verdict 10/10 PASS is synthetic; ITER-100 unreached.
- M5 Any commit after 2026-06-15 contradicting the pause (git log: last agent-dir commit 06-03).
- M6 A lift-only planted signal in the calibration (not attempted; see D9).
- M7 Any LLM call in the tick path (daemon and generators are rule-based; grep for provider libs: 0).

## 5. Primary observations vs later interpretations

| primary (May/Jun 3) | later reading | dossier review |
|---|---|---|
| ITER-5: 2 PROMOTED / 4 REJECTED / 1 UNVERIFIED via loaders | 06-24: "composition-aware loader never shipped (claims short-circuit as *_pending)" | PARTIALLY_UPHELD: true for the 11 quarantined plugins, false as a general statement (19 loader commits, 29 modules, 14 plugins resolve) |
| Phase 3.K: STATISTICALLY UNDERDETERMINED, p=0.105 | 06-23/24: "realized~0 (0 perm-null survivors)"; QUEUE: "realized value ~0" | PARTIALLY_UPHELD / OVERTURNED: an unresolved test became a zero; the statistic has no resolution at N=699 |
| daemon enqueues to Stygian; loaders exist | P57 (08-21): "seam never built", "ZERO external references", review.py = self-review | OVERTURNED on executed evidence; grep scope excluded charon/agents/stygian and harmonia and was case-sensitive |
| 06-15 reset: "off-spine until it has a consumer" | ROSTER/QUEUE: SELF-CONTAINED-GENERATION, "likely TRUE_CORPSE" | UPHELD for the pause (consumer = organism); OVERTURNED for the class label and the TRUE_CORPSE pre-label |

## 6. Residue: executed vs read

Executed today: 25 generators (REGISTRY import), 29 loaders (import + find_loader), 813
tests, `pair_aware_permutation_null.py` (run on synthetic input), `_quarantine.py`,
`scripts/composed_claim_consumer_audit.py`.
Read only: `_cross_cell_motif.py`, `_kill_tensor.py`, routing (`next_plugin_kp_routed`),
`review.py`, `_mahler_composition_helpers.run_binary_split_permutation_null`,
`sprint1/verdict.py`, the Phase 3.A-K verdict docs, Harmonia B's costume-parity test.
Nothing in `residue` is claimed to reproduce a May result; the May inputs are gone.

## 7. PORTABILITY DEFECTS (not silently resolved)

- D1 Executed-by-whom. LAW N17 says VALID needs EXECUTED evidence. Phase 3.K was executed by the original author in June; I executed the instrument, not the measurement. I went: MEASUREMENT verdict rests on my calibration run (executed) and treats the June numbers as quotes. HYPOTHESIS/DESIGN rest partly on quoted verdicts (ITER-5 tally) -- a stricter reader would mark HYPOTHESIS NOT_EXAMINED, which would change nothing in fair_test (already UNFAIR) but would remove the "H-A exercised" statement.
- D2 "External consumer" boundary. Stygian is a sibling under the same operator (Charon). I counted it as external to Erebos (it is a different agent with its own daemon and ledger) but flagged that a reader who defines external as "outside the Charon swarm" gets Harmonia B (code import) as the only external consumer -- still not zero.
- D3 Two hypotheses under one agent_id (H-A composer, H-B Layer-2 value). The certificates attack H-B; the seam evidence defends H-A. I scoped fair_test to H-B and said so; a reader who scopes to H-A could argue FAIR + not-refuted, which the schema has no classification for except CONSUMER_BLOCKED.
- D4 Three kill conditions on record (Sprint-1 rule; ITER-100; the 06-15 pause). None is Erebos's own firing. I recorded the pause as the death and the other two as unfired.
- D5 CONSUMPTION.jsonl counts design-doc consumption by Aporia as consumption. I did not count it as consumption of Erebos output.
- D6 ROSTER dossier_exists refers to the pivot component dossier, not a Necropolis dossier. Not treated as prior Necropolis work.
- D7 Runtime state absent: EXECUTION is VALID on the Keeper's dual-recorded census plus git activity, not on artefacts. A reader who refuses self-reported rows must mark EXECUTION NOT_EXAMINED; the schema would then forbid the current classification only if fair_test changed (it would not).
- D8 "Underdetermined" vs HYPOTHESIS_FAILURE. I did not let an underdetermined test carry a hypothesis kill; the validator would have accepted either.
- D9 Calibration scope: one planted signal class (partner-conditioned kill pattern). A lift-only class was not tried; the MEASUREMENT finding says "no resolution for this class at N=699", not "no power ever". Left as an unresolved question rather than widened.
- D10 load_bearing semantics when the author self-downgraded (catalog-tier reclassification 05-27). I treated the downgrade as honest and not a failure of any layer; a reader could file it as a HYPOTHESIS observation.
- D11 Name of the failure class: the queue's SELF-CONTAINED-GENERATION vs the seam actually built but under-consumed. I overturned the label; I did not invent a replacement class (schema has none), the stack carries it.
- D12 Classification: NO_FAIR_TEST_ON_RECORD chosen; CONSUMER_BLOCKED (the 06-15 wording) fits the same stack and is recorded in `uncertainty`. I chose the former because the certificates' load-bearing claim is a value measurement that was never fairly made.
- D13 213 ticks vs 234 artefacts: different objects (tick rows vs claim files) and different windows/hosts; recorded, not reconciled, not averaged.
- D14 Script count: five scripts + one repo-script rerun against a brief asking for 2-4. Each answers one question; merging them would hide which result answers which question. Left at six and declared here.
- D15 Keeper census is dual-recorded, single-mechanism (the daemon wrote its own rows). Every EXECUTION number carries that caveat in the dossier text.
- D16 validate.py path scan: on the scratch copy 0/49 paths resolve (scratch is outside a repo). Replicating the scan against the worktree root: 43/49 resolve; the 6 unresolved are the three absent kill_ledger.jsonl paths (that absence is the INSTRUMENTATION finding), this README (cited before it was written; resolves now), and one regex fragment of a longer path.
- D17 ORGANS.jsonl grew 39 -> 72 when validate.py regenerated it on the scratch copy with the Erebos residue present. I did not touch ORGANS.jsonl or COUNTERFACTUAL_HISTORY.jsonl in the worktree (forbidden); the Keeper must regenerate and commit them.

## 8. validate.py output (scratch copy, second run after the forced regeneration)

```
=== Necropolis validate.py ===
schema:   SCHEMA.json OK
roster:   48 agents, 0 duplicate ids
dossiers: 7 files checked
selftest: FAILED-classification rejection FIRED (ok)
organs:   72 organs in ORGANS.jsonl; executed_by_necromancer=true for 13
history:  33 counterfactual rows (mistake -> symptom -> verdict -> corrected cause -> repair -> post-repair); 1 with a repair filed
monsters: 2 files checked; kill_condition-rejection self-test FIRED (ok); repair-without-counterfactual self-test FIRED (ok)

ALL GREEN
```
First run on the fresh scratch copy reported 2 problems, both "STALE ... regenerated by
validate.py -- re-run", i.e. the expected ORGANS/COUNTERFACTUAL regeneration, and 0
errors against erebos.dossier.json. Erebos note line: "stack 4 INVALID / 0 NOT_EXAMINED;
fair_test=UNFAIR; primary=ECOSYSTEM_FAILURE; certificates OVERTURNED,PARTIALLY_UPHELD,
PARTIALLY_UPHELD,PARTIALLY_UPHELD,UPHELD,OVERTURNED,OVERTURNED".
