# PTE-C2A preregistration: search-limit localization

Status: FROZEN at the commit that adds this file together with FREEZE_C2A.json and PLAN_C2A.json. That commit
comes before any production search row. Flight data are not production data (s9).

Authority: the operator's direct science order of 2026-10-05, recorded verbatim at
roles/Ananke/prompts/2026-10-05_pte_c2a_directive/ (34bcebe4b). No other activation is needed (order s17).

Design input: research/harvest/wave2/W2-AB/PREREG_PTE_C2_DRAFT.md. This document is the preregistration; the
draft is not. Where the two differ, this document governs, and every difference is listed in s10.

## 1. Question

At PTE cells where:
- the physics permits the task (P excluded);
- a valid plant exists inside the searched genome space (R excluded);
- a qualified ruler recognizes the plant and rejects cheap false friends (V excluded);

is C1-style failure caused by the evolutionary search, or by selection (U)?

Families: RELAY-mh (every held world needs at least 2 transport hops) and FLIP.
The maximum claim is family-scoped:

> Within the admitted RELAY-mh/FLIP cells tested, C1-style competence failure localizes primarily to
> search/selection rather than physics/representability/ruler failure.

Its negative is equally reportable. Nothing here is a statement about PTE physics at large.

## 2. Code and data

- **Code:** roles/Ananke/pte/c2a/ at the code SHA in FREEZE_C2A.json.
  - c2a_common.py: plants, adversaries, rulers, namespaces.
  - admit.py: P/R/V admission.
  - run.py: search runner.
  - make_plan.py: cells and job order.
  - reduce.py: every verdict rule below, as code.
- **Engine:** prometheus/ananke at the same SHA. The engine is unmodified. search.py's random_genomes, mutate and
  crossover are imported unchanged.
