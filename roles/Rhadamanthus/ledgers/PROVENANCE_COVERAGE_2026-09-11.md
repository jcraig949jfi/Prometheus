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

(Per-grave rows are amended from the Necromancer READMEs when they land.)
