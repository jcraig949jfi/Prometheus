# Ensorain status

Currency: 2026-09-25 18:30Z (Foundry charter; WTP-LM01 directive received; M2).

seat state: ACTIVE, DESIGNING WTP-LM01 (Lossless Memorizer Challenge). No runs.
DIRECTION (2026-09-25): major scientific direction now arrives by comms from the SI stewards Cyclops (M2) and Aporia (M1)
  (roles/Ensorain/prompts/2026-09-25_wtp_lm01_directive/). WTP-LM01 supersedes WTP-04.
  - Heartbeat to both stewards every 60-90 min; report defects/falsifiers immediately.
  - NO M2 launch while the Bellerophon coupling campaign runs. Cyclops issues the launch prompt.
  - First response: comms #590 (ACK + objections O1-O6).
  - Rulings R1-R3 RECEIVED (#591/#592/#594): ensorain/lm01/STEWARD_RULINGS.md.
  - Dev envelope: <= 2 workers while ENVGATE-02 runs, IDLE priority, stop at < 6 GB free RAM, sweep log committed.
  - Deliverables before launch: directive s13 (prereg, frozen config, arms + audit tests, accounting spec, calibration
    results, dev resource estimate, falsifier + limitations, runtime proposal, sealed campaign-seed procedure).
CHARTER: Tensor Physics of Intelligence Foundry (roles/Ensorain/prompts/2026-09-24_foundry_directive/).
workspace: worktree D:/Prometheus-worktrees/ensorain-base-role, branch ensorain/base-role-adopt-2026-09-23 (KEEP; only
  Ensorain branch). HEAD is fast-forwarded to main after every commit. Host M2. EW_DB_HOST=192.168.1.202 for comms.

## Campaign line (all complete, all on main)
- WTP-01: verdict REDESIGN (ensorain/ENSORAIN_WTP01_REPORT.md). The top anomalies were a variance-collapse metric artefact.
- WTP-02 (ensorain/ENSORAIN_WTP02_REPORT.md). The sole specimen was a one-float running mean.
  - Frozen scorer: EXPAND.
  - Operator scientific ruling: PARK/REDESIGN (ensorain/WTP02_OPERATOR_RULING.md).
- WTP-03, the substrate collider (ensorain/ENSORAIN_WTP03_REPORT.md; PREREG_WTP03.md; engine ensorain/wtp3/; rows
  runs/wtp03/; main a65d27ced; comms #566).
  - Mechanical verdict: CANDIDATE PHYSICS FOUND -- DEEPEN (9 flags, 4 lineages, full chain).
  - Seat adjudication: all 9 are bounded online matrix/tensor completion. A post-data tuned batch completion (N6,
    n6_check.py) beats every one by 0.2-2.3 AC, so they are KNOWN PHYSICS and a positive control.
  - Admission: 181 of 38,000 (0.48%), 13 lineages, 174 mutants of near-misses.
  - Crossovers: 0 of 12 replicated. Hybrids: none promoted. Conversions: never necessary.
  - Instrument weaknesses W1-W4 (report s3).

## Mid-flight experiments
None. No background jobs, no monitors, no worktree changes uncommitted.

## Open questions for the operator (pre-directive; Q2 and Q4 superseded by WTP-LM01)
1. WTP-03 adjudication: accept "mechanical DEEPEN, specimens = known completion physics (positive control)"? Or rule the
   DEEPEN as scientific DEEPEN?
2. Go / no-go on WTP-04 (report s6), and which of its four fixes are in scope:
   - W4: N6 rung (tuned batch completion of any class) in the ladder;
   - W1: cross-field transfer (a different instance of the same generator family);
   - W2: class-agnostic admission (don't pre-select completion);
   - search on the learning-time / lifetime ratio that decides inhabitability.
3. The WTP-03 world physics changes are declared in PREREG_WTP03 s4:
   - graded prediction market;
   - query market in every world;
   - information-cost scale kappa;
   - energy buffer;
   - replay consolidation;
   - clean-channel stratum.
   Keep them as the Foundry's standard physics, or revert any?
4. Scale: WTP-03 Wave A took ~10 h for 181 worlds / 13 lineages. Is a longer Wave A (more founders) acceptable, or should
   WTP-04 target founder diversity directly (e.g. seeded founders per generator family)?

## Suggested next step (if go)
WTP-04 "beyond completion". Keep the WTP-03 engine and add:
- (a) an N6 rung;
- (b) cross-field transfer (the learned artifact, or the learning law, carried to a new field instance);
- (c) admission by a class-agnostic information-demand test;
- (d) a stratum that searches the learning-time / lifetime and memory / description-length ratios directly.
Promotion requires beating N6 or cross-field transfer. Preregister first; dev seeds 9.1M-9.9M; campaign seeds disjoint.

blockers: operator direction.
