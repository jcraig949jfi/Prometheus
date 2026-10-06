# PTE-C2B result packet: search-barrier dissection

Date: 2026-10-06. Prepared by Ananke, instance m1-46797183, on M1 with the RTX 5060 Ti.

**Provenance**
- Authority: operator order at roles/Ananke/prompts/2026-10-05_pte_c2b_directive/ (204a69374).
- Freeze: c699838cf, code 49baad291, C2A input b3b2863fd. C2A is unmodified.
- Run: 248/248 jobs, 00:25:31Z to 05:58:43Z (5.55 h; the projection was 6.6 to 8.9 h). No censoring.
- Integrity: 0 flags. No PLANT_FALSE, no START_COMPETENT, no OVERLAP. All 64 B4X prefix gates passed: the
  gen-36 population, champion, status and curve equal the C2A BASE search exactly.
- External review: EXTERNAL REVIEW PENDING AT LAUNCH. Request #1659 went to Argus and Aporia. Argus declined as
  out of scope (#1663). No other reply has arrived, and no fatal defect has been claimed.
- Frozen verdicts are from reduce_c2b.py (REDUCE_C2B.json). Sections 3 and 4 are DESCRIPTIVE and do not change
  them.

## 1. Headline: the two families have different barriers

| family | BRK1 lineage recovery | BRK2 | B4X new after gen 36 | STEP lineage success | frozen classification |
|---|---|---|---|---|---|
| RELAY-mh | **6/32** (CP95 .07-.36), 3 cells: LOCALLY_REPAIRABLE | 1/32: SPARSE | **6/32** (CP95 .07-.36), 3 cells: BUDGET_RESPONSIVE | 1/32: WEAK (plus 1 background) | **MIXED: B4X + BRK1** |
| FLIP | 2/32 (CP95 .008-.21), 2 cells: SPARSE | 0/32: FLAT | 0/32 (CP95 0-.11): NO_BUDGET_RESPONSE | 0/24 (CP95 0-.14): NO_STEP_RESPONSE | **LANDSCAPE_BARRIER_WITH_SPARSE_EXCEPTIONS** |

The two families no longer share one pathology.
- **RELAY-mh is rare but reachable.** Four times the generations opens new competent lineages, and broken plants'
  lineages rebuild competence about one time in five. The barrier is quantitative.
- **FLIP behaves as a barrier.** Under the tested operators, extra time, a copy/latch stepping stone and
  two-edit broken starts all fail to create an accessible path. The only exceptions are 2 rebuilds from
  one-edit broken starts. Following order s20, this is reported as a measured landscape barrier, not global
  unreachability.

## 2. Per cell

Counts are lineage-attributed successes out of n, with background successes in brackets.

| cell | BRK1 | BRK2 | B4X new after 36 (any final) | STEP |
|---|---|---|---|---|
| RELAY-0010 | 3/8 | 0/8 | 1/8 (1) | 0/8 |
| RELAY-0019 | 2/8 | 1/8 | 4/8 (5; idx 4 was already competent at 36) | 0/8 |
| RELAY-0027 | 0/8 | 0/8 | 0/8 | 1/8 |
| RELAY-0032 | 1/8 | 0/8 | 1/8 (1) | 0/8 [1 background] |
| FLIP-0000 | 1/8 | 0/8 | 0/8 | 0/8 |
| FLIP-0004 | 0/8 | 0/8 | 0/8 | 0/8 |
| FLIP-0099 | 1/8 | 0/8 | 0/8 | unavailable (copy B .745, near the boundary) |
| FLIP-0167 | 0/8 | 0/8 | 0/8 | 0/8 |

**Heterogeneity.** RELAY's B4X response is concentrated: 4 of the 6 are at RELAY-0019, the cell where C2A BASE
found its only success. Without RELAY-0019, B4X would be 2/24 in 2 cells (WEAK). RELAY's BRK1 recoveries are
spread across 3 cells (3, 2, 1).

## 3. DESCRIPTIVE: what "recovery" actually was

- **No broken edit was ever reverted** (0/9 lineage successes). The recovered champions differ from the plant in
  4-16 of 16 instruction lines (median 14), while keeping a lineage share of .69-1.0.
  - In practice, the broken plant's descendants spread through the population and then rebuilt competence in a
    reworked form.
  - It is genealogical recovery, not one-step local repair. The prereg's "LOCALLY_REPAIRABLE" label should be
    read as "a broken near-plant is a usable scaffold", not as "a local gradient back to the plant".
- **Robustness to the lineage threshold:**
  - RELAY BRK1: 6 recoveries at share ≥ .5, 6 at ≥ .75, 3 at ≥ .9.
  - The single RELAY BRK2 and STEP lineage successes (share .69) do not survive ≥ .75.
  - FLIP BRK1: 2 recoveries at every threshold up to .9.
- **Starts that recovered were partly functional.** The median held accuracy of a recovered start was .566
  (RELAY) and .648 (FLIP), against .540 and .500 for starts that failed. The FALSE starts nearest the boundary
  are the ones that come back.
- **Fate of the injected lineage.** It went extinct in:
  - RELAY BRK1 11/32, BRK2 18/32, STEP 23/32;
  - FLIP BRK1 21/32, BRK2 28/32, STEP 4/24.

  The median extinction generation was 2-6, except FLIP STEP (14.5).
- **FLIP STEP is a trap.** The copy/latch lineage persists (it holds at least half the population at the end in
  19/24 runs), and its champions sit on the copy plateau (median accuracy .675). None converts to B > .75. The
  stepping stone is selectively attractive and leads nowhere under these operators.
- **RELAY B4X timing.** First competent checkpoint: gen 36 for 1 search (the C2A success), then 72, 108, 108,
  144, 144, 144. All 7 stayed competent at every later checkpoint. The arrivals are still occurring at gen 144,
  so the rate has not saturated.
- **FLIP B4X.** Failed champions sit at chance even at gen 144: median .505, maximum .529.
- **C2A consistency.** C2A's post-hoc broken KSEED-1 at RELAY was 0/9. That is not in conflict with BRK1's
  6/32: P(0/9 | p = .19) is about .15.

## 4. Answers (order s35)

1. **Can a genuinely broken one-edit plant recover?**
   - RELAY-mh: yes, in 6/32 (3 cells).
   - FLIP: rarely, 2/32.
   - Recovery happens by rebuilding within the lineage, never by reverting the edit.
2. **A two-edit plant?** Almost never: RELAY 1/32, and that one is fragile to the threshold; FLIP 0/32.
3. **Descendants or independent discoveries?** Every BRK success was lineage-attributed: 0 background
   successes in the BRK arms. STEP had 1 lineage success and 1 background success, both at RELAY.
4. **Does 4x horizon create new competent lineages?**
   - RELAY-mh: yes, 6/31 searches that were not competent at gen 36 became competent. 4 of those are at
     RELAY-0019.
   - FLIP: no, 0/32.
5. **When?** Gens 72-144, with half arriving only in the last block (gen 144). Every one persisted.
6. **Does the one-hop RELAY stone enable multi-hop?** Weakly: 1/32 lineage success, and that one is fragile to
   the threshold. Most stone lineages go extinct (23/32).
7. **Does the FLIP stone enable genuine FLIP competence?** No: 0/24. It produces a stable copy plateau.
8. **Are STEP successes lineage-attributable?** One RELAY success is (share .69); one is background.
9. **Classification:**
   - RELAY-mh: MIXED. It is budget-limited (rare but reachable) and its broken lineages can rebuild. It is not
     stepping-stone-limited.
   - FLIP: a landscape barrier with sparse BRK1 exceptions.
10. **Same pathology?** No. C2A's shared S-LOCATED verdict hid two different barriers: a rarity barrier for
    RELAY-mh, and a path barrier for FLIP.
11. **Justified operator changes:**
    - RELAY-mh: more search, through a longer horizon or restarts. The yield is about 0.2 per 4x-budget
      search at the easiest cell and about 0.07 elsewhere.
    - FLIP: more budget is not justified. The copy plateau is an attractor that the line-level mutation and
      crossover operators cannot leave. The case is for a representational or operator change (for example
      block or module duplication, or a mutation that can rewire the teacher-use pathway as a unit), or for a
      stepping stone with graded B rather than a B ≈ .5-.7 copy policy. Each must be qualified first.
12. **C1/PTE conclusions that change:**
    - (a) C1's 36-generation budget understated multi-hop RELAY reachability. Some C1 multi-hop NULLs are
      budget-censored, not unreachable.
    - (b) FLIP's failure is robust to budget, to a mechanistic stepping stone, and to two-edit proximity. It is a
      property of the operator landscape.
    - (c) "The failure is search" (C2A) now splits into two kinds: rarity (RELAY-mh) and path (FLIP).

**Strongest alternative explanations**
- **RELAY.** The RELAY positives lean on one easy cell (RELAY-0019) for B4X. The BRK "recoveries" are rebuilds
  scaffolded by partly functional starts, not repairs, and the ruler's late-half guard is two-valued, so
  several recovered champions sit at .59-.66.
- **FLIP.** The FLIP barrier may partly reflect the strict B > .75 ruler: the copy plateau gets B ≈ .6-.7, and
  competence needs a discrete mapping-switch mechanism. The landscape is measured under this ruler and this
  operator.

## 5. Next experiment (proposal; needs the operator)

The proposal is FLIP-specific: the operator/representation test. At the same 4 FLIP cells with the same rulers,
compare:
- (i) a block-level mutation operator (duplicate, transpose or replace a contiguous 2-4 line block);
- (ii) a graded stepping stone (a teacher-hold FLIP variant with B in .75-.85 on a deliberately weakened ruler
  margin, qualified first);

against B4X as the paired control. RELAY-mh needs only a cheap budget-scaling curve (8x, 16x at 2 cells) to
estimate the discovery rate, not more mechanism work.

## 6. Files

- `REDUCE_C2B.json`
- `production/rows_C2B.jsonl.gz`: 248 rows, with curves, lineage curves, edits, checkpoints and champions.
- `production/pops_C2B.tar`: final populations, line tags and parent logs.
- `PREREG_PTE_C2B.md`, `FREEZE_C2B.json`, `PLAN_C2B.json`.
- `qual/`, `flight1/` and `flight2/`.
