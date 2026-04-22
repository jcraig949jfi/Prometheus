# Literature Diff Cadence Runbook

**Purpose:** Turn gen_07 from a one-shot into a scheduled cadence.
**Owner:** Harmonia conductor (any session).
**Cadence target:** weekly batch pull + diff.

## Weekly procedure

1. Pull latest paper batch from Aporia stream (or S2 API directly) since last run timestamp. Store at `aporia/data/literature_scan_<yyyymmdd>.json`.
2. Run `PYTHONPATH=. python harmonia/runners/gen_07_literature_diff.py`.
3. Script produces:
   - `harmonia/memory/literature_diff_entries.json` (machine-readable, overwrite-on-run)
   - Append-only entries to `harmonia/memory/literature_diff_log.md`
   - Append-only entries to `harmonia/memory/calibration_anchors_from_lit.md`
4. Conductor reviews top-priority entries manually (CANDIDATE_NEW_F_ID, DIVERGENCE_*, RETRACTION_CROSS_CHECK).
5. For each reviewed item: either promote to Agora task, retract the classification, or log as noted.
6. Commit.

## Entry-to-task promotion rules

| Classification | Promotion condition | Priority |
|---|---|---|
| REPRODUCTION | Auto-log; no task | — |
| DIVERGENCE_NUMERICAL | Paper claim extracted + human-verified | -1.5 |
| DIVERGENCE_STRUCTURAL | Claim-class mismatch confirmed by conductor | -1.0 |
| RETRACTION_CROSS_CHECK | Always, but bundled per F-ID | -1.0 |
| KILL_REINFORCEMENT_CANDIDATE | Feed into gen_05 candidate pool; don't double-seed | — |
| CANDIDATE_NEW_F_ID | Conductor approves F-ID registration | -0.5 |

## PROBLEM_TO_FIDS map maintenance

The diff executor uses a static `PROBLEM_TO_FIDS` map. As new F-IDs land, this map must be extended. Check: `git log --follow harmonia/runners/gen_07_literature_diff.py` for history; bump when F-ID roster changes.

## Epistemic limits

- Semantic matching is lossy. A paper about "the 42% CFKRS-excised deficit" may be the same finding as F011's "~38% residual" under different framing — the matcher can miss this. Human review required for anything tensor-mutating.
- Paraphrase drift: TL;DRs are S2 summaries, not author text. Cite abstracts verbatim in the diff log when promoting.
- Pattern 30 gate: before registering a new F-ID from literature, run the algebraic-coupling diagnostic on the paper's claim.

## Version

- **v1.0** — 2026-04-20 — initial cadence under generator pipeline v1.0.
