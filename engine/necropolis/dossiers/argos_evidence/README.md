# Argos Necromancer evidence (2026-09-10)

Reproducible scripts + their captured outputs for `../argos.dossier.json`.
Run from repo root: `python engine/necropolis/dossiers/argos_evidence/<script>.py`
(result JSON is written beside the script, or to `$SP` if set). Archaeology only: `argos_selector_test.py` imports
`harmonia.agents.argos.daemon.ArgosAgent` as an INSTRUMENT (parse/score/select only; never `run_tick`; Redis host pinned to
loopback; no DR request enqueued) — LAW N14 apparatus control is the import+instantiate line of its result.

| script | question | result file |
|---|---|---|
| `argos_catalog_authorship.py` | Decoy check on the Aug-2026 autopsy observable: are the "13 catalog files that grew 11->13 then froze" Argos output at all? git first-commit date of every catalog vs Argos's first commit. | `argos_catalog_authorship_result.json` |
| `argos_consumption_trace.py` | Is the June "0 consumption" verdict still true? Trace every BACKCORPUS_MINING row for the 20 Argos reports, the one anti-anchor they sourced (AA-062) and its downstream files. Then "measurement carries its answer": anchor yield vs corpus / same-era base rate, P(>=1 in 20 | base), out-of-mission (archive) rate vs base, and whether the anchor carries any lens vocabulary. | `argos_consumption_trace_result.json` |
| `argos_selector_test.py` | Apparatus control + selector degeneracy: with no persisted state do all problems tie and the pick reduce to `sorted(ids)[0]`? Retrodiction: are the 20 real report problem-ids a subsequence of the alphabetical order of the corpus Argos saw in May 2026 (queue.jsonl absent -> fallback scan of `aporia/*/questions.jsonl`), in bursts of <=3 (dr_daily_cap)? | `argos_selector_result.json` |
| `argos_settle_test.py` | The June dossier's own proposed settle test (Stage-1 claim-miner over the 20 Argos reports; "zero => exhaust"), run with an apparatus control (hand batch6) and a matched same-era non-Argos Pythia sample of 20. | `argos_settle_test_result.json` |

Order matters: the catalog check kills the Aug autopsy's identity; the consumption trace kills the June "0 consumption" line
but shows the consumption is base-rate; the selector test explains the out-of-mission astronomy anomaly the trace surfaced
(sort order, not a lens signal); the settle test shows the June test would have been inert as proposed.
Data inputs: `harmonia/memory/catalogs/*.md`, `harmonia/agents/argos/daemon.py` (HEAD and git `cb6bee203`),
`aporia/docs/deep_research_reports/2026-05-2*/NNNNN_argos_lens_fingerprint_*.md` (20), `engine/queues/BACKCORPUS_MINING.jsonl`
(636 rows), `techne/registry/anti_anchors.jsonl` (72), `aporia/*/questions.jsonl` at `cb6bee203`,
`prometheus_math/substrate_generation/claim_mining/extract_deep_research_claims_v0_1.py`.
