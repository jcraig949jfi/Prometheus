# RECONCILIATION of the C4 v0.2 reviews (Cosmos; started 2026-10-08)

R-STAT (Ananke) FINAL: 5c0c104ab, verdict REVISE. R-MECH (Bellerophon) FINAL: PENDING (interim 164df3cdd reproduced).
Each row: finding -> v0.3 response -> executable evidence (branch cosmos/c4-v03) -> status. "Repaired" means the
attack no longer succeeds for the stated reason; it is NOT a claim that a reviewer accepts the repair.

## R-STAT
| id | sev | v0.3 response | evidence | status |
|---|---|---|---|---|
| A1 pooled-BA base-rate shortcut | BLOCKING | primary S0-A statistic = mean within-family uplift, equal family weights; within-family sign-flip; v0.3a: no family significantly negative (Holm) + not carried by one family | stats.py; tests/test_c4_stats.py (cheat FAILS 10/10; v0.2 statistic kept as red reference; one-family-carrying control FAILS) | REPAIRED |
| A2 inferential unit | REPAIR | claim stated conditional on the visible families; exact family-level sign-flip reported (floor 2^-F) | stats.family_level_signflip_p | REPAIRED |
| A3 power realism | REPAIR | simulator with logit-normal family accuracy, unequal base rates, boundary-clustered errors | calib_s2.s0a_power_realistic; c4_power_v03a (n160: uplift .20 -> .94 / .66 at family SD .5 / 1.0; cheat 0; carried 0). The run exposed v0.3's own floor rule as over-strict (65% false failures) -> replaced | REPAIRED (numbers in DESIGN v0.3) |
| A4 S2 multiplicity | BLOCKING | one omnibus test per criterion (offset LRT, slope LRT, CMH permutation), Holm FWER .05 | calib_s2; planted universal passes .93, family-specific 0/60. DEFECT found on the way: calibration-LRT on LOFO predictions falsely rejects 30% of universal laws -> replaced by slope LRT | REPAIRED |
| A5 selection leakage | BLOCKING | DISCOVERY / CONFIRMATION / EXTERNAL namespaces; vault: freeze-first, spend-once, ledgered; confirm.py writes labels only into the vault | firewall.py, confirm.py; tests/test_c4_firewall.py | REPAIRED (no confirmation batch generated yet) |
| A6 no law vs not detected | REPAIR | equivalence bound: "absent" only if the 95% upper bound of U < MIN_EFFECT .05 | stats.equivalence_bound + test | REPAIRED |
| A7 Z_A unknown | REPAIR | confirm.py logs every Q draw and its REGISTERED outcome per family | confirm.specs q_draws | REPAIRED (estimator to be added to the S0-C report) |
| A8 Q_A author not blind | NOTE | recorded in exp01.Q and every prereg; Q was written after EXP-01 | prereg/EXP-02 | ACKNOWLEDGED |
| A9 exclusions | REPAIR | worst/best-case BA bounds; Newcombe CI for differential exclusion | stats.exclusion_bounds, newcombe_diff + tests | REPAIRED |
| A10 DELTA/EPS units | NOTE | to be reported in both units in the S0 report | -- | OPEN (report format) |
| A11 concentration rule | NOTE | carried-by-one-family check is on candidate uplift, not on T3 failures | stats.s0a_verdict e_not_carried | REPAIRED |
| A12 B label noise | NOTE | A/B agreement per family reported before scoring (EXP-01 .97-1.0; EXP-02 sediment .83 = power difference) | results/EXP-02_RESULT.md | DONE for discovery |
| A13 headline statistic | NOTE | one headline per gate to be fixed in F-0002 | -- | OPEN |
| A14 single-class families | BLOCKING | >= 10 per class per family or the family is excluded and counted; S0 NOT_REACHED with < 4 informative families | labels.informative_families + test. Independently observed by Cosmos (EXP-01 sediment 30/30) | REPAIRED (rule); per-family boundary-straddling proposals needed for confirmation |
| A15 no effect-size floor | REPAIR | USABLE / MARGINAL / NOT with MIN_EXCESS .10 of chance-to-perfect, fixed a priori | labels.three_way + test (Ananke's J .262 example -> MARGINAL). Independently observed (EXP-02 A/B split) | REPAIRED |
| B1 second new mechanism | REPAIR | cosmos_phase (Kuramoto phase coding) authored under the foreign-author contract; no independence claimed | families/cosmos_phase (selftest 8/8; natural distribution mixed) | REPAIRED |
| B3 quenched wiring | REPAIR | wiring seed sampled per world in every C4 run (rnn, graph, phase) | exp01.sample_world (wseed) | REPAIRED |
| B4 S1 unimplemented / kicks undefined / G1 | BLOCKING | LOCAL SYSID implemented behind LocalProbe; perturbation = per-element RESAMPLE from the stationary marginal (defined for float, int, binary state); sysid_local imports numpy only (does not import system.py, so the probe.Logit import is not inherited) | sysid_local.py; tests/test_c4_sysid_local.py (G1 AST audit, G3, G5, locality) | REPAIRED for S1; contract s2 for the C3 families: OPEN (LocalProbe draws symbols in range; adapters needed for full contract parity) |
| B5 family identification | REPAIR | measured on the LOCAL coordinates: vector .908 (fingerprint), composed L-0003 score .425 (chance .25); raw coordinates enter only through within-family statistics; frozen family-ID bound for the law input before F-0002 | results/B5_FAMILY_ID_EXPLORATORY.txt | PARTIAL (bound not yet frozen) |
| B6 contract asymmetry, N0 | REPAIR | -- | -- | OPEN |
| B7 k in planted seeds | NOTE | LocalProbe seeds derive from knobs only (no k); DelayLine is used only in tests | exp01.run_world | REPAIRED |
| B8 shared P1 null | NOTE | recorded as a shared-null cluster | -- | ACKNOWLEDGED |

## R-MECH (from the interim; final pending)
| id | sev | v0.3 response | evidence | status |
|---|---|---|---|---|
| F1 SYSID restatement | BLOCKING | vocabulary restricted to LOCAL (one controlled step from a stationary state); the REL@q cheat cannot be built (HorizonError) | tests/test_c4_sysid_local.py | REPAIRED BY REDESIGN |
| F2 B reconstructs A | BLOCKING | S3 re-scoped to machinery robustness; shared-failure matrix; actor class declared | cert_b.py; tests/test_c4_cert_b.py | RE-SCOPED |
| F3 S4 arm on remeasurement | REPAIR | arm counts only if the law is LOCAL-only or differs from T4 | DESIGN v0.3 s2 | REPAIRED (text) |
| F4 T3 registers all continuous worlds | REPAIR | per-family REGISTERED rate reported (EXP-02: 30/30, 28/30, 30/30, 30/30) | results/EXP-02_verdict.txt | REPORTED |
| F5 planted continuous family + cheat | REPAIR | planted.Reservoir / RotReservoir; F1 cheat test | tests | REPAIRED |
| F6 exclusions in continuous families | NOTE | A9 machinery | -- | REPAIRED |
