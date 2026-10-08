# PTE-C3R preregistration: FLIP representation factorial

Status: FROZEN at the commit that adds this file, PLAN_C3R_S1.json and FREEZE_C3R.json, before any C3R production row.
The stage-2 plan is generated from the same rules when stage 1 completes. It is the same 192 trajectories (or the
M32 subset in s4), and it is fixed here.

**Authority:** the 72h order (roles/Ananke/prompts/2026-10-07_72h_c3_c4_c5/, 8c48ebfdf), s4 and s5.

## 1. Question

Is FLIP inaccessible because the current representation makes a two-stage computation combinatorially unreachable?

**Fixed:**
- the 4 admitted FLIP cells (physics and env from PLAN_C2C.json);
- the frozen FLIP ruler: B lo99 > .75, reading3 TRUE, margin 2.605;
- the held discipline: 128 worlds, H(search_seed, HELD_NS), fresh C3R seeds;
- the C2 GA settings: pop 96, elite 4, trunc .25, p_field .04, p_instr .15, p_swap .10, p_cross .30, M_final 16;
- shaping (.10, .02) and the selector, both set by C3S (s4).

## 2. Representation-v2 (c3r_common.py)

The engine is NOT modified. The golden_v1 digests still pass (test_c3r).

| arm | prog_len | state registers | free lines at gen 0 | operator |
|---|---|---|---|---|
| R0 CURRENT | 16 | 2 | 0 | OP0 |
| R1 CAPACITY | 24 | 2 | 8 (NOP) | OP0 |
| R2 PERSISTENT | 16 | 3 | 0 | OP0 |
| R5 CAP+PERS | 24 | 3 | 8 | OP0 |
| R3 DUPLICATE | 24 | 2 | 8 | OPD |
| R4 COMPOSED | 24 | 3 | 8 | OPD |

- **Persistent state.** All four cells have decay_shift 0, so the added register S2 is exactly one generic
  non-decaying register. It is unnamed, starts at 0, is bound to nothing, and is reached only through the ordinary
  dst/a/b fields.
- **OPD (duplication and divergence).** It is content-blind. After crossover, with probability .25, it copies a block
  of b ~ U{2..6} lines from a uniform source to a uniformly chosen fully-free (all-NOP) destination; if no such
  destination exists, the destination is uniform and overwrites. The ordinary OP0 mutation follows. Copied lines
  carry a DUP-ORIGIN mark.
- **Conditional-state opcode: not implemented.** The audit found SEL (conditional assignment) and MULQ/XOR (gating)
  already present, and P_FLIP is written with them. A new op would be task-semantic.
- **Admissibility (rep_admission.json, 24/24 admissible).** The re-encoded P_FLIP (by register name, NOP-padded,
  canonical) must have the same ruler status as R0 and |ΔB| ≤ .02 on 128 fresh REP_QUAL worlds.
  - 20/24 are byte-identical in behaviour.
  - The 4 that are not are FLIP-0004 at prog_len 24. Its mut_site .001 site mutation indexes program lines mod
    prog_len, so capacity changes the in-world mutation targets: B .877 against .881, both INDETERMINATE (R0's
    status there too). This is recorded as a confound of the capacity arms at FLIP-0004.

## 3. Seeds and pairing

- search_seed = H(C3_NS, 0x3E9, cell_key, idx) for idx 0..7. Arms with the same genome spec share the gen-0
  population and training worlds:
  - R1 and R3 share one;
  - R4 and R5 share one;
  - the duplication contrasts R3 vs R1 and R4 vs R5 are therefore exactly paired.
- Searches: 32 per arm (8 per cell). 192 trajectories in total.

## 4. Staged budget and selector

- **Stage 1:** every trajectory runs to generation 36 (1x). Its full GA state is saved, including the numpy
  bit-generator state; test_c3r proves continuation equals a straight run.
