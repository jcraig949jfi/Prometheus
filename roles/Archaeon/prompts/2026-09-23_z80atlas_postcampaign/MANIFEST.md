# MANIFEST -- 2026-09-23 Z80 x Atlas Post-Campaign

## Active directive
00_OPERATOR_DIRECTIVE.md -- Z80 x Atlas post-campaign repair and targeted
falsification. Four phases: (1) preserve historical evidence + audit receipt,
(2) repair provenance instrumentation + 10 required tests, (3) re-adjudicate
72-hour campaign without re-running it, (4) small pre-registered de-novo
replication experiment.

## Status
READY -- boot and execute. No prior work to resume.

## Key artifacts on main (bcb9f22ad)
  archaeon/z80atlas/campaign/CAMPAIGN_PACKET.md
  archaeon/z80atlas/campaign/PACKET.json
  archaeon/z80atlas/campaign/ATLAS_INDEX.jsonl
  archaeon/z80atlas/campaign/RUNS.jsonl
  archaeon/z80atlas/campaign/GRAMMAR_FROZEN.json
  archaeon/z80atlas/pivot/Z80ATLAS_REVIEW_2026-09-22.md
  archaeon/z80atlas/campaign/runs/<family>/<run_id>/  (per-run artifacts)

## Defect summary (discovered post-campaign)
The transplant verification constructor sets init="random" in the spec but
injects evolved tapes. The spontaneous_replication predicate checks
init=="random" without excluding transplanted ancestry. All 26 flagged runs
are transplant verification runs (0 fresh-seed, 0 primary exploration).
Corrected campaign: 0 verified de-novo spontaneous replication events.

## Grammar digest
63ffdeca16db3333 (frozen; do not change)

## Previous session context
Session 49ee5a4d (2026-09-16 to 2026-09-22), model claude-sonnet-4-6,
worktree D:\Prometheus-worktrees\archaeon-wse-2026-09-16, branch merged.
