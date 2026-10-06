# PTE-C2B preregistration: search-barrier dissection

Status: FROZEN at the commit that adds this file together with PLAN_C2B.json and FREEZE_C2B.json. That commit
comes before any production search row. Flight rows are not production data.

**Authority:** operator order of 2026-10-05, recorded verbatim at
roles/Ananke/prompts/2026-10-05_pte_c2b_directive/ (204a69374). It authorizes freeze and execution.

**Inputs:** PTE-C2A is closed and its artifacts are unmodified. The C2A input SHA is b3b2863fd. That commit
holds the result packet, PLAN_C2A.json, rows_C2A.jsonl.gz and pops_C2A.tar.

## 1. Question

At the 8 C2A cells, search almost never constructs a competent mechanism (BASE 1/96), even though valid solutions
exist and are retained (PSEED 32/32). The question here is what kind of barrier causes that:
- **gradient:** can a genuinely broken near-plant be repaired?
- **budget:** does four times the generations open the competence class?
- **path:** does a mechanistic stepping stone convert into competence?

RELAY-mh and FLIP are classified separately.

## 2. Fixed instrument (imported from roles/Ananke/pte/c2a/, unchanged)

- **Cells:** RELAY-0010, RELAY-0019, RELAY-0027, RELAY-0032, FLIP-0000, FLIP-0004, FLIP-0099, FLIP-0167. Exact
  physics, env and cell_key come from PLAN_C2A.json.
- **Plants:** the canonical plants of record. relay_refresh for RELAY; P_FLIP for FLIP.
- **Rulers:** c2a_common.competence.
  - RELAY-mh: SIGNAL reading3 TRUE on all trials, plus the late-half guard lo99 > .55.
  - FLIP: B lo99 > .75, reading3 TRUE.
  - Margin: 2.605 SE.
- **Engine and search:** prometheus.ananke is unchanged. The BASE settings are pop 96, M 8, elite 4, trunc .25,
  p_field .04, p_instr .15, p_swap .10, p_cross .30, w_contrast .10, w_any .02, M_final 16.
- **Champion and held set:**
  - The champion is the argmax of final training accuracy.
  - Held: 128 worlds under H(search_seed, HELD_NS). These are C2A's held worlds for the same seed index.
- **Seeds:** search_seed = C2A's search_seed(cell_key, idx) for idx 0 to 7. Every arm shares C2A BASE's gen-0
  population and training worlds at that index (common random numbers). Seeded arms differ only at index 0.

## 3. Arms (per cell, seed indices 0-7)

### BRK1 and BRK2: broken-start recovery (order s4-s9)

**Construction.** For each (cell, k ∈ {1, 2}, idx), the start is chosen as follows:
- attempt a draws exactly k distinct GA-native field edits of the plant, from
  rng(C2B_NS = 0xC2B01005, 0xB7E0, cell_key, k, idx, a);
- fields 0-3 are drawn uniformly from 0..255 and field 4 uniformly from -128..127; a draw equal to the old value
  is redrawn;
- each candidate is scored with the frozen ruler on C2B_BROKEN_QUAL (128 worlds,
  H(C2B_NS, 0xB0E1, cell_key));
- the first FALSE draw wins. TRUE and INDETERMINATE draws are rejected and redrawn, with a cap of 50 attempts.

**Result of construction:** 128 of 128 starts qualified, 0 failures. Every attempt and edit record is in
PLAN_C2B.json.

**Search:** the start sits at gen-0 index 0, then the 36-generation BASE search runs.

### B4X: budget (order s10-s13)

- BASE with gens 144, at C2A BASE seed indices 0-7. Nothing else changes.
- Champions are taken at gens 36, 72, 108 and 144.
  - Gen 36 uses C2A's FINAL_NS key exactly.
  - Later checkpoints use H(search_seed, FINAL_NS, 0xC4E7, gen).
  - Every checkpoint is scored on the held set.
- **Prefix gate**, recorded per row. All four conditions must hold:
  - the gen-36 population equals the C2A BASE final population (pops_C2A.tar);
  - the gen-36 champion equals the C2A champion;
  - the competence status equals C2A's;
  - the accuracy curve for gens 0-35 is identical.
  A failing row is excluded and flagged (stop condition).
