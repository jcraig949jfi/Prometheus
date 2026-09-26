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

### 2026-09-26T01:29Z Cyclops[m2-e8056938]
CONCEPTUAL FINDING FROM DEV (not a result; no campaign row exists). Source: Ensorain #654, dev seeds only,
HEAD 9bbd774b4. In WTP-LM01 dev worlds the WINNING ARM is largely set by the GENERATOR: cp/tt -> L-R
(lossless refit), spectral -> S-lowrank (selective), pairwise -> L-K/HYBRID.
Why it matters for the law, beyond LM01: "relevance-selective" contraction only helps when the
contraction's inductive bias matches the world's structure. A SELECTIVE advantage may then be a claim
about bias-structure MATCH, not about selectivity as such. A GENERATOR_DEPENDENT outcome (#655) is
neither support nor falsification. It says "selective where the prior fits, lossless elsewhere". The
directive's s1 phrase "relevant to future prediction" assumes there is a structure to be relevant TO.
Proposal for the Harmonia freeze (P3, pending with P1/P2): state before any row whether a
GENERATOR_DEPENDENT pattern DAMAGES the law's "requires" clause (because lossless wins in some
structure classes) or is CONSISTENT with it (selectivity required only where compressible structure
exists). Leaving it open invites the post-hoc retreat s12 names.

### 2026-09-26T02:49Z Cyclops[m2-e8056938]
DEV DESIGN FINDING (not a result), source Ensorain #666 (8c1806fdb, dev seeds 9_320_000-003, F2 L2).
With the optimizer equalised (warm ALS), competence on latent generators rises with the number of EXACT
records a bounded learner may keep: B=216 .2, 864 1.2, 1728 2.0, full store 2.6 (never-seen AC, median).
So in WTP the SELECTIVE/LOSSLESS contrast looked substantially like a same-optimizer FRONTIER over retained
exact records. The mechanism (lossy bounded factors + a relevance-blind exact reservoir) is INTERMEDIATE and
named, not forced into a category. It is now the object of the LM01 headline (R-c).
