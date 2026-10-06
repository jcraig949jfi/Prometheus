# Preregistration: C2BX (RELAY budget extension) and PTE-C2C (FLIP operator x path geometry)

Status: FROZEN at the commit that adds this file, PLAN_C2C.json and FREEZE_C2C.json. That commit comes before any
production row.

**Authority:** the operator order of 2026-10-06, roles/Ananke/prompts/2026-10-06_c2b_close_c2bx_c2c/ (64dad7553).
Both campaigns are successors to PTE-C2B, which is CLOSED. The C2B packet and classifications are unchanged.
C2B's external review continues as a non-blocking audit.

**Inputs:** C2B result 1ac44021c (rows_C2B.jsonl.gz, pops_C2B.tar). The C2A instrument (c2a_common) and the C2B
lineage-tagged operators (c2b_common) are imported unchanged.

**Interpretive shorthand (operator ruling):** RELAY-mh is "scaffold-enabled reconstructive reachability", not
"locally repairable".

## Part 1: C2BX, the RELAY budget extension (a measurement campaign, not a repair campaign)

**Scope.** It continues the 32 C2B B4X searches unchanged: RELAY-0010, 0019, 0027 and 0032, idx 0-7. There is no
new operator, ruler, representation or starting population.

**Continuation.** Each search reruns its exact C2B trajectory from the same search_seed (C2A
search_seed(cell_key, idx)). It uses the same BASE settings and the frozen operator, and runs to 576 generations,
which is 16x the C2A budget of 36.

**Prefix gate.** Every row is gated on two conditions:
- the population after gen 144 equals C2B's saved B4X final population;
- the champion statuses at 36/72/108/144 equal C2B's.

A failing row is excluded.