- **NEW_AFTER_36:** the gen-36 champion is not TRUE, and some gen-72, gen-108 or gen-144 champion is TRUE.
- Also recorded per row: the first competent checkpoint, and persistence thereafter.

### STEP: mechanistic stepping stone (order s14-s19)

**Selection rule.** Candidates are declared in order. The first candidate that qualifies at ALL four cells of a
family becomes the family's stone. If none qualifies everywhere, a cell uses the first candidate that qualifies
there; otherwise STEP is unavailable at that cell.

**Qualification** (STEP_QUAL worlds: 128, H(C2B_NS, 0x57E9, cell_key)):

- **RELAY-mh.**
  - Qualifying conditions:
    - RELAY-1h ruler TRUE on the cell's one-hop variant (same physics, env d = 1, every world exactly 1 hop);
    - RELAY-mh ruler FALSE on the production env.
  - Candidate 1, relay_step: relay_refresh with emission gated on the site's own sensor. It FAILED one-hop at
    all 4 cells (.536-.547).
  - Candidate 2, relay_step_sense: relay_refresh with the emit line EMIT := T2*T3 changed to
    EMIT := SENSE*SENSE. Sensors broadcast every cue tick, receivers latch, and nobody forwards. It is 2 field
    edits from relay_refresh.
    - Declared at Flight 1, after candidate 1 failed and before any STEP search.
    - QUALIFIED at all 4 cells: one-hop .853-.985, multi-hop exactly .500.
    - It is the RELAY-mh stone.
- **FLIP.**
  - Qualifying conditions:
    - B ruler FALSE;
    - B hi99 < .75, so the stone is not near the boundary;
    - same-cue accuracy ≥ .75, showing the copy/latch subfunction.
  - Candidate: RELAY_LATCH, canonical. It qualified at FLIP-0000, FLIP-0004 and FLIP-0167.
  - At FLIP-0099, B is .745 with hi99 .776, so STEP is UNAVAILABLE there. It was not tuned.

### Arm sizes

- 8 seeds per arm per cell. The exception is STEP at FLIP-0099, which has 0.
- Total: 248 jobs.
- Order: rounds by idx 0-7. Within a round, cells interleave R1 F1 R2 F2 R3 F3 R4 F4. Within a cell the arms run
  BRK1, B4X, STEP, BRK2. This order follows the order's shrink priority.

## 4. Lineage attribution (order s7, s17)

**Tags.** Every instruction line carries an origin tag: True iff it descends from the injected genome.
- Field resampling keeps the tag (descent with modification).
- Whole-instruction resampling sets it False.
- Swaps and uniform line crossover move tags with their lines.
- Elites keep their tags.

The tagged operators consume the GA's RNG in exactly search.py's order, which test_c2b.py verifies.

**Lineage share** of a genome = the fraction of its lines tagged True.

**Attribution of a competent champion:**
- share ≥ .5 means it descends from the injected genome: BROKEN_LINEAGE_RECOVERY (BRK) or
  STEP_LINEAGE_SUCCESS (STEP);
- otherwise it is BACKGROUND_SUCCESS.

