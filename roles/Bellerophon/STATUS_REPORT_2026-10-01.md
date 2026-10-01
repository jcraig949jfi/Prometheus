# Bellerophon -- status report 2026-10-01 ~06:35Z (M2 / SPECTREX5; model claude-opus-5-5)

Work orders: MWO-0004 (blob 925660b2, unchanged) + CWO-2026-09-30C (finish / surface / dispatch).
State: **WORKING, gated.** The only in-flight item is the C4 R-MECH review (Aporia #1138). Nothing else is running:
no workers, no leases, no GPU, $0 spend.

## 1. Status / ETA

| item | state | ETA |
|---|---|---|
| C4 R-MECH review (Cosmos C4 DESIGN v0.2) | Phase 1 INTERIM delivered (164df3cdd, branch bellerophon/c4-rmech-2026-09-30; posted to Cosmos #1158). The FINAL is gated. | **Bellerophon's part: ~1.5-3 h after the gate opens.** The gate itself has no ETA (see below) |
| Gate condition (1): foreign visible family committed | NOT MET. prometheus/cosmos/c4/families/ does not exist on origin/main. No Cosmos commit since ~2026-09-30T18:00Z | owned by the foreign-family author / Cosmos; unknown |
| Gate condition (2): C3 substrate code published | NOT MET. roles/Cosmos/c3/PUBLICATION_PLAN.md has V1-V5 pre-checked PASS, but publication is triggered only AFTER (1) | follows (1) |
| Completion | then the s11 completion message to Aporia and READY | same day as the gate |

What the remaining 1.5-3 h covers:
- **PART B, implementation diversity (I1-I5),** on the 4+ real families. This includes my own brief item 1b (does a
  delay-invariant coordinate encode family?), executed on the real families.
- **Re-running the F1-F4 attacks on the real families.** They were shown on a planted continuous family; the real
  families decide whether the findings are general.
- **The final verdict** (PROCEED_TO_F-0002 / REVISE / NOT_WORTH_BUILDING), committed under roles/Cosmos/c4/reviews/.

## 2. C4 interim findings (no verdict; executed, reproducible in ~2 min)

| id | gate | severity | finding |
|---|---|---|---|
| F1 | S1 | BLOCKING | A guard-compliant SYSID coordinate (probe reliability over H = 1..16; passes G1-G5, k-invariant) lets a ZERO-parameter law read it at q = k+1. That law restates Certificate A: BA .91, against .50 for T3-DOWN |
| F2 | S3 | BLOCKING | Certificate B reconstructs A's causal contrast: agreement 47/48 determinate rows |
| F3 | S4 | REPAIR | do(noise .05 -> .80) flips A FUNCTIONAL -> NONE while T3-DOWN stays REGISTERED, and the F1 law predicts it, so S4 credits a remeasurement |
| F4 | S0 | REPAIR | T3-DOWN registers 60/60 continuous world-k rows (exact-zero distances), so S0-A is the whole distribution for continuous families |
| F5 | s8 | REPAIR | The planted suite has no continuous family and no restatement cheat |
| F6 | S0 | NOTE | 12/60 rows are excluded (INDETERMINATE / INCOHERENT) |

## 3. Closed since 2026-09-30 (all on main)

- **E-BEL-REPL-01** (independent BEE rebuild of Nestor's C-A3-INTERNALIZE):
  * Verdict: DISAPPEARS (K3), frozen. The descent component is UNRESOLVED in BEE.
  * Two adversarial merge reviews (MERGE_WITH_FIXES) led to ERRATA_REPL01: overclaims withdrawn, and the blinding was
    disclosed as honour-system only. Merged c776cea6a.
  * The NPE claim is not killed: Nestor's X-MAT is ENDOGENOUS 8/8.
- **E-BEL-REPL-02** (adversarial transformations of the residue):
  * Verdict: RESIDUE_NOT_REPLICATED (ABSENT), frozen.
  * Caveat: the dominance readout was never shown reachable.
  * Post-hoc: REPL-01's K1 signal was mostly TRANSIENT appearance (state-free present at tick 2000: P90 8/100, P75 17/100,
    ZERO 4/100). Result 64d8d2d3f.
- **E-003 BEE leg:** Harmonia's audit was CONFIRMED. The confirmatory label is ALTERED under the pre-exposure rules, and
  the verdict of record is with the OPERATOR (ERRATA_2026-09-30, comms #1050).

## 4. Open items (none blocking the in-flight review)

| id | item | owner / next |
|---|---|---|
| E003-BEE-LABEL | ALTERED vs VALIDATED-as-amended | operator decision (CWO s4) |
| DEF-BEL-008 | BEE glineage is a resemblance label (label-as-content) | confirmed; fix if assigned (CWO-C: no scope growth) |
| DEF-BEL-009 | transplant slots take 0 world-RNG draws, so transplant-vs-control same-seed runs are not CRN-paired (REPL-01/02 unaffected) | confirmed; fix if assigned |
| DEF-BEL-010 | geometry `replicates` inflated by zero padding (ENDOGENOUS_PARTIAL need = 1) | confirmed candidate; fix if assigned |
| E-BEL-BUILD-01 | generalise BEE controls into BUILDER-EXPERIMENT | NOT started (CWO-B/C: no automatic promotion); for Aporia |

## 5. Calibration lessons recorded (calibration/LEDGER.md)

- Exposure is a property of the DATA. Any seat's dry run on the same deterministic data counts as exposure.
- A blind lane must not merge main after an embargo starts.
- Every kill test needs a real-data planted positive that shows it can return SURVIVES. A post-hoc diagnostic may narrow a
  kill, never upgrade it.
- Land state files from a main-based commit, never by pushing a work branch's head.

## 6. Resources

- Today (2026-09-30 UTC): ~19.1 core-h, inside MWO-0004 R2 (<= 48 per day).
- The C4 review used ~0.05 core-h.
- Leases: lse-ede8c1ed2167 RELEASED; lse-4e19412ded95 expired on TTL (token lost; reported to Aporia #1077).
- Heartbeats to Aporia go out hourly while gated (last #1231).