**Checkpoints.** A champion is taken every 36 generations (C2B's rule) and scored on the held set: gen 36, 72, ...,
576, 16 checkpoints in all.

**Reported:**
- per cell, pooled, and leave-RELAY-0019-out;
- cumulative success at 4x, 8x and 16x, meaning a competent checkpoint champion at a generation ≤ 144, 288 or 576;
- first competent generation;
- persistence;
- final status at each budget;
- arrivals in (144, 288] and in (288, 576].

**Tail classification.** NEW = competent by 576 and not by 144.

| label | rule |
|---|---|
| TAIL_CONTINUES | ≥ 4 NEW, in ≥ 2 cells |
| TAIL_SPARSE | 1-3 NEW, or all NEW in one cell |
| TAIL_STOPS | 0 NEW |

The classification is computed pooled and leave-0019-out. The campaign stops at 16x regardless of outcome. There
is no further escalation.

## Part 2: PTE-C2C, FLIP operator x path geometry (2x2)

**Fixed:**
- the 4 FLIP cells: FLIP-0000, FLIP-0004, FLIP-0099, FLIP-0167;
- the plant of record (P_FLIP, canonical);
- the B ruler and success criterion: B lo99 > .75, reading3 TRUE, margin 2.605 SE;
- the 36-generation budget and the BASE settings.

**Seeds.** Seeds are fresh: H(C2C_NS = 0xC2C01006, 0x5EED, cell_key, idx) for idx 0-7. They are shared by all four
arms at the same idx (common random numbers: the same gen-0 population and training worlds). The STEP arms
overwrite index 0 only. The held set is H(search_seed, HELD_NS), 128 worlds.

**Operators.**
- **OP0:** the frozen C2A/C2B mutation (c2b.mutate_tagged).
- **OPB:** OP0, then with probability .25 one mechanism-blind block move.
  - The rule is chosen uniformly.
  - Block length is uniform over {2, 3, 4}.
  - Start and target positions are uniform.
  - The kind is uniform over DUPLICATE, MOVE and REPLACE.

  All of these are fixed before production and independent of genome content (tested). No knowledge of any FLIP
  solution is encoded.

**Starts.**
- **BASE:** a random gen-0 population.
- **STEP:** the graded stepping stone for that (cell, idx) at index 0. The stone is the first draw, in attempt
  order, of k = 1 (even attempts) or 2 (odd attempts) GA-native field edits of P_FLIP from
  rng(C2C_NS, 0x570E, cell_key, idx, attempt) that meets all of the following on STONE_QUAL worlds
  (H(C2C_NS, 0x5A0E, cell_key), 128 worlds):
  - FALSE under the B ruler;
  - B mean ≥ .60;
  - B hi99 < .75.

  The cap is 200 attempts.

  Result: 28 of 32 stones qualified, with B .600-.718. FLIP-0000 has no stone at idx 2, 4, 5 or 7, so STEP is
  UNAVAILABLE there and is preserved as such, not tuned. The same stone is used in OP0_STEP and OPB_STEP
  (paired).

**Arms.** OP0_BASE (32), OPB_BASE (32), OP0_STEP (28), OPB_STEP (28).

**Success counts.**
- BASE arms count any competent champion.
- STEP arms count STEP_LINEAGE_SUCCESS: the champion is competent and its lineage share is ≥ .5 (C2B's tag
  definition). Background successes are reported separately.

**Material(x vs y).** Computed on the (cell, idx) pairs present in both arms. It requires all three:
- x ≥ 4;
- x's successes span ≥ 2 cells;
- x − y ≥ 4.

One-sided Fisher p values and exact CP95 intervals are reported beside the counts but do not enter the rule.

**Classification,** with a = OP0_BASE, b = OPB_BASE, c = OP0_STEP, d = OPB_STEP. The rules are applied in order:

| condition | label | operator's interpretation |
|---|---|---|
| Material(c vs a) and Material(d vs b) | BASIN_PATH_ACCESSIBILITY_BARRIER (suffix _WITH_OPERATOR_EFFECT if Material(b vs a)) | the stepping stone improves under both operators |
| Material(b vs a) and neither Material(c vs a) nor Material(d vs b) | OPERATOR_GRANULARITY_BARRIER | the block operator improves; little stepping-stone effect |
| Material(d vs a), but neither Material(b vs a) nor Material(c vs a) | COMPOUND_SEARCH_GEOMETRY_BARRIER | operator x stone interaction |
| none of the four contrasts material | NEITHER_IMPROVES (suffix _WITH_SPARSE_EXCEPTIONS if any success occurred) | operator/path explanations weakened; a representation experiment becomes the next campaign |
| anything else | MIXED (the material flags listed) | |

Isolated one-seed recoveries stay SPARSE_EXCEPTIONS unless they replicate across cells.

## Exclusions and stop conditions (both parts)

Each of the following is flagged, and the row is never counted as a success or a failure:
- PLANT_FALSE: the plant reads FALSE on the row's held worlds;
- START_COMPETENT: a C2C stone reads TRUE on the held worlds;
- OVERLAP: held and train worlds overlap;
- PREFIX_FAIL: a C2BX prefix gate fails.

There is no mid-run change of any kind. A semantic defect means re-freeze, never a patch.

## Production

**Hardware and order.** One 3-worker queue on the M1 RTX 5060 Ti (Fabric lease lse-d5be3b4e224c). All 32 C2BX jobs
come first. They are the long jobs, and running them first means a wall censors only the last C2C rounds, which
are balanced across arms. The C2C jobs then run in rounds by idx, with cells interleaved and arms in the order
OP0_BASE, OPB_BASE, OP0_STEP, OPB_STEP.

**Projection** (C2A per-tick model): 9.15 h central and 11.34 h conservative. Calibrated by C2B's actual/central
ratio of 0.84, that becomes about 7.7 h central and 9.5 h conservative.

**Deadline.** Launch + 11 h 30 m; no job starts after it. The hard wall is 12 h. A C2BX job in flight at the wall
finishes, so cumulative curves use only completed rows.

## Flights

- **Flight 1.**
  - The C2BX prefix replay at RELAY-0019 idx 1, to gen 145, passed: the population at 144 and the 36-144 statuses
    are identical.
  - test_c2c.py passes 5/5: block-operator kinds and tags; OPB equals OP0 before the block step; content
    blindness; the stone rule; fresh seeds. test_c2b.py also passes.
  - The batched stone scoring reproduces the sequential choice (attempts 32 and 33, identical B).
  - The plant does not read FALSE on any stone-qualification set.
- **Flight 2.**
  - The C2C four arms ran at FLIP-0004 idx 8, a non-production index whose stone was qualified by the frozen rule.
  - The C2BX code path ran at RELAY-0010 idx 0, limited to the published 145-generation prefix: gate PASS, no
    generation beyond 144 computed.
  - 5/5 jobs, 0 errors, 0 flags. The reducer ran end to end.
  - Measured: a C2C 36-generation job takes 91-97 s; the C2BX 145-generation job took 213 s.
  - Flight outcomes changed no rule.

## Known threats

- **FLIP-0004's plant is near the ruler margin.** It reads INDETERMINATE on the stone-qualification worlds
  (B .874, lo99 .804, d_se 2.35) while reading TRUE on every C2A/C2B held set. A plant-quality champion there may
  not read TRUE, which biases FLIP-0004 toward failure in every arm alike.
- **The graded stones are degradations of the plant** (1-2 edits). STEP therefore tests path accessibility from a
  partially functional near-plant. That is not a mechanistically distinct intermediate, and STEP is not a
  representation test.
- **OPB adds block moves on top of OP0** (P_BLOCK .25). It is one operator family at one rate. A null result
  weakens "operator granularity" only for this family.
- **Thresholds are fixed by the same author.** The C2B external review is still pending.
- **The C2BX held set** is C2A's held set for the same seed index, the same as in C2B.

## Candidate questions for a representation experiment (recorded only; not designed; spent only if C2C leaves FLIP substantially inaccessible)

1. Does FLIP become accessible if the genome can express a persistent mapping bit as a first-class state
   (state_dim 3 or more, or a dedicated latch register), rather than through MULQ/SEL arithmetic on decaying
   state?
2. Is the teacher-to-mapping update one instruction away in some alternative instruction set (for example a
   conditional XOR-into-state op), and does that change BASE discovery?
3. Does a larger program space (prog_len 24, the C2 draft's FLIP fallback) or rules > 1 change accessibility
   without changing the plant's competence class?
4. Does the copy plateau persist under a representation in which the mapping inversion is a single field change?
