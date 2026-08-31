# PREREG-EVIDENCE — Evidence Protocol, Gates, Statistics (Phase 3)

Status: FROZEN 2026-08-27, after: G0_PASS (evidence preflight, commit
a516b2d2), instrument validation ALL 7 CASES PASS, hardness calibration on
engineering seeds, battery composition from untouched evidence seeds. No
[TBD] remains. After this freeze: no task edits, no budget raises, no
navigator changes, no gate movement, no M1 patches post-evidence (s44).

## 1. Battery (frozen; results/task_manifest.json)
- Dev: 58 tasks, seeds 3000+, frozen shuffle order (seed 31337): F1 x12
  (E4/M4/H3/VH1), F3 x10 (E2/M5/H3), F4 x12 (E4/M5/H3), F2 x8 (H2/VH6),
  CTRL x10 (case mix 2/3/4), NEGX x6. Strata: 11 EASY / 15 MEDIUM / 13 HARD /
  19 VERY_HARD.
- Alien: 20 tasks, seeds 6000+ (3 MEDIUM / 14 HARD / 3 VERY_HARD).
- All 78 EXPRESSIBLE (constructive witnesses, verified) and REACHABLE
  (edge-checked structural paths). EC = RC = 1.0; the R==E theorem
  (PREREG-TASKS s5) means G2 carries no information and every failure is a
  findability failure.
- Trivial rejection applied at composition (frozen rule: M0c-RX probe seed
  7*seed+13, reject first_solve <= 32): 4 rejected (F1:1, F3:3).

## 2. Arms
- M0 suite: M0a-HC, M0b-POP, M0c-RX (navigators/m0.py, frozen). MAIN
  COMPARATOR: M0c-RX (best on evidence-preflight rows, rule preregistered
  before those rows existed). All three run; gates use M0c-RX.
- M1: IDENTICAL M0c-RX machinery + developmental artifact library:
  - Library: machine-native executable artifacts only (genotypes). Cap 64,
    most-recent-first eviction, genotype-deduped. No labels, no task IDs, no
    oracle data, no strata. (Anti-cheat A1-A3 apply.)
  - Admission after each dev task, in sequence order: the solving genotype
    (if found) plus up to 4 behavior-distinct best-scoring candidates from
    the final population.
  - Use: the extra_pool mechanism of _m0_pop — 50% of immigrant draws come
    from the library (mutated), instead of the seed repertoire. Nothing else
    differs. Every library-derived candidate is metered identically (1
    verifier evaluation). Library lookups are O(cap<=64) uniform draws — no
    hidden intelligence outside the meter.
  - M1 lineages run the dev battery in the frozen order; the library carries
    across tasks within a lineage, never across lineages.
- Ablation arms (same lineup seeds as M1): M1-no-history (empty library ==
  M0c-RX; sanity identity), M1-random-library (library replaced by
  size-matched random-walk genotypes from engineering seeds, refreshed at the
  same admission points), M1-shuffled-history (library accumulated on the
  independent disjoint stream: dev-battery task ORDER permuted by Random(999)
  so artifacts arrive out of correspondence), M1-frozen-half (library frozen
  after dev position 29).

## 3. Replication and pairing
- 5 M0 lineages x 5 M1 lineages, seed-paired: lineage j uses navigator seed
  base 4000+100j (M0) and 5000+100j (M1) with per-task offset = manifest
  position; same task order, same tasks, same verifier. Only history differs.
- Alien zero-shot: M1's library FROZEN at end of dev sequence; alien tasks
  run with frozen library, seeds 5500+100j; M0 alien seeds 4500+100j.
  Adaptation-after-transfer (library unfrozen) is a separate, secondary run.

## 4. Budget model
- Frozen ladder per task: 1000 / 3000 / 10000 / 30000 verifier evaluations;
  identical for every arm; one run at 30000 per (arm, lineage, task), lower
  rungs derived from first_solve (prefix property of budget truncation).
