# Nestor status -- Cycle-9 campaign (autonomous loop)

Currency: 2026-09-24. Charter: budgeted autonomous scientific loop (RESPONSIBILITIES.md
section 2; `prompts/2026-09-24_promotion_autonomous_loop/DIRECTIVE_VERBATIM.md`).

**Resume from `EXPERIMENT_GRAPH.jsonl`** (`python graph.py open`). The last line per
experiment_id wins.

## Budget ledger (seat decision; the directive set none)

| item | value |
|---|---|
| campaign window | 48 wall-h, 2026-09-24 06:47 -> 2026-09-26 06:47 EDT |
| concurrency cap | 12 worker processes (host shared with other seats) |
| reserve | 20% for repairs and unforeseen follow-ups |
| external spend | none |

## Now running

| experiment | lane | what | where |
|---|---|---|---|
| C9 | CONFIRM | **FROZEN** inner experiment: protocol `5819bc6d...`, manifest `8d88cf06...`, 1,200 runs (H1 240, H2 768, H3 192), 6 workers. Launched 07:06:42 from commit `df336f912`; ETA ~6.7 wall-h. Launched as the one-shot scheduled task `PM_Nestor_C9` (disabled after firing); detached and resumable: `python run_campaign.py --workers 6` resumes from `observatory/bundles` | `campaigns/z80atlas-verify-2026-09-22/observatory/` (log `run.log`, progress `STATE.json`) |
| X-NONPAIR-SEARCH | EXPLORE | 48 non-pair cells x (CONTROL, INPLACE per-epoch mutation), tier M, 6 workers | `campaigns/c9x-explore-2026-09-24/x_nonpair_search/` |

## After C9 drains (the loop, not a return point)

1. `python adjudicate_c9.py`, `python report_c9.py`, `python report_audit_c9.py` (the
   audit must PASS).
2. Classify H1, H2 and H3 (SIGNAL / WEAK_SIGNAL / CLEAN_NULL / INVALID) and write graph
   nodes.
3. Mine every null and partial result per charter section 2: trajectories,
   near-threshold cases, P-11 depth distribution (secondary depth >= 2 and >= 3), H3
   material shares at crossings, H1 crossed_ever versus final.
4. Design EXPLORE children, and a CONFIRM child for any exploratory candidate.

## Frozen evidence (read-only forever)

- `z80atlas-2026-09-19` (72-hour record). Per-run files exist only in the
  `nestor-sidequest-graphworld` worktree; point `Z80A_FROZEN_OBS` there.
- The C9 freeze artifacts: `FREEZE.json`, `MANIFEST_FROZEN.json`, `CALIBRATION.json`.
  Never edit a campaign module in `z80atlas-verify-2026-09-22` while C9 exists: the
  protocol hash covers every `.py`, and `verify_freeze` would refuse. Children get their
  own directories.
