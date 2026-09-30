# D004 result -- the frozen D003 analyses, run on Fabric

Artemis, ubu002, 2026-09-30. Plan: PLAN.md (frozen at 5bb4463 before submission). Receipts: RECEIPTS.json.
Outputs: each Task's stdout artifact (fetched to ubu002 /home/jcraig/artemis-d004/artifacts, sha256 re-checked).
Each verdict applies the rule the D003 worker wrote before any output existed. D003 claims were spot-checked
separately: ../D003/DIGEST.md (30/30 verified).

## 1. Science (6 of 6 returned)

| Task | question (D003 thread) | frozen rule outcome | numbers |
|---|---|---|---|
| D004-01 | Do the accessibility rulers (foothold density, d_flat, rho) work on a second substrate? Stdlib proxy (FR-003) | FAIL: criterion 1 (arm ranking) is false, so all three rulers are disqualified on this proxy | XO vs PM: foothold .421 vs .437, d_flat 1.03 vs 1, rho .980 vs .983, all in the wrong direction; discovery .033 vs 0 is right. Foothold density would have passed criterion 2 in XO (K7 CI [.076, .375]), but criterion 1 disqualifies it first. PM has no variance in T (0 discoveries). |
| D004-02 | BEE as "implicit replication with no scalar objective" data (FR-091, XE-07/AL-5) | Q1: the summaries differ (1/100 identical), so the scalar objective is NOT inert. But the origin of self-replication does not depend on it: spontaneous SR 1 vs 1, 0 discordant, same first-SR tick, in both pressures. Q2 CONFIRMS 8/300 vs 0/300 (base vs ldir_off). Q3: 7/800 in all four arms | EXTERNAL fitness-proportional reaches the task 35/100 (INC), 0/100 (COND_ONE). Identical 7/800 across OFF/ON/SHUFFLED/YOKED means coupling cannot act at origin in B-rand. |
| D004-04 | Proteus v0.5 mutation-kernel current: minimum detectable current, and does it bias selection? (FR-116) | A: MDC = 1e-4 flux units (injected currents fully recovered at 1e-4, 75% of reps at 3e-5, ~0 at 1e-5). That is below the 1.44e-3 residual-current scale, so the instrument CAN certify profiles at that level. B: INDETERMINATE | Max delta_L = .004 instructions (slope -0.01). Consequential needs >= 1 instruction, so the bias is far below consequential, but above noise at some slopes. Equilibrium statement, not campaign horizon. |
| D004-05 | Archaeon attribution TH-014 harness-leak coverage (FR-031) | G1 TRUE: every transplant/inflow leaky variant is rejected. G2: the residual hole is CONFIRMED -- a mis-logged leak is ACCEPTED with no violations for via = provenance_log, by_construction and taint | The worker's pytest step was not run (not part of the script). |
| D004-09 | Ensorain: does learning-time/lifetime predict learning pays? (FR-081) | UNDECIDED: 0/181 admitted worlds have lifetime <= 600, so this data cannot see the ratio | Every proxy's AUC CI contains .5 (lifetime .53, lr .48, updates/step .53, info gap .46), which would read as REFUTE, but the instrument-blindness clause takes precedence. A new experiment is needed. |
| D004-10 | program_ecology: 20 untested mechanism x substrate cells (FR-121) | (1) TRUE: the V1-C snapshot is exactly the V0 81-finding curation. (2) TRUE: public scores = mech_tot x sub_tot. (3) TRUE: CUSTODY DEFECT, see s2. (4) 11 empty PE cells vs null mean 6.9, P = .008 overall, but no single cell has P(empty) < .05, so no individual gap is statistically surprising | |

## 2. Custody defect (D004-10 check 3)

evidence_wiki/benchmarks/gap_prospective_v1.json seals which slate-generation method produced which slate
("methods_sealed_until_adjudication"). D004-10 shows the published slate scores and their order identify the
sealed method from committed public data alone: gap_slates_v1c.py:52 defines it by weight. No sealed
artifact was opened. This file deliberately does not restate the mapping. Routed to Harmonia (evidence-system
audit) and Aporia; Mnemosyne, the owner, is parked.

## 3. Fabric

6/6 completed on the first attempt, 0 timeouts (walls 0-40 min; D004-04 took 40 min on worker.ubu001.sci).
Changes from D002: line-buffered stdout in run_frozen.py (F1 mitigated on the client side), max-attempts 1
(F2 avoided), rootcopy mode used by D004-10. Numpy routing was correct again.