- Meter: 1 evaluation = one candidate scored on the full task table (bitwise
  Hamming objective; exact solve re-verified on the reference VM). All
  candidate sources cost identically.

## 5. Gates (numeric, frozen)
- G1 oracle-solvable: all 58 dev + 20 alien EXPRESSIBLE with verified
  witnesses. (Met at composition; restated as a gate so a later defect
  invalidates rather than reweights.)
- G2 reachable: == G1 by the R==E theorem (disclosed as uninformative).
- G3 M0 nontrivial competence: M0c-RX top-rung CFR on the 42 non-control dev
  tasks (F1/F2/F3/F4) in [8%, 70%].
- G4 findability (PRIMARY): M1 CFR - M0c-RX CFR >= +10pp on the 42
  non-control dev tasks at top rung, AND one-sided paired task-level
  permutation test p < 0.05 (unit = task; statistic = mean over tasks of
  per-task solve-fraction difference across the 5 paired lineages; 10,000
  sign-flip permutations). The permutation test carries the inference; the
  10pp margin is a minimum-effect floor.
- G5 acquisition cost: on jointly-solved non-control dev tasks, HACR =
  M0 median first-solve / M1 median first-solve >= 1.25, bootstrap (tasks,
  10,000 resamples) 90% CI excluding 1.0. Censored analysis reported beside.
- G6 developmental trend: (late-29 CFR delta) - (early-29 CFR delta) > 0,
  permutation p < 0.10 (secondary tier; positions from frozen order).
- G7 frozen alien transfer: M1 zero-shot alien CFR - M0 alien CFR >= +10pp,
  paired permutation p < 0.05 over the 20 alien tasks.
- G8 control selectivity: CTRL-RAND CFR delta <= +15pp. Violation = leakage
  or compute asymmetry investigation; G8 fails regardless of cause.
- G9 causal ablation: M1-random-library and M1-shuffled-history each retain
  < 50% of the (M1 - M0) non-control CFR advantage. (If either retains
  >= 50%, the advantage is not attributable to correspondent developmental
  structure.)
- NEGX (6 tasks) is reported descriptively (solve rates, reuse rates, cost
  inflation vs matched F1/F2) — no gate, preserved as a finding either way.

## 6. Statistical discipline
- Unit = task (n=42 non-control dev; n=20 alien; n=10 CTRL). Never candidate
  rows. Lineage variance reported.
- Every gate reported with observed value, CI, and distance-to-threshold in
  SE units; a pass within 1 SE of its line is labeled weakly informative
  (as G0e was).
- Multiplicity: G4 is the single primary claim. G5-G9 label the verdict tier
  per the mapping below; no re-testing of G4 under alternative analyses.

## 7. Verdict mapping
- Apparatus defect -> TASK_BATTERY_INVALID / ORACLE_COVERAGE_INSUFFICIENT.
- G3 fail -> TASK_BATTERY_INVALID (M0 floor or ceiling).
- G4 fail -> NO_HISTORY_ADVANTAGE (preserved negative).
- G4 pass -> HISTORY_FINDABILITY_ADVANTAGE; +G5 -> HISTORY_COST_ADVANTAGE;
  +G6 -> DEVELOPMENTAL_ACCELERATION; +G7 -> FROZEN_TRANSFER_ADVANTAGE;
  +G8 AND +G9 -> CAUSALLY_REUSED_DEVELOPMENTAL_STRUCTURE (top verdict).
- Forbidden words in any verdict: intelligence, cognition, understanding, AGI.

## 8. Run order (frozen)
1. M0 arms on dev battery (5 lineages x 3 arms).
2. Build M1 exactly to s2 spec; hash before first evidence run.
3. M1 dev lineages (5). 4. Alien zero-shot (M0 + M1-frozen). 5. Ablation
arms. 6. Verdict computation by script (results/gates_verdict.json).
M1 code may not be modified after step 3 begins (s44). Engineering-seed
shakedown of the M1 harness is permitted BEFORE step 3 with seeds < 2000
only.
