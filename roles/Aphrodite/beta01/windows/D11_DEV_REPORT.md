# DEV-11 REPORT (C-006 Beta-01, cycle 11)

Opened 2026-10-05T13:40Z, after TEST-10 closed. Closed 13:50Z with T11 frozen.

## 1. Diagnostic (operator s17: use existing rows before spending compute)
`engine/v2b/d11_derivation_diag.py` (sha256 80168bcb...) re-ran g10 at O4 and O10 for seeds 1, 6, 12 and 13. It
recorded the derived schemas and the full g10 tables (G, L, eligibility). Selections reproduced 8/8.

**Result: T10's hypothesis (non-monotone derivation) is REFUTED.**
- No candidate is lost from O4 to O10.
- In seeds 6, 12 and 13, **MEMORISE** wins at O10. Its validation G rises with the number of observations (to 49k,
  126k and 66k) at near-zero L.
- The donor entries show MEMORISE also wins in T09 (g0 and g10) at seeds 7, 9 and 14, and over the planted G1 in seed
  14.
- MEMORISE never transfers.

Errata were appended to the T09 and T10 reports. Their labels are unchanged.

## 2. The first broken rung
**R3: the selection score admits a non-generalising library.** Its validation savings grow with observation and
reflect exact-program recurrence across natural lineage siblings. They do not reach the PRISTINE-censored transfer
families. Observation breadth (T10) feeds MEMORISE as much as abstraction.

The secondary limit is a validation-to-transfer mismatch between two real abstractions (seed 1).

## 3. One repair (smallest causal)
**g11 = g10 minus MEMORISE in candidacy:** a content-free rule about candidate type. T11 tests it at O4 and O10,
plus the NULL gate. It pre-registers a cumulative comparison against I_0.

The exposure is disclosed: there is no fresh seed supply, so this is the same 15 seeds.

## 4. Pre-freeze controls
- **K1** (seed 3 O4 continuity) PASS.
- **K2** (seed 13 O10 predicted selection (v - {H})) PASS.

## 5. Frozen
beta01/windows/T11_ABS_SPEC.md. Runner t11_absonly.py, sha256 f2b8442e....
