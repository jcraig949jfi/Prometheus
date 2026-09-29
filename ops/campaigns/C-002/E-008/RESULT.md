# E-008 result -- horizon falsifier for rcv_add / rcv_str. CLOSED 2026-09-29.

Decision rule: Aether/AETH-03/PHYSICS_DESIGN_03_2026-09-27.md s1 (committed 39b7f7e85 before any horizon run), unchanged.
Execution: 4 Fabric Tasks (executor `script`, caps python.numpy + compute.cpu.light), claimed by worker.ubu001.sci (ubu001;
Linux 7.0.0-34; Python 3.14.4; NumPy 2.5.3), one at a time, base c49f2ebad4 (the pinned code). No RunPod.

| unit | law / seed | Fabric task | attempt | wall s | peak RSS MB | result_sha256 (16) |
|---|---|---|---|---|---|---|
| T-087 | rcv_add s0 | tsk-f11c5d60cb83 | att-687d71d2c7d8 | 758 | 71 | 7cd7ffee25f7658e |
| T-088 | rcv_add s1 | tsk-e56d9c5fea64 | att-0829e7440973 | 776 | 72 | 24b6c7865acfff5b |
| T-089 | rcv_str s0 | tsk-eea4d3806a84 | att-ff8702dbc04d | 789 | 71 | 571fc5c15532319b |
| T-090 | rcv_str s1 | tsk-55b1b35fab2a | att-60d71c2b533a | 801 | 71 | da582d108bc66a0b |

Verification, per unit:
- The result file came back inside the attempt's changes.patch, and its git blob id equals the patch index.
- The in-file `result_sha256` and `unit_id` equal the unit's stdout line.
- `code_sha256_lf` equals the pinned manifest (Aether/runpod/aether_units/aether_files.json, commit c49f2ebad4) and the
  E-005 pod units for all 10 files.
- 0 locality violations.
Reduction: `python Aether/observatory/aeth03_longhorizon_reduce.py ops/campaigns/C-002/E-008/attempts` -> REDUCTION.json.
Cross-host determinism for THESE units was not checked: the 2026-09-27 pod results were lost, so there is nothing to compare.

| arm (OFF, 32 origins) | max radius +500 / +2,000 / +10,000 | max generation +500 / +10,000 | breached | new max gen after 2,000 | radius >= 5 share +500 / +10,000 | differing at +500 / +10,000 |
|---|---|---|---|---|---|---|
| rcv_add | 16 / 19 / 19 | 18 / 21 | 0 | 18.75% (3/16 per seed, both seeds) | 0.313 / 0.344 | 0.94 / 0.94 |
| rcv_str | 8 / 16 / 19 | 8 / 24 | 0 | 18.75% (3/16 per seed, both seeds) | 0.219 / 0.281 | 0.75 / 0.66 |
| (E-005) rcv | 7 / 7 / 7 | 8 / 13 | 0 | 3.1% | - / 0.031 | 0.69 / 0.62 |
| (E-005) add | 3 / 3 / 5 | 3 / 5 | 0 | 9.4% | - / 0.031 | 0.97 / 0.94 |

**Verdict under the declared rule: HORIZON-DEPENDENT for both rcv_add and rcv_str, through clause (iii) only.**
- (i) does not fire: the radius >= 5 share grows 1.10x (rcv_add) and 1.29x (rcv_str), below the 2x bar.
- (ii) does not fire: no region breaches; the largest radius is 19 of the 28 bar.
- (iii) fires: 6 of 32 origins in each arm set a new maximum generation after tick 2,000, against a 10% bar. The effect
  is identical in every seed (3 of 16), not carried by one seed.

Read at its width:
- These are the first OFF arms in which the horizon matters. Their components (v1, add, rcv OFF) were horizon-robust in
  E-005. Horizon-dependence here means slow continued causal chains inside a bounded region, not escape. Influence stays
  local and sub-ballistic: 19 sites in 10,000 ticks against a possible 10,000.
- rcv_str carries the slower process. Its radius goes from 8 at +500 to 16 at +2,000 and 19 at +10,000; its generation goes
  from 8 to 24. A reading at the assay's ~400-tick horizon understates its reach by more than half.
- rcv_add reaches most of its extent early (16 by +500) and then deepens slowly: 19 at +2,000, flat to +10,000. In seed 0
  alone the radius moves 9 -> 14 between +2,000 and +10,000.
- As a falsifier of "the super-additive effect is a short-horizon transient", the result goes the other way. Differences
  persist (rcv_add 0.94 still differing at +10,000; rcv_str 0.66, the same level as rcv OFF's 0.62) and keep deepening.
  Nothing here weakens the Block D rcv_add positive.
- It does NOT settle rcv_str's Block D status. That verdict rests on the assay's N1 clause at 128 origins, passing by one
  origin (Amendment A1). This instrument asks a different question at 32 origins. rcv_str's Block D reading stays
  UNRESOLVED (Amendment A2 corrects A1 point 4, which said this run would resolve it).
- The declared consequence of horizon-dependence is methodological: for these two laws, conclusions drawn at the assay's
  horizon are lower bounds on reach and depth. This agrees with "adjacency generation is a lower bound on causal depth"
  (ladder 2). What to do with that is part of the physics-search decision, deferred to the next MWO review; TH-007..012
  stay parked.

Fabric notes (MWO-0001 adoption evidence):
- The work ran as Fabric Tasks with no change to Fabric: the script executor, the numpy environment probe and the patch
  capture were enough.
- Output travels as an untracked file inside changes.patch, because the script executor gives a unit no path it can know
  in advance except FABRIC_OUT_DIR, and the frozen unit takes --out on the command line.
- 4 earlier submissions (tsk-6ed598230989, tsk-d3d665f66b7f, tsk-942556352c75, tsk-eecfab9c883a) carried a mistyped
  base SHA. They failed closed at worktree creation and were superseded. That was a principal error, not a Fabric defect.
  An observation for the Fabric backlog: submit does not check that `--base` resolves, so the error surfaces only at claim
  time, after the attempts are spent.
