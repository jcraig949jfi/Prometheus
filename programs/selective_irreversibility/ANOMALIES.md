# Counterexamples and anomalies

Part of programs/selective_irreversibility/ (README.md: writing rules,
directive path + hash). Append-only.

Surfaced IMMEDIATELY (s13.12): post to both stewards on comms at the same
time as the entry. Each entry: what was observed, the rows beneath it, the
accounting boundary, and why it might NOT be a counterexample (a boundary
leak, externalised history, an unpriced resource: s2, s9).

---

### 2026-09-25T16:30Z Aporia[m1-cb5a6069]
File created (skeleton). No entries yet.

### 2026-09-25T23:45Z Aporia[m1-cb5a6069]
CANDIDATE INSTRUMENT DEFECT in PTE-C1 evidence (Ananke #639, D-A). Surfaced per s13.12. C1
labels are NOT changed (PTE-SI01 directive s0). C1b adjudicates.
  D-A  C1's packet_ablation drops arrivals over range(t0, ro_tick). The readout tick's own
       delivery is never dropped (assays.control_battery end == envs ro_tick; engine._tick
       orders delivery -> sense -> run -> emit -> trace within one tick). A cue emitted at t0
       with delay == delta escapes the ablation. Aporia independently re-derived the mechanism
       from code (#640): CONFIRMED in code; FAMILY-GENERAL (HOLD included). NOT verified: the
       M3 cells' delay == delta == 4 (C1b H-M3-0 settles it).
       Effect: it can only produce a false NOT_SUPPORTED, never a false SUPPORT. If confirmed,
       C1's M3 ("self-modifying, timing-locked MAJ") may be ordinary timing-locked transport.
  D-B  C1's memory ablation reset only S. The inbox, Kp and w were untouched, so M2's "held
       bit not in any site" is under-identified. PTE-SI01 attack A depends on M2, so C1b's
       per-carrier resets are a PREREQUISITE to SI01.
  D-C  M3 cells have WIMM 0 and mut_site 0, so those directive arms are NOT_APPLICABLE by
       physics.
Why the program cares: PTE is the program's clean externalized-memory case. A mechanism that
turns out to be an instrument artifact must not enter SI01 as a specimen.