- **Stage 2:** the SAME trajectories continue to generation 144 (4x).
- **Checkpoint champions:** at 36, 72, 108 and 144, using C2B's rule, and scored on the held worlds.
- **Order:** rounds by idx, cells interleaved, arms R4, R3, R1, R2, R5, R0. A wall therefore censors the highest
  idx of every arm, and R0 first.
- **Selector:** if C3S issued SELECTOR_RESOLUTION_EFFECT, every arm uses M32 and stage 2 is limited to R4, R3 and R0.
  Otherwise every arm uses M8 and all six arms go to stage 2.
  - **Outcome:** C3S issued SELECTOR_RESOLUTION_EFFECT (M effect +.55, sign p 1e-7, boot95 .35-.74;
    REDUCE_C3S.json). So C3R uses M32 in every arm, and stage 2 continues R4, R3 and R0 only.
- **Measured cost (C3S production):** M32 costs about 1.1-1.3x M8 per job, not the 2.3x first assumed (the GPU
  batches the extra worlds). Projection: stage 1 about 8 h, stage 2 about 12 h.
- **Deadlines:** stage 1 at launch + 10 h; stage 2 at its launch + 14 h. No job starts after its deadline.

## 5. Frozen interpretation (reduce_c3r.py, verbatim)

**Competent:** a checkpoint champion reads TRUE on held. Cumulative k_b = searches competent at any checkpoint ≤ b.

**Material(x vs y, b):** computed on the (cell, idx) present in both arms. It requires x ≥ 4, successes in ≥ 2
cells, and x − y ≥ 4. The budget b is 4x when both arms have ≥ 16 searches there, otherwise 1x.

**Labels:**

| label | rule |
|---|---|
| CAPACITY_OPENS | Material(R1 vs R0) |
| PERSISTENT_STATE_OPENS | Material(R2 vs R0) or Material(R5 vs R1) |
| DUPLICATION_OPENS | Material(R3 vs R1) or Material(R4 vs R5) |
| COMBINATION_REQUIRED | Material(R4 vs R0) with no single-factor contrast material |
| REPRESENTATION_OPENS | issued alongside any of the above |
| MIXED | more than one specific label |
| SPARSE_EXCEPTION | no material contrast, but some non-R0 competent search |
| NO_REPRESENTATION_EFFECT | none of the above |

**Kill criterion (order s5).** MINIMAL_REPRESENTATION_ROUTE_FAILED if both hold:
- R3 and R4 each have ≤ 1 competent by 4x (n ≥ 24 each);
- no arm R1-R5 has a per-cell median champion held B at 4x exceeding R0's by ≥ .05 in ≥ 2 cells.

**Exclusions** (flagged, never counted): PLANT_FALSE and OVERLAP.

## 6. Causal assays for every competent candidate (order s5; run after production, before interpretation)

For each competent champion:
1. Fresh held worlds: a new namespace, 256 worlds, re-scored.
2. Lineage and provenance: the full trajectory, saved populations, and dup marks.
3. Carrier localization: swap_v2 on S0, S1, S2 (if present) and payload, at mid-trial offsets.
4. Ablation of the new feature:
   - S2 held at 0 every tick (R2/R4/R5);
   - DUP-ORIGIN lines set to NOP (R3/R4);
   - the extra lines 16..23 set to NOP (R1/R3/R4/R5).
5. A swap of the candidate mapping carrier between mirror twins.
6. Old-physics controls: zero_comm, and teacher_off (the teacher removed after trial 0).

A competent candidate that does not causally depend on the representation change (its competence survives that
change's ablation) does not support the representation hypothesis. It is reported as a representation-independent
discovery.

## 7. Threats

- **Capacity × site mutation at FLIP-0004** (s2).
- **FLIP-0004's plant is near the ruler margin.**
- **One block-duplication family at one rate.** A null weakens "duplication opens" only for this operator.
- **R0 at 4x** has a prior record in C2B (0/32, C2A seeds); C3R re-measures it on C3R seeds.
- **Same author.** Review is requested and is not a gate.