**Recorded per row:**
- the injected genome ID;
- the edit record;
- the per-generation lineage count and the best lineage member's training accuracy and rank;
- the generation at which the lineage went extinct;
- the competence of the injected start and of the best final lineage member on the held set;
- per-generation parent indices (pops/*.npz), so the mutation and crossover path can be reconstructed.

## 5. Verdicts (reduce_c2b.py, verbatim; n = counted rows; exact Clopper-Pearson 95% intervals)

**Row exclusions.** Each is flagged and reported. An excluded row is never counted as a failure or a success.
- PLANT_FALSE: the plant reads FALSE on the row's held worlds.
- START_COMPETENT: a BRK or STEP start reads TRUE on the held worlds.
- OVERLAP: held and train worlds overlap.
- PREFIX_FAIL: a B4X prefix gate fails.

**Arm verdicts:**

| arm | count | top tier | middle tier | zero tier |
|---|---|---|---|---|
| BRK1, BRK2 | BROKEN_LINEAGE_RECOVERY | LOCALLY_REPAIRABLE: ≥ 4, in ≥ 2 cells | SPARSE_REPAIR_PATH: 1-3, or concentrated in one cell | LOCALLY_FLAT_SUPPORTED: 0 |
| B4X | NEW_AFTER_36 | BUDGET_RESPONSIVE: ≥ 4, in ≥ 2 cells | WEAK_BUDGET_RESPONSE | NO_BUDGET_RESPONSE: 0 |
| STEP | STEP_LINEAGE_SUCCESS | STEP_RESPONSIVE: ≥ 4, in ≥ 2 cells | WEAK_STEP_RESPONSE | NO_STEP_RESPONSE: 0 |

For FLIP, STEP has n = 24 (3 cells). The thresholds are unchanged.

**Family classification** (order s20). Let R be the set of arms that reach their top tier, from BRK1, B4X and
STEP. BRK2 is reported as strengthening only.
- R empty: LANDSCAPE_BARRIER. The suffix is _STRICT if BRK1, B4X and STEP all count 0, otherwise
  _WITH_SPARSE_EXCEPTIONS.
- R = {B4X}: BUDGET_LIMITED.
- R = {STEP}: STEPPING_STONE_LIMITED.
- R = {BRK1}: LOCAL_BASIN_BARRIER.
- Otherwise: MIXED, with R listed.

LANDSCAPE_BARRIER is reported as: "Under the tested operators, nearby broken states, extra search time, and the
selected mechanistic stepping stone all fail to create an accessible path." It is never reported as global
unreachability.

## 6. Production envelope, censoring, stop conditions

- **Envelope:** the M1 RTX 5060 Ti with 3 workers, Fabric lease skullport:gpu0.
- **Projection:** 6.6 h central, 8.9 h conservative, from C2A's per-tick costs with B4X at 4.0-4.6 times a
  36-generation job.
- **Deadline:** launch + 11 h 30 m. No job starts after it. The hard wall is 12 h.
- **Censoring:** a censored job is simply absent. Arm verdicts use the counted n, with intervals. Asymmetric
  truncation is never read as "no response". Every round contains every arm, so a wall cuts the highest seed
  indices of all arms first.
- **Stop conditions** (order s31) are the exclusions above. Also, any CPU/GPU threshold disagreement, or evidence
  that cannot reconstruct edits, lineage or search state, stops interpretation for that cell and arm.
- **No mid-run change** of any kind (order s32).

## 7. Flights

- **Flight 1.**
  - The C2B tests: 7/7.
  - B4X prefix replay on GPU passed at RELAY-0019 idx 4 (the C2A BASE success) and at FLIP-0000 idx 0.
  - Every plant is TRUE on C2B_BROKEN_QUAL.
  - 128/128 BRK starts qualified.
  - STEP was qualified as in s3.
- **Flight 2.** RELAY-0019 and FLIP-0000 at seed index 8 (never a production index), one job per arm.
  - All 8 jobs completed with 0 errors.
  - Both B4X prefix gates passed.
  - The reducer and attribution ran end to end.
  - Measured: about 80-140 s per 36-generation job and 280-310 s per B4X job (3 workers); mean GPU utilization
    91%; peak VRAM 2.4 GB; 275 KB per 8 jobs.
  - Flight outcomes changed no rule.

## 8. Known threats

- **Same author.** A review packet was posted on comms before launch. If no reply arrives before launch, the
  record reads "EXTERNAL REVIEW PENDING AT LAUNCH".
- **Lineage threshold.** Share ≥ .5 is a line-majority rule. A lineage member that is rebuilt line by line could
  pass as "descended". The per-row share and the parent log allow a re-reading at another threshold.
- **The RELAY stone is 2 field edits from the plant of record.** A STEP success could therefore be read as
  near-plant repair rather than mechanism conversion. BRK2 (2 edits, but broken anywhere) is the comparison
  arm.
- **FLIP STEP has 3 cells (n = 24).** Its family-level reading is weaker than the others.
- **BRK starts are FALSE on the qualification worlds**, and are re-checked on the held worlds (START_COMPETENT).
- **The held set is shared with C2A at the same index.** It is a fixed in-distribution held design, already
  disclosed in C2A.
- **Every result is relative** to the C1 operator, the 16-line genome, pop 96, and at most 144 generations.
