# BEL-RD-72 FAILURE BOUNDARIES (conditions under which a supported mechanism stops working; negative evidence)

Each entry: claim | where it holds | where it stops | evidence (receipt). Failure classes use the directive's F list:
inaccessible / improbable / too short / insufficient variation / destructive selection / instrument blindness /
extinction.

## FB1 -- uptake suppresses origination (BEL-48H CL-20; D1, D2)
- Holds: GRID WELL_MIXED budget 256 (BEL-48H, twice), and two NEW substrates (D1): GRID LOCAL PARTIAL budget 256, and
  PAIR_EXECUTION WELL_MIXED budget 320.
- Stops: SOUP; budget 384 (BEL-48H S1).
- Fault line: the BEL-48H account ("imports destroy more replicators than they create", UF2 ratio rule) FAILS as a
  prediction. In S_LOCAL imports create more FUNC than they destroy (R 0.67), yet blocking still raises origination
  (D1-P1 FALSIFIED). Precursor-damage account: D2 (s8), pending.
- Receipts: receipts/D1_analysis.json; D2 pending.

## FB2 -- budget coupling of computation to heredity (BEL-48H M6; Q4)
- Holds: copy-then-compute machines whose overlong copy consumes the step budget (EXHAUSTION), at budget <= 256.
- Stops: budget >= 384 (exhaustion vanishes); compute-first machines (immune).
- Fault line: a SECOND component, I/O DAMAGE (input read after an overlong copy overwrites 0xE0), does NOT vanish with
  budget (to 4,096). "Coupling vanishes when budget exceeds copy cost" is true of exhaustion only.
- Prevalence of each type in evolved populations: not measured.
- Receipt: receipts/Q4_budget_split_summary.json.

## FB3 -- operator-aware reachability as a predictor (A3)
- Holds: tapes one SUB step from FUNC complete 8/9 in unseen worlds (descriptive).
- Stops: as a ranking over a natural harvest. 97% of non-FUNC survivors have no one-step route, so outcomes there are
  background origination; the operator-aware score adds nothing over substitution (0 MOVE-only routes in 600 tapes).
- Class: instrument scope. One-step geometry is blind beyond distance 1.
- Receipt: receipts/A3_stage2_analysis.json.

## FB4 -- composition across a desert (K2, E1b, DP, F1, F2)
- K2: 0 competent replicators across a verified 4-5-step desert, 1,320 worlds, three copy operators. Classes:
  extinction (58% of worlds dead before t500), improbable (one assembly route; used once, non-heritable), too short
  (1,000 ticks). Not inaccessible; not blind.
- E1b: ECHO + INC coexist and never compose (0/150). DP: 0 routes from evolved material.
- F1: a planted composite is NOT maintained (1/14 surviving paid worlds; unpaid 0/20), and founders one step away never
  cross. Class (frozen rule): DESTRUCTIVE SELECTION / INSTABILITY.
- F2: removing half-credit payment does not rescue maintenance (2/20 vs 1/20). Not a payment-structure boundary.
- F3: THE boundary. Maintenance of a 10-critical-byte composite fails at MED mutation (1/20) and holds at LOW (13/20)
  and VLOW (17/20); CAUSALLY_CONFIRMED (p 2.0e-7). Class: destructive variation, an error threshold.
  - Below the threshold, payment is still needed (VLOW 17/20 paid vs 8/20 unpaid).
  - Fault line: minimal capabilities (2-6 critical bytes) sit below the threshold at MED, composites above it. The
    rate that finds the parts destroys the whole.
- XR: one distance-1 crossing (point repair) under paired payment, inherited; n = 1.
- F4: the threshold is REPRODUCED on fresh seeds (12/20 LOW vs 1/20 MED). At LOW, one-step precursors still do not
  cross (1/20 vs 0/20; FUNC at end 4/20). Class: search-maintenance conflict; no single fixed rate does both in 2,000
  ticks.

## FB5 -- lineage-independent persistence (BEL-48H M4; C2, C2R)
- Holds: ECHO regenerates after removal of every carrier (C2-b), faster than its first origin. It needs world material:
  slower after a copier-rich reset (C2R-P1) and slower after near-carrier removal (C2R-P2).
- Stops / limits:
  - shown for the MINIMAL capability only (ECHO);
  - re-acquisition is first appearance, not durable return;
  - a material-free copier population re-invents ECHO by itself in 9/16 worlds;
  - NOT shown for a composite: no composite exists to remove.
- Receipts: receipts/C23_analysis.json, receipts/C2R_analysis.json.

## FB6 -- payment and acquisition in a composite task (E1 / E1b)
- E1 setting (WELL_MIXED, lifespan 80): keeps organisms but NO replicators (0 FUNC from tick 100); stopped and disclosed.
- E1b: the frozen E1-a / E1-b fail over all worlds, because survival dominates (~80% lose replicators by t500 in every
  cell).
- Within established worlds, payment raises ECHO / INC acquisition and retention (descriptive).
- Class: extinction before exploration (for the all-world tests).

## FB7 -- the persistence pilot (process fault line)
A pilot that scores "population alive" selected a setting that kept no replicators. Cheap proxies for a downstream
precondition fail silently; recorded in the calibration ledger.