- **Admission rows:** pte/c2a/admission/*.jsonl.gz.
- **Plan:** PLAN_C2A.json (sha256 in FREEZE_C2A.json).

## 3. Admission (P, R, V), computed on CPU before any production search

**Candidates.** The W2-AD seeded sampler (census.candidate, SEED 0xC2AD0001), 200 per family.
- Physics comes from the C1 A0 dial ranges.
- The C2 genome spec is imposed: prog_len 16, rules 1, setrule 0, state_dim 2, payload_width 1, channels 1,
  economy off.
- None of these cells was searched by C1.

**Admission worlds.** Each candidate gets 128 worlds (64 mirror pairs) under H(C2A_NS = 0xC2A01005, 0xAD01,
family, i), fresh.

**P (physics):**
- RELAY: every world needs at least 2 transport hops (graph BFS sensor -> actuator).
- No world may be impossible.
- Joint ceiling: the min of the task2_timing, w2u, LC2k and epidemic bounds (W2-AD joint_ceiling), computed on
  the SAME 128 worlds as the plant. It must reach the threshold:
  - RELAY: max(A90(.55, K), A90(.55, K/2)) + .05;
  - FLIP: max(.90, A90(.75, K) + .05);
  - A90 is the true accuracy at which lo99 crosses the cut with 90% power at P = 64 (W2-B
    attain.min_true_to_cross).
- Failing P gives P-CAPPED (or OUT_OF_STRATUM).

**R (representable):**
- Plant designs are scored in a declared order:
  - RELAY: relay_refresh, then relay_flood (relay_bit is descriptive);
  - FLIP: P_FLIP only (FLIP_BIT16 is descriptive).
- A plant passes when its competence ruler (s4) is TRUE and its must-fail ablation is not TRUE:
  - RELAY: the sensor is silenced;
  - FLIP: the teacher is removed after trial 0.
- The plant of record is the first design that passes. No pass gives R-NOT-ESTABLISHED.
- Every plant is in the GA's sampling support. REPAIR R1 (s8) re-encodes CONST 128 as imm 64 with shift 1. The
  canonical genome is scored and injected.

**V (valid ruler).** Every in-scope adversary must read FALSE under the same ruler. An INDETERMINATE adversary
fails V.
- RELAY adversaries: null, onehop (sensors emit, nobody forwards), latch_once (a once-per-episode flood latch;
  in scope only at decay_shift 0, because with decay it re-arms and is a working relay).
- FLIP adversaries:
  - null;
  - RELAY_LATCH (the copy policy);
  - latch_once (same scope rule);
  - anti-copy: the analytic complement of RELAY_LATCH per trial.
- FLIP_CLOCK needs prog_len 28 or more and state_dim 4 or more. It lies outside the genome space, so no
  champion can be it.

**Ceiling violation:** the plant's mean is above ceiling + max(.01, 2.605 SE).
- On a core cell, this is a STOP for the whole admission run.
- On a rejected candidate, it is recorded.

**Admission result (computed 2026-10-05):**
- RELAY: 17 admitted. Rejected: 106 out of stratum, 52 P-CAPPED, 25 R-NOT-ESTABLISHED, 0 V-FAILED.
- FLIP: 4 admitted. Rejected: 147 P-CAPPED, 48 R-NOT-ESTABLISHED, 1 V-FAILED.
- 0 ceiling violations.

**Selection (outcome-blind, declared before any search):**
- Per family, take the admitted candidates in ascending index and keep the first 4.
- Sampler order is a seeded random draw. There are no C1 anchors, so the anchor/fresh sensitivity split is void:
  every cell is fresh.
- Rejected candidates and their failing clause are listed in PLAN_C2A.json.

## 4. Competence-class rulers (search success, plant validity, PSEED retention)

Every reading is inference.reading3 at BOOTT 99%, with margin_se = margin_for_keep(.95, f = 1.12) = 2.605 SE.
Held set: 128 worlds (64 pairs) per search under H(search_seed, HELD_NS).

- **RELAY-mh.** TRUE iff both hold:
  - SIGNAL on all trials (lo99 > .55, reading3 TRUE);
  - the late-half liveness guard: trials tr/2 and later, two-valued BOOTT lo99 > .55.

  The late guard rejects once-per-episode flood latches (E-W22).
- **FLIP.** TRUE iff B = mean(changed-cue acc, same-cue acc) has lo99 > .75 (reading3 TRUE).
  - FLIP_FEEDBACK is not used.
  - Copy and anti-copy sit at B ≈ .5.
- **RELAY-1h (positive control).** SIGNAL on all trials (reading3 TRUE).

Overall status: TRUE iff every component is TRUE, FALSE iff any component is FALSE, otherwise INDETERMINATE.
A search succeeds iff its champion is TRUE.

## 5. Search arms (per admitted core cell; the search seed is the unit; arms are paired by seed index)

**BASE** is the C1 protocol: pop 96, gens 36, M 8, elite 4, trunc .25, p_field .04, p_instr .15, p_swap .10,
p_cross .30, M_final 16, w_contrast .10, w_any .02. The champion is chosen on final training accuracy at
M_final 16.

| arm | change from BASE | seeds per cell |
|---|---|---|
| BASE | none | 12 |
| W0 | w_contrast = w_any = 0 | 8 |
| M32 | M = 32 | 8 |
| PSEED | plant of record at gen-0 index 0 | 4 |
| KSEED-1/2/4 | plant at index 0 with k distinct fields resampled from the GA's own field distribution (a draw equal to the old value is redrawn) | 4 each |

**Pairing (common random numbers).**
- search_seed = H(C2A_NS, 0x5EED, cell_key, idx) is shared by every arm at seed index idx: the same gen-0
  population and the same training-world stream.
- world_seeds is prefix-consistent in M.
- The seeded arms overwrite index 0 only.

**Control cell:** C1 d9cc RELAY d=3 delta=8, exact C1 physics and env. BASE 8 and PSEED 2 (plant relay_flood).

B4X and STEP are excluded by default (order s6). They would be added only by an amendment committed before
production, under the s6 conditions.

## 6. Verdicts

All verdicts are computed by reduce.py, verbatim.

**Cell verdicts** (evaluated in this order):
1. A stop flag gives SUSPENDED: the plant reads FALSE on any search's held worlds, a champion sits above
   ceiling + .05, or held and train seeds overlap.
2. U-LOCATED: any PSEED champion is FALSE (the plant was lost), regardless of k_BASE (k_BASE is reported).
3. SEARCH-SUCCEEDS: k_BASE ≥ 6.
4. S-PARTIAL: 2 ≤ k_BASE ≤ 5.
5. S-LOCATED: k_BASE ≤ 1, n_BASE ≥ 10, and PSEED TRUE in every completed PSEED seed (at least 4).
6. UNRESOLVED: anything else, including an INDETERMINATE PSEED.

**Landscape form.** Computed for S-LOCATED and S-PARTIAL cells, pooled over the family's such cells. Contrasts
use only seed indices completed in both arms.
- **RESPONSIVE:**
  - W0 or M32 beats BASE (one-sided Fisher on pooled counts, BH q .05 over the 2 contrasts); or
  - KSEED recovery > 0 at k = 2 or 4 (a climbable basin).
- **NEEDLE-LIKE:** no response arm (each Newcombe upper 95% bound on the success difference < .25), KSEED-1
  recovery > 0, KSEED-2 = KSEED-4 = 0.
- **LOCALLY_FLAT:** no response arm (bounded as above) and KSEED-1 recovery = 0. It is reported as "under the
  measured mutation/operator neighbourhood, the known solution lies in a locally unrecoverable region", never as
  "a better search would find it".
- **UNRESOLVED:** anything else, including a response arm that is neither significant nor bounded.

**Family verdict** (needs 4 interpretable cells; otherwise CELL_LEVEL_ONLY):
- SEARCH_LIMIT_SUPPORTED: at least 3 cells S-LOCATED.
- SEARCH_LIMIT_NOT_SUPPORTED: at least 3 cells SEARCH-SUCCEEDS or U-LOCATED.
- MIXED: otherwise.
RELAY-mh and FLIP are reported separately.

**Positive control.** SEARCH_HARNESS_FAILED iff a control PSEED is lost, or n_BASE ≥ 4 and k_BASE/n_BASE ≤ .25
(that is, ≤ 2 of 8). If n_BASE < 4 the verdict is CONTROL_UNDERPOWERED. In either case no core-family search
failure is interpreted.

**Classification error at n_BASE = 12 (binomial; C2 draft s6.4):**
- a true rate of .05 is called S-LOCATED with probability .88;
- a true rate of .10 is called S-LOCATED with probability .66;
- a true rate of .30 is called SEARCH-SUCCEEDS with probability .12;
- a true rate of .50 is called SEARCH-SUCCEEDS with probability .61.

These are reported with every verdict.

## 7. Production envelope, schedule, censoring

- **GPU:** the M1 RTX 5060 Ti, under Fabric lease skullport:gpu0.
- **Workers:** 3 concurrent workers on the one GPU (Flight 2 measured about 1.35x throughput for 2 workers over 1,
  with mean GPU utilization 94% and peak VRAM 3.2 GB at 3).
- **Wall time:** projected at 11 h or less (FREEZE_C2A.json), with a hard wall of 12 h. Each worker gets
  --deadline-utc = launch + 11 h 30 m and starts no job after it. A job in flight finishes.
- **Order:** rounds by seed index. Within a round, cells interleave R1 F1 R2 F2 R3 F3 R4 F4 CTRL. Within a cell,
  the arms run PSEED, KSEED-1, KSEED-2, KSEED-4, BASE, W0, M32. Jobs are claimed dynamically in plan order.
- **Censoring:** contrasts use only indices completed in both arms. A cell whose n_BASE is below 10 cannot be
  S-LOCATED. Asymmetric truncation is never read as "no response".
- **No mid-run changes** of any kind: generations, mutation, plants, rulers or cells (order s23). A defect
  found mid-run stops the run and is reported. It is never patched into the same run.

## 8. Repairs made during preparation (each with a test; semantics recorded)

- **R1. Plants outside the GA support.**
  - P_FLIP, FLIP_BIT16 and relay_bit carried CONST imm 128; the GA samples imm in -128..127.
  - Fix: c2a_common.canonical, which re-encodes the constant as imm 64 with shift 1.
  - Semantics: identical while Kp = 0. With site mutation the constant is perturbed by 2 Kp instead of Kp, so
    the canonical genome was re-admitted.
  - Test: test_canonical_plants_in_ga_support_and_equivalent_at_kp0.
  - The engine is unchanged.
- **R2. Ruler late-half component.** It is two-valued (lo99 > .55), not reading3. The reason is that, at the
  2.605-SE margin, it rejected every RELAY plant at dev cells. Decided before any search.
- **R3. latch_once scope.** It is a V adversary only at decay_shift 0. With decay it re-arms, and it relayed at
  .78 at a dev cell. Decided before any search.
- **R4. Runner file names.** The job-id file names on Windows were made safe. This is mechanical and has no
  semantic effect.

## 9. Flights (not production)

- **Flight 1** (admission and instruments):
  - flight1_gates.py: G6 reproduces four C1 champions bit-exactly on CPU and GPU (6f82f9c7 .4791666667 and
    three d9cc RELAY-1h). G7 shows CPU = GPU accuracy arrays. G8 is the PSEED pilot at C1 FLIP@d9cc, which
    never enters production.
  - The PTE test suite: 268 passed, plus 95 conformance tests with CUDA (graph replay).
  - The C2A tests.
- **Flight 2:** a miniature end-to-end run on RELAY-0010, FLIP-0000 and the control under FLIGHT-only seeds
  (cell_key -> H(cell_key, 0xF11647)). No flight seed is a production seed. Flight outcomes changed no design
  rule. Only runtime and harness facts were used.

## 10. Differences from the W2-AB draft

- Families: RELAY-mh and FLIP only. No MAJ, no XOR, no HOLD.
- No B4X or STEP.
- The control is one RELAY-1h cell (BASE 8, PSEED 2).
- Every cell is fresh. There are no anchors.
- RELAY-mh competence uses the late-half liveness guard in place of REACH_BEYOND_HOP_NEAREST plus a native 2-hop
  check. The stratum already requires at least 2 hops in every world, so SIGNAL needs forwarding.
- The mutation-gate (W2-C) and explib provenance machinery are not on the C2A path. They are replaced by:
  - the stated known-answer tests;
  - the held/train/admission disjointness assertion in make_plan.py;
  - genomes and final populations saved for every search.
- explib certify_gate is not on the C2A path. Attainability is enforced by:
  - the ceiling threshold;
  - the requirement that the plant pass the actual ruler on fresh worlds (golden tests:
    test_attainability_golden_*).
- rng.py's 32-bit counter hash (world seeds) is on the path, and it is unmodified so that C1 reproduces exactly.
  Aliasing is guarded by the disjointness assertion: 0 overlaps.
- The GA's own RNG is numpy PCG64.

## 11. Known unresolved threats

- **Same author.** One seat wrote the plants, rulers, adversaries and verdict code. There is no external
  review before the run (operator order: run tonight).
- **Designer-tuned plants.** "S" can read as "the GA did not find what a designer found". R is excluded for the
  plant family only.
- **Held-out is in-distribution.** Held worlds share the cell's graph and constants.
- **No in-situ provenance guard** for randomize_source-type corruption (W2-C F9). The mitigation is saved
  genomes plus re-evaluation.
- **n = 12 BASE** cannot separate true rates of .15 to .4 from either pole. Such cells land in S-PARTIAL or
  UNRESOLVED.
- **The late-half guard is two-valued.** A champion near lo99 = .55 in the late half flips on world noise.
- **The FLIP B ruler is near-cheatable by the copy policy at some physics.** At FLIP-0184, RELAY_LATCH reached
  B .76 (same-cue 1.0, changed-cue .52), which reads INDETERMINATE. V excluded that cell. On the 4 admitted FLIP
  cells the copy adversary reads FALSE. An evolved copy-like champion at an admitted cell is therefore expected
  to read FALSE, not TRUE.
- **Response-contrast power.** W0 and M32 have 8 seeds each, per the operator's defaults; raising them to 12
  projected 10.5 h on the conservative model and was rejected. If only one cell of a family is S-LOCATED or
  S-PARTIAL, 0/8 vs 0/8 cannot bound the difference below .25. The landscape form is then UNRESOLVED, not
  "no response".
- **Admission used the same sampler as the incomplete W2-AD census.** The cells were seen there with
  non-canonical plants and 32 pairs (admission information only, never search outcomes). C2A re-admits them
  from scratch on fresh worlds.
