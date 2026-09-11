# Evidence / provenance coverage for the first native trial (RHAD-26, RHAD-31)

Measured 2026-09-11 on rhadamanthus/native-trial-2026-09-11. Columns:
artifact | on tree (git) | first channel (runtime files) | second channel
(agora.intelligence_outputs, M1) | historical number | reproducible today.
"self-report" = written by the organism itself (dual-recorded, single-
mechanism at best; Atalanta #98).

## Pollux

| artifact | tree | first channel | second channel | historical number | reproducible |
|---|---|---|---|---|---|
| charon/agents/pollux/daemon.py (+ _pick_and_advance, _emit_kill_ledger_row) | yes | -- | -- | -- | code executes offline (pollux_evidence/) |
| charon/agents/pollux/state/kill_ledger.jsonl | gitignored | ABSENT on this host and the local data backup | 286 pollux_tick_complete rows, 05-24..05-30, self-report | P69: 286 rows, 9 pairs, distinct=1; patterns 86/39/161 | count: dual-recorded; pattern split: NOT reproducible (first channel lost) |
| Hecate mi_crossgen=0.0034 (P69 cites) | ? (hecate artifacts gitignored) | ABSENT | 561 hecate rows, self-report | 0.0034 | NOT reproducible |
| agora.agent_heartbeats Pollux | -- | -- | "online", last 2026-05-30 11:55 | -- | instrument is write-only (D-24) |

## Erebos

| artifact | tree | first channel | second channel | historical number | reproducible |
|---|---|---|---|---|---|
| charon/agents/erebos/ (daemon, 25 generators, review.py, sprint1/, tests/) | yes | -- | -- | -- | offline tests executable (erebos_evidence/) |
| composed_claim artifacts | gitignored | ABSENT | 213 erebos_tick_complete rows, 05-26..05-30, 212 distinct, enqueued=True on each, self-report | P57: 234 composed claims, zero external references | 234 vs 213: counts of different things or windows; NOT reconciled |
| Stygian / Pollux / Erebos kill_ledgers (Erebos inputs) | gitignored | ABSENT | stygian 563 rows, pollux 286 rows | stygian_recent=166, pollux_recent=95 in summaries (Erebos's view) | input volume dual-recorded; content lost |

## Nous

| artifact | tree | first channel | second channel | historical number | reproducible |
|---|---|---|---|---|---|
| agents/nous/src/*, configs/manifest.yaml, data/priority_triples.json | yes | -- | -- | -- | yes (nous_evidence/) |
| agents/nous/runs/<13 dirs>/responses.jsonl | yes (committed) | present | NONE (0 rows; no heartbeat) | pivot dossier 01 numbers | replayable from committed runs |
| SALVAGE-NOUS 2026-08-20 -> techne/registry/concepts_index.jsonl (fbd94b997) | yes | -- | -- | 95 concepts / 20 fields / 4 mechanisms | build_concepts_index.py executable |
| M4 runtime state (ROSTER machine M4) | -- | not on this host | -- | -- | unknown; shelving has no recorded author/date (D-20) |

## Fleet context (all three)

fleet_halt_census_result.json: fifteen agents last wrote 2026-05-30
11:40..12:25 local; five on 2026-05-24 04:50..05:01. All heartbeats
"online". The certificates under review (June disposition plan, June 24
pivot dossiers, August AGENT_AUTOPSIES rows) postdate the halt by 3 to 12
weeks and were written from first-channel files that no longer exist on
this host.

## Amendments from the Necromancer READMEs (after the three passes landed)

Source: dossiers/<grave>_evidence/README.md, each with executed scripts and
captured result JSON. Rows here are the Keeper's condensation; the README is
primary.

### Pollux (pollux_evidence/README.md section 5, pollux_record_census_result.json)

| artifact | tree | first channel | second channel | historical number | reproducible |
|---|---|---|---|---|---|
| charon/agents/pollux/state/{pair_history.json, settled_pairs.json, candidate_pool_idx.json} | gitignored | ABSENT (three roots) | -- | -- | no |
| charon/agents/pollux/artifacts/scan_*.md (286 claimed) | gitignored | ABSENT | 286 tick rows (self-report) | 286 | count only |
| charon/agents/hecate/artifacts/gradient_archaeology_20260530T162054Z.md (P69 cites) | ABSENT at cited path | ABSENT | -- | mi_crossgen=0.0034 | no |
| charon/agents/stygian/loaders/pollux_survivor.py | NEVER WRITTEN | -- | -- | -- | the consumer never existed (pollux_consumer_trace) |
| charon/agents/pollux/tests | NEVER WRITTEN | -- | -- | -- | -- |
| Mahler data for the 9 pairs (Q4 replay) | yes | -- | -- | -- | replayed on today's data; identity with May's data ASSUMED |
| certificates: 06-23 REVIVE "real signal"; 06-24 RETIRE "tautology"; 08-21 P69 | yes | -- | -- | contradictory; 24 h apart | pollux_record_census: 6 primary observations, 9 interpretations, 2 prescriptions, 2 provenance gaps |

### Erebos (erebos_evidence/README.md sections 1 and 4)

| artifact | tree | first channel | second channel | historical number | reproducible |
|---|---|---|---|---|---|
| charon/agents/erebos/{state,artifacts,logs}; charon/agents/{stygian,pollux}/state; charon/agents/_shared_queues/*.jsonl | gitignored | ABSENT (worktree, main worktree, data backup) | -- | -- | no |
| 699-row real ledger behind Phase 3.K | ABSENT | ABSENT | -- | 2 vs 2, p 0.105, N_PERM 200, SEED 1789 | the triplet FALSIFIED verdict is NOT re-executed; only the instrument was calibrated (null + planted, 699 synthetic rows) |
| Stygian-side DEQUEUE record of any Erebos row | none anywhere (git grep, three roots) | ABSENT | Stygian summaries not in the census | -- | consumption of Erebos OUTPUT unproven either way |
| Harmonia B import of _cross_cell_motif (2905c5659, 2026-06-15) | yes | -- | -- | -- | external consumer of Erebos CODE: verified by read |
| tests: 39 + 11 sprint1 + 14 Stygian composition | yes | -- | -- | -- | 813 pass offline (608+1 skip, 59, 146) |
| git history charon/agents/erebos | yes | -- | -- | 39 commits 05-26..06-03; max ITER 84; ITER-100 never reached | yes (erebos_history_census) |

### Nous (nous_evidence/README.md sections 1-3)

| artifact | tree | first channel | second channel | historical number | reproducible |
|---|---|---|---|---|---|
| agents/nous/runs/* (13 dirs, 12 with data) | COMMITTED | present | none (surface added 05-13, after every run) | 5918 entries, 5727 unique triples | scorer replay 5918/5918 |
| forge ledger (agents/hephaestus/ledger.jsonl, 6661 lines) | yes | -- | -- | 1212 Nous-shaped keys 03-31..04-02 with NO committed Nous record | orphans: uncommitted M4 output or a second producer; NOT resolvable from the tree |
| priority_triples.json (15) | yes | -- | -- | 2 committed / 11 in ledger / 9 attempted 03-31 with no Nous record | the wire's exercise is only in the consumer's ledger |
| cost / token accounting | NEVER LOGGED | -- | -- | -- | -- |
| supersession commit b674a9976 (2026-04-03) | yes | -- | -- | -- | dated; "why it stopped" otherwise unevidenced |
| agents/nous/.env / key files | NOT READ (rule); absent in worktree by listing | -- | -- | -- | -- |

### Coverage summary

Pollux: 0 of 4 first-channel artifacts recoverable; every historical
number except the 286 count is unverifiable. Erebos: code and tests fully
reproducible; the value measurement's inputs (699-row ledger) are gone, so
the only load-bearing historical number cannot be re-executed. Nous: the
best-covered grave (runs committed), but its most consequential residue
(1212 forge orphans) points off the tree to M4.

