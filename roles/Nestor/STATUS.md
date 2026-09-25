# Nestor status -- Cycle-9 campaign (autonomous loop)

Currency: 2026-09-25 ~07:20 EDT (pre-reboot save). Charter: budgeted autonomous scientific loop
(RESPONSIBILITIES.md section 2). **Resume from `EXPERIMENT_GRAPH.jsonl`**
(`python graph.py open`); the last line per id wins. FINDINGS section E has every promoted
claim (E-6..E-10). Consolidated report:
`campaigns/c9x-explore-2026-09-24/CAMPAIGN_REPORT.md`.

## RESUME AFTER REBOOT (2026-09-25, operator directive `prompts/2026-09-25_reboot_resume/`)

Bootstrap: read RESPONSIBILITIES.md section 0-2, this file, then `python graph.py open`.
Worktree `F:/Prometheus-worktrees/nestor-s1-forensics`, branch `nestor/s1-forensics-2026-09-23`
(merged to main at the reboot save).

1. **X-DONOR-SWAP was mid-flight at the save** (44/96 runs at 07:17; ~15 min remaining). Check
   `campaigns/c9x-explore-2026-09-24/x_donor_swap/run.log` for an `EXIT` line. If absent (the reboot
   killed it), resume: `cd campaigns/c9x-explore-2026-09-24/x_donor_swap && python run_ds.py`
   (it skips finished runs; its per-cell assay rates are recomputed, deterministic). Prefer a
   one-shot schtask (template: any `launch_*.cmd` pattern in STATUS history; task NestorDS exists,
   disabled - `schtasks /Change /TN NestorDS /ENABLE`, `/Run`, then `/DISABLE`).
2. Record its result: graph node X-DONOR-SWAP (declared classification in `run_ds.py`), FINDINGS
   E-10 tail, CAMPAIGN_REPORT section 3 item 5, commit + push.
3. Next branches (charter: SIGNAL -> CONFIRM; null -> localize/targeted/orthogonal):
   - if SIGNAL (competent donor runs away in foreign cells): C-DONOR-SWAP, fresh frozen confirm.
   - if CLEAN_NULL: localize which cell factors block a competent donor (representation, pressure).
   - open question worth a child: 7ae3 copies only from tape side 1 (runs second) - why, and does
     side asymmetry matter in the world?
4. Budget: window ends 2026-09-26 06:47 EDT (48 h from 09-24 06:47), <= 12 workers, 20% reserve.
   Whether the reboot downtime counts against it is an OPEN operator question (below).

### Operator rulings on the reboot questions (2026-09-25 08:16)
- Q1 Budget clock: **extend by the downtime**. Downtime 07:20 -> 08:15 (55 min); window now ends
  **2026-09-26 07:42 EDT**.
- Q2 Housekeeping: **keep** the eight disabled one-shot schtasks; do not delete them.
- X-DONOR-SWAP was killed by the reboot at 66/96 (no EXIT line); resumed 08:15 via NestorDS
  (enable, run, disable).
- FYI (not my lane, not worked around): Harmonia reports test_base_role RED on origin/main
  (Nyx manifest mismatch; Ananke MONITORS row); the merge of this branch does not touch it.

## Budget ledger (seat decision)

| item | value |
|---|---|
| window | 48 wall-h + 55 min reboot downtime (operator Q1), 2026-09-24 06:47 -> **2026-09-26 07:42 EDT** |
| concurrency cap | 12 workers |
| reserve | 20% |
| external spend | none |

## Done

- **C9 inner experiment (frozen 5819bc6d)**: 1,200/1,200 runs, audit PASS. After mining: H1
  INVALID (C9-D16), repaired and rerun as **C9-H1R: COST_INTERACTION_ONLY** (confirmatory). H2:
  weak signal in specimen 7ae3. H3: retired structurally. See
  `campaigns/z80atlas-verify-2026-09-22/observatory/C9_OUTCOME_AND_ADDENDUM.md`.
- **Confirmed (CONFIRM lane):**
  - **C-SELFLOC**: self-location gates non-pair heredity (13/36 vs 0/36).
  - **C-ENERGY**: the depth-1 wall is newborn starvation (20/40 vs 4/40).
  - **C-DENSE**: spontaneous non-pair heredity appears once world-op encodings are 1 byte
    (13/40 vs 0/40).
  - **C-ABLATE**: under dense encodings, self-location and search remain necessary.
  - **C-RUNAWAY**: the recombination splice prevents runaway pair-tape heredity
    (7/150 vs 0/150, p = 0.007).
  - **C-ATOMIC C1**: tape-write erosion stops pair-tape heredity in 7ae3's cell (46/80 vs 1/80); C2 generality NOT confirmed.
  - **C-CORE**: runaway heredity in 7ae3's cell conserves the founder's SELF + LDIR instructions as material, little else (17/27, bar 60%).
  - **C-CRITICAL-MASS**: with the splice off, heredity is establishment-limited (41/80 vs 5/80).
- Not confirmed: C-NORECOMB (threshold endpoint); energy-for-depth arm of C-ABLATE.
- Chain since C-CRITICAL-MASS: X-DOSE-CURVE null (independent founders) -> X-TICKET (copying stops by ~epoch 12) -> X-DECAY (in-place mutation minor) -> X-STALL (members sterile) -> X-STERILE (fertile at birth) -> X-STALL-F0 (tape-write erosion ~25x nominal) -> X-ATOMIC SIGNAL (36/64 vs 3/64 runaways).
- Earlier EXPLORE: X-CRITICAL-MASS WEAK_SIGNAL (4 founders vs 1: runaways 9/64 vs 0/64), confirmed by C-CRITICAL-MASS; X-DOSE-CURVE CLEAN_NULL (founders are independent ~13% tickets, no critical mass).

## Running

| experiment | lane | what |
|---|---|---|
| X-CERT-BREAK | EXPLORE | P-11 certification breaks in runaway lineages: share uncertified by epoch window + failing criterion, 6 replays; schtask NestorCB |
| C3-D (Cosmos #561) | DELEGATION | SEALED + pushed 2026-09-25: commitment ae4479c6...57ac, commit a56ef7787, report 5e05307b2 (branch nestor/c3-holdout-d-2026-09-25); reported to Cosmos #599. Awaiting Cosmos predictions; no outcomes run |

Child experiments live in `campaigns/c9x-explore-2026-09-24/<id>/`. Each is declared, and
committed, before it runs.

## Rules learned this campaign

- Never edit a `.py` in `z80atlas-verify-2026-09-22`: `verify_freeze` would refuse.
- If a job swaps a module, use one job per process (X-DENSE-OPS).
- Identical arms are a defect signature, not a null (C9-D16).
