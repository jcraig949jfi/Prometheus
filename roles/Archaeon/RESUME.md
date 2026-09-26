# Archaeon -- RESUME HERE (written 2026-09-25T10:48Z, session m2-db608f52, before operator reboot)

On bootstrap read, in order:
1. THIS file.
2. `roles/Archaeon/ENGINE_LANDSCAPE_2026-09-25.md` -- the engine table + distinctness verdict. Operator will
   review it and DECIDE; that decision is the first thing to take.
3. `roles/Archaeon/TODO.md` (2026-09-25 section: Azure E8s v5, commit-aware admission gate, RunPod probe, PEW gap).
4. `roles/Archaeon/journal/2026-09-23_m2-db608f52.md` (full session history 09-23 .. 09-25).

## UPDATE 2026-09-26 (session m2-1034e815): ENVGATE-02 CLOSED -- WINDOW_NOT_SUPPORTED, sequence STOPPED
24/24 blocks complete 2026-09-26T02:50:06Z. Frozen analysis run on the operator's "Do phase C". The Phase-C gate FAILED on
condition 6 (P2 0+/2-, P3 1+/0-). Blocking replicates (U 24 vs BAND0 5); the window rescue fails (RRIGHT 3 / RWEAK 2 /
R128 5). Record: archaeon/envgate2/VERDICT_2026-09-26.md (branch commit c5ba19571). Rows are off-repo at
C:/Prometheus-data/evidence/envgate02_2026-09-26/. The audit and RIE-01 are NOT started. Next = the operator's call
(ENVGATE-03 prereg? lens portability, directive f0dd0599 s6?). Nothing running.

## UPDATE 2026-09-25T18:30Z (session m2-1034e815): ENVGATE-02 RUNNING
Hold lifted by operator directive roles/Cyclops/prompts/2026-09-25_selective_irreversibility/01_OPERATOR_DIRECTIVE_verbatim.md
(sha256 f0dd0599..., s6: "Archaeon -- ENVGATE-02. Run the frozen experiment unchanged"; it also frames Archaeon as an
assay/attribution LENS, not another Z80 world -- lens extraction only AFTER the frozen sequence). Relayed by Cyclops #585.
Launched 18:30:33Z, pid 8244, 6 workers, from pinned worktree D:\Prometheus-worktrees\archaeon-envgate2-run-2026-09-25
(detached at f3b530624). Receipt comms #593. Progress = that worktree's archaeon/envgate2/OPS_LOG.jsonl + runs/.
If not running after a reboot: re-run `python -m archaeon.envgate2.launch_ops` in THAT worktree (resumes, skips done blocks).
Bellerophon's coupling campaign co-runs (20 workers); it records the overlap.

## State at shutdown: NOTHING RUNNING. All science ON HOLD by operator instruction.
Operator (2026-09-25): "Don't change anything as of yet, don't continue any experments." Do NOT relaunch anything
until the operator decides on the engine-landscape discussion AND gives a go.

## Research left-off point (the scientific sequence, frozen)
Governing ruling: `roles/Archaeon/prompts/2026-09-24_envgate_adjudication_rie/01_OPERATOR_RULING_RESUME.md`
("preserve the experiment; reduce concurrency"; one heavy Archaeon job at a time on M2).

| step | item | state |
|---|---|---|
| done | Z80xAtlas post-campaign repair + rulings 1-4 (moat ledger, copier census, evidence bundle, sampler fix) | COMPLETE (memory: project_archaeon_z80atlas_postcampaign_20260923) |
| done | ENVGATE-01 (`archaeon/envgate/`) frozen GATING_CAUSALLY_SUPPORTED, adjudicated GATING_PARTIALLY_SUPPORTED; mechanism = input window 120..131, host-mediated reproduction | COMPLETE (ADJUDICATION_ADDENDUM_2026-09-24.md, ENVGATE01_REVIEW_2026-09-24.md) |
| done | Phase A genetic attribution (`archaeon/lineage/`: taint_vm.py, core.py) | COMPLETE -- operator ruled done; 12/12 tests pass (slow suite re-run 2026-09-25: 12 passed in 57 min) |
| **NEXT** | ENVGATE-02 (`archaeon/envgate2/`), prereg commit 1475b7995 (digest 9e3fb887a4aeaa84), 24 blocks x 5 arms | ON HOLD. `runs/` EMPTY (0/24 blocks). First launch reaped for memory (OPERATIONAL_INCIDENT_2026-09-24.md). Relaunch = `python -m archaeon.envgate2.launch_ops` (6 workers, memory-gated, resumes). Was NOT launched: commit headroom only 1.42 GB (44.5/45.9 GB) at last check -- check `commit_avail_gb` first; after reboot it should be free. |
| then | evaluate frozen Phase-C gate (archaeon/envgate2/analyze.py) | if FAIL: stop and report |
| then | historical genetic audit of 21 ENVGATE-01 worlds (`archaeon/lineage/audit_envgate01.py`), <= 3 workers | not run |
| then | RIE-01 preflight (`archaeon/rie/preflight.py`) then RIE-01 (<= 6 workers) | staged, unfrozen, unlaunched |

Never run two of these concurrently. Never terminate other seats' processes.

## Open discussion (operator decides after reset)
- Is Archaeon's build its own engine? My assessment: NOT as a world (third independent Z80xAtlas build, alongside
  NPE and BEE); YES as a method (environment-as-variable + byte-level genetic attribution + paired sham assays).
  Proposal: make the lens portable across the three Z80 implementations. See ENGINE_LANDSCAPE section 2.
- Atlas does not index z80atlas/census/envgate*; proposed varied=/observed= lens field for a cross-engine standard.
- Compute placement (Azure E8s v5 via GitHub Actions) -- TODO.md.

## Where things live
- Branch: archaeon/z80atlas-postcampaign-2026-09-23 (merged to main 2026-09-25); worktree
  D:\Prometheus-worktrees\archaeon-postcampaign-2026-09-23.
- Evidence (off-repo, read-only): C:\Prometheus-data\evidence\z80atlas_campaign_2026-09-19\, C:\Prometheus-data\evidence\envgate01_2026-09-24\.
- OFF_MACHINE_COPY_BLOCKED stands (no M1 probing; no invented credentials).
