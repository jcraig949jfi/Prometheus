# G12 IMPLEMENTATION (BETA-03 E2): ENDPOINT-ALIGNED ACCEPTANCE RULE + TRAP CONTROLS

Status: **implemented and unit-tested; NOT frozen, NOT run on confirmation supply.** The coordinator (Aphrodite) owns
pre-registration, freeze and launch. The only data used here are EXPOSED Beta-02 seeds (LIN 26, 31, 35, 47); no LIN 72+
seed was touched.

Files:
- `roles/Aphrodite/engine/v2b/g12.py`: rule, traps, per-job patch, donor job, post-hoc rescorer.
- `roles/Aphrodite/engine/v2b/tests/test_g12.py`: 16 tests (14 fast, 2 slow).
- `roles/Aphrodite/engine/v2b/receipts/G12_DEV_SMOKE_EXPOSED_2026-10-08.jsonl`: full rows from the 4 smoke donors
  (EXPOSED DEVELOPMENT DATA, NOT EVIDENCE).

No existing engine file was modified.

## 1. The rule (E4_DESIGN s3, as implemented)

| Step | Implementation |
|---|---|
| Folds | VALIDATE's 12 families (O10 plan) are sorted, shuffled with `random.Random(I._seed("APHRODITE/B03/G12/FOLDS/<seed>"))`, and split 6/6. |
| Selection walk | Every candidate library is walked on **every VALIDATE cell the donor builds** (a17.R_VAL = 4 per family, so 48 cells). The walk is `walk.first_qualified` to **SEL_CAP = 100,000**, with the tribunal **T4 v1a, path BOTH** (DIRECT, and every positive is confirmed through ARTIFACT). `max_spurious` is 10,000, unchanged. Cells are the donor's own `V2B/T51-...-val` cells, which are disjoint from transfer cells. |
| reach_f(C) | 1 iff, in >= 1 cell of family f, C reaches a qualified program AND INHERITED is censored **in that same cell**. This is the transfer endpoint's per-cell rule (`b02._gains`) moved onto validation. |
| Score | S(C) = min(reach_fold1, reach_fold2) - LAMBDA * DL(C), with **LAMBDA = 0.25**. |
| Eligible | C != INHERITED, S > 0, and every reached program passes the tribunal. A reached program is qualified by construction; each one is also re-checked through the DIRECT path. |
| Choice | Max S. Ties go to the larger total qualified-walk charge saving vs INHERITED (a censored walk counts as cap), then to the smaller sha256. If nothing is eligible, the choice is INHERITED. |
| Fallback | E4 s5 "min >= 1 OR total >= 3" is implemented behind `FALLBACK = None`, i.e. **OFF**. The coordinator must decide before freeze. |
| Content-freedom | The rule reads no family labels, no schema text and no candidate names, apart from the shared reference key INHERITED. `MEMORISE` appears only in the donor's output flag `memorise_selected` (copied from b02's row format), never in the rule. Tested by random renaming (`test_name_freedom_renaming_keys_keeps_choice`). |

### Description length (DL): definition and justification
`DL(C)` is the sum of `entry_dl` over the entries that C adds to INHERITED. This is a multiset difference on walked
content. Dropped entries cost 0.

`entry_dl(e)` = number of body generators + stated inits + stated finals, where:
- **Body generators:** 1 per schema template (`schema`), or 1 per template in `schemas` (SCHEMA_ALL). An entry with no
  template costs **1 per explicitly listed body**.
- **inits / finals:** 0 if the entry uses the full default space (nothing is stated), otherwise 1 per listed item.

Why: DL counts the irreducible items a library *states*. A schema is one expression that generates many bodies, so it
costs 1. A memorised entry has no generator, so it must list each body and pays for each. The rule never asks "is this
MEMORISE"; it pays for enumeration wherever enumeration occurs.

Exposed values: natural MEMORISE DL = 20 / 18 / 9 / 15 (seeds 26 / 31 / 35 / 47). The memorised plant costs 3 per
program (DL 27-45). A schema costs 1. SCHEMA_ALL costs its number of templates (3-6).

E4's "a 4-entry memorised library must reach one extra family per fold to break even" holds exactly under this DL
(`test_description_length`).

## 2. Trap arms (planted; scored by the same rule)

| Plant | Construction | Why it is a fair control |
|---|---|---|
| **PLANT_OFF** (NULL12) | `[a17.schema_entry("g2_new", gtc.OFF_SCHEMA)] + start`. These are identical entries to the gtc NULL plant. | Unchanged Beta-01/02 junk gate. |
| **PLANT_MEMO** (MEMO12) | One entry per distinct observed **fold** program, verbatim (exact init, body and final), then start. Expression programs have no fold entry and are skipped. | E4's "planted memorised library of the observed programs". The natural MEMORISE (class member bodies x full inits/finals) stays in every g12 run as an un-named candidate. |
| **PLANT_NEAR** (NEAR12) | Source: the donor's best-**supported** derived schema (max LGG `n_pairs`; ties go to the schema text). Its **root operator** is replaced by another `engine.PRIMITIVES` operator. The alternative must instantiate >= 2 in-space bodies and must not be literally or extensionally (ruler v2.1) equal to any derived schema. Among valid alternatives, the most **attractive on weak validation** is chosen: the most VALIDATE cells with a dev-consistent program (`a18.hits_any_cell`, the cheap first-hit evidence that I_0's charge saving rewards). Ties go to a seeded order (`APHRODITE/B03/G12/NEARMISS/<seed>`). | Same DL as the real schema (1), so DL cannot reject it. It sits next to evidence-derived structure. It is selected for dev-consistency, not for tribunal-qualified reach. Only the endpoint-aligned term (qualified reach while INHERITED is censored, replicated across folds) can reject it. It reads **no tribunal and no transfer outcome**. |

**Joint scoring.** A candidate's score depends only on (C, INHERITED, cells, folds). So one donor job scores the
natural candidates plus all three plants once. The arm choices are argmaxes over subsets of the same table:
- **g12** = natural candidates only;
- **NULL12 / MEMO12 / NEAR12** = natural candidates + one plant;
- **ALL12** = natural candidates + all plants.

`test_arm_choice_equals_separate_runs` checks, on 300 random tables, that this equals running each arm on its own. The
joint job saves about 3 g12 donors per seed. If the coordinator prefers physically separate arm jobs, `install(...,
plants=...)` supports it.

## 3. Plumbing (per-job patch and reset)
- `install(seed, prov)` replaces `a17.select` (the g0 genome's selector) and wraps `a17.candidates_from`. The wrapper
  only captures `derived` and `classes` for the plants; it calls the original unchanged.
- `reset()` restores both in a `finally`. The originals are captured once and asserted to be the true engine functions
  (module + name), so a b02 lambda can never be captured.
- `walk_table` saves and restores the meta-tribunal and T4 provider globals (`M._P`, `T4v1._P`).
- `donor12(args)` mirrors `b02._donor` (same init_worker, `a17.R_VAL = R_VAL_C1`, `gtc.donor_g("g0", ...)`) and adds
  `row["g12"]` (folds, full table, arm choices and entries, I_0 diagnostic table, per-cell walk summaries, timing).
  Mode `off` skips the patch entirely. `run_job` dispatches g12 and b02 jobs in one worker.
- **Bug found and fixed (important for whoever launches):** `a18.TAG` enters every OBSERVE/VALIDATE cell label. It is
  frozen at a18's first import, and Beta-02 donors used `"T51"`, which t51_natural sets *before* importing a18.
  - If a module imports a17/gtc before b02, TAG silently becomes `"V2B"` and every cell changes. Seed 26 O4 then
    observed 4 programs, not 7; seed 26 O10 observed 9, not 16.
  - g12 now imports b02 first, and `donor12` asserts `a18.TAG == "T51"`.
  - My first seed-26 smoke had this bug and was discarded.
- **Exact fast path (`FAST_PREFIX = True`).** Every candidate is `prefix + START`. iter_hits charges exactly
  `KLib(prefix).size()` for the prefix, and keyed orders depend only on (items, cell seed). So the candidate's walk is
  the prefix walk followed by INHERITED's walk shifted by the prefix size, with the spurious count carried over.
  `compose_prefix` reconstructs it from the prefix walk and INHERITED's walk.
  - Verified **0 / 480 mismatches** against full walks on exposed seed 26 at O10, covering censoring, charge and
    program for every (candidate, cell). The tables and arm choices were identical.
  - A slow unit test repeats the check on 6 real cells x 6 libraries.
  - Effect: walked charges fell from 43.9M to 24.7M, and walk time from 140 s to 83 s.
- `rescore(row, cap, cells_per_family, lam)` re-derives tables from recorded walks at a lower cap or with fewer cells.
  It is exact for cap <= 100k and is used only for the sensitivity note.

## 4. Tests: 16 / 16 PASS
Run with `python -m pytest roles/Aphrodite/engine/v2b/tests/test_g12.py -q` (host Python has no pytest; a scratch venv
was used). Total 315.5 s.

| Test | Result |
|---|---|
| picks max S; min-over-folds (not total); ties: saving, then sha; all-ineligible returns INHERITED; INHERITED never eligible | PASS |
| name-freedom (200 random tables, keys renamed to MEMORISE / SCHEMA_k / SCHEMA_ALL): same choice | PASS |
| joint arm choice == separate-arm choice (300 random tables); g12 never returns a plant | PASS |
| DL values (schema 1, SCHEMA_ALL 2, 4-body memorised 4, 2-program plant 6, start-only 0) and the E4 break-even | PASS |
| folds: seeded, input-order invariant, disjoint 6/6, seed-dependent | PASS |
| root_split / near_miss (deterministic, not equal to source, ruler-distinct) and the attractiveness preference | PASS |
| memo plant is verbatim; expression programs are skipped | PASS |
| per-cell reach rule against INHERITED (synthetic walks); saving arithmetic | PASS |
| rescore at full cap == table | PASS |
| **slow: reset + continuity in ONE worker.** Order: g12 (plants) on seed 26 O4, then b02 g10_O4, then g12-off g0_O4, then b02 g11_O4. The last three each reproduce the Beta-02 E12 row exactly (selected, schema, origin, entries, n_observed, n_derived, classes). The g10_O4 row selects MEMORISE, so a leaked g12 patch would have shown. | PASS (259.8 s) |
| **slow: FAST_PREFIX == full walks on real cells** | PASS (51.2 s) |

Also checked by hand: g12-off on seed 26 **O10** reproduces E12 g0_O10 (n_observed 16, n_derived 4, classes 9,
SCHEMA_3 `({H} + v)`). Under g12, the observation phase of all 4 smoke donors matches E12 (n_observed and n_derived
equal).

## 5. Development smoke: EXPOSED Beta-02 seeds (NOT evidence)
These seeds were chosen *because* I_0 or g10 picked MEMORISE on them, so they are a biased, exposed sample of 4. The
runs were O10 joint g12 donors. "Transfer gain" uses Beta-02's E12 endpoint (32 TRANSFER families x 2 cells, 1M cap,
vs PRISTINE). For seeds 35 and 47 the g12 library was new, so its 64 transfer walks were run here on the exposed seed.

| Seed | I_0 @ O10 (gain) | g10 @ O10 | g11 @ O10 (gain) | **g12 choice** (S; reach by fold) | g12 transfer gain (exposed) | Eligible candidates |
|---|---|---|---|---|---|---|
| 26 | `({H}+v)` (8) | `({H}+v)` | `({H}+v)` (8) | `({H}+v)` (0.75; [2,1]) = same entries as g11 | 8 | 2 |
| 31 | MEMORISE (0) | MEMORISE | `(acc-{H})` (12) | `(acc-{H})` (2.75; [3,3]) = same entries as g11 | 12 | 4 |
| 35 | MEMORISE (0) | MEMORISE | `(acc+{H})` (5) | `({H}+v)` (0.75; [1,1]) | **2** | 1 |
| 47 | MEMORISE (0) | MEMORISE | `({H}+v)` (4) | `(v-{H})` (1.75; [2,4]) | **3** | 2 |

Exposed totals over 4 seeds: g12 25, g11 29, I_0 @ O10 8, I_0 @ O4 0. g12 avoided MEMORISE on all 3 seeds where I_0
picked it, but on the 2 seeds where it disagreed with g11, it reached fewer held-out families than g11.

**Traps** (S < 0 means rejected; I_0-eligible means the trap is *attractive* under I_0):

| Seed | Natural MEMORISE: reach, DL, S / I_0-eligible | PLANT_MEMO: reach, DL, S / I_0-eligible | PLANT_NEAR: schema, dev-consistent cells, reach, S / I_0-eligible | PLANT_OFF: reach, S |
|---|---|---|---|---|
| 26 | [0,1], 20, -5.0 / **yes** | [0,0], 36, -9.0 / no | `(acc*{H})`, 0/48, [0,0], -0.25 / no | [0,0], -0.25 |
| 31 | [0,3], 18, -4.5 / **yes** | [0,2], 45, -11.25 / **yes** | `pow(acc,{H})`, 1/48, [0,0], -0.25 / no | [0,0], -0.25 |
| 35 | [1,0], 9, -2.25 / **yes** | [0,0], 27, -6.75 / no | `({H}*v)`, 4/48, [1,0], -0.25 / no | [0,0], -0.25 |
| 47 | [1,3], 15, -2.75 / **yes** | [0,0], 30, -7.5 / no | `({H}//v)`, 0/48, [0,0], -0.25 / no | [0,0], -0.25 |

- **Rejected: 4/4 seeds for each of MEMORISE, PLANT_MEMO, PLANT_NEAR and PLANT_OFF.** No arm chose a plant (NULL12 =
  MEMO12 = NEAR12 = ALL12 = g12 on every seed).
- **Natural MEMORISE** is I_0-attractive on 4/4 seeds and rejected 4/4:
  - min-over-folds alone rejects it on 3/4;
  - on seed 47 it reaches [1,3], and only DL rejects it.
  - With LAMBDA = 0 at cap 30k (sensitivity below), g12 would **select MEMORISE on seed 47**. The DL term is
    load-bearing.
- **PLANT_NEAR is a weak trap as built.** It was I_0-eligible on 0/4 seeds and dev-consistent on 0-4 of 48 cells. Its
  rejection is therefore weak evidence (see risks).

**Sensitivity** (rescore of recorded walks; no new walks):
- **Cap 100k -> 50k:** the g12 choice is unchanged on 4/4 seeds.
- **Cap 30k, 4 cells:** unchanged on 4/4.
- **2 cells per family:** seed 35 goes to INHERITED at 100k and 30k (0 eligible); seed 31 changes at 30k.
- **LAMBDA 0.5:** choices unchanged.
- **LAMBDA 0:** MEMORISE becomes eligible on seed 47 (and is chosen at 30k).
- **Reach is not monotone in cap:** "INHERITED censored" is itself cap-dependent.

## 6. Cost (measured) and feasibility
Measurements were taken on a contended host (a 4-worker foundry plus another job plus my 2 processes on 8 cores), so
these are upper-side figures.

| Item | Measured |
|---|---|
| **g12 joint donor, total CPU** (donor + plants + selection walks + I_0 diagnostic) | 242 / 312 / 368 / 331 s (seeds 35 / 26 / 31 / 47); **mean 313 CPU-s, about 5.2 CPU-min** |
| of which selection walks (fast path) | 80-124 s wall; 432-576 walks; 21.8-27.6M charges |
| of which I_0 diagnostic table | 28-34 s (optional; `DIAG_I0`) |
| Beta-02 reference: E12 g0_O10 / g11_O10 / g0_O4 donor | 101 / 99 / 46 s mean |
| One new library's transfer scoring (64 walks at 1M) | 237 / 227 CPU-s (seeds 35 / 47) |

A g12 donor costs about 3x an O10 donor, as E4 predicted.

**Projection, 24 fresh seeds, arms {I_0 @ O4, g11 @ O10, g12, NULL12, MEMO-trap, NEARMISS-trap}:**

| Component | Estimate |
|---|---|
| g12 joint donors (all four g12-family arms) | 24 x 313 s = 2.1 core-h |
| I_0 @ O4 + g11 @ O10 donors | 24 x (46 + 99) s = 1.0 core-h |
| Transfer walks | <= 4 distinct libraries/seed (PRISTINE, I_0, g11, g12; plant arms add a library only when a plant is chosen, which happened 0/4) = 24 x 256 walks. At Beta-02's 9.4 s/walk average that is <= 16 core-h; deduplication (g12 == g11 on 2/4) lowers it. |
| Foundry/supply for LIN 72+ | not measured here (coordinator's foundry) |
| **Total (excluding foundry)** | **about 13-19 core-h**: about 4-5 h wall at 4 workers, within the 48 core-h/24h cap |

Running the four g12-family arms as separate donor jobs would add about 6 core-h for identical choices.

**A cheaper variant is not needed.** If one is wanted, SEL_CAP = 50k gave identical choices on the 4 exposed seeds.
Walk cost scales roughly with charges, so it would save perhaps 30-40% of the walk share (about 0.3 core-h over 24
seeds). That saving is too small to justify a definition change. Not recommended.

## 7. Recommended frozen parameter set
`LAMBDA = 0.25`; `FOLD_TAG = "APHRODITE/B03/G12/FOLDS/%d"`; `N_FOLDS = 2` (6/6); `SEL_CAP = 100_000`;
`CELLS_PER_FAMILY = None` (all 4 VALIDATE cells); `TRIBUNAL = v1a / BOTH`; `MAX_SPURIOUS = 10_000`; `FALLBACK = None`;
tie-break as in s1; DL = `entry_dl` as in s1; `NEAR_TAG = "APHRODITE/B03/G12/NEARMISS/%d"`; plants as in s2;
`FAST_PREFIX = True` (exact); joint-arm scoring; width O10; INHERITED = PRISTINE start (kind "P").

`DIAG_I0 = True` is recommended as a diagnostic only, never label-bearing. It costs about 0.2 core-h.

Freeze the g12.py sha together with the prereg.

## 8. Open risks and decisions for the coordinator
1. **Fold strictness / fallback.** Min-over-folds plus a cap-dependent INHERITED-censored rule can leave nothing
   eligible on sparse seeds. Exposed: 1-4 eligible at 4 cells; 0 eligible on seed 35 at 2 cells. Decide FALLBACK (OFF
   recommended, per E4) and the "INHERITED-selected" handling before freeze.
2. **NEAR trap is weak** (I_0-attractive 0/4). Options before freeze:
   - (a) keep it, and pre-register that NEAR rejection is reported overall AND on the "attractive" subset (seeds where
     PLANT_NEAR is I_0-eligible or dev-consistent on >= k cells), with an expected small denominator;
   - (b) widen the generator to all derived schemas x all root alternatives, and take the most dev-consistent one;
   - (c) drop "must not be selected" as a pass condition for NEAR and keep it descriptive.

   I did not change it after seeing data. This is flagged, not tuned.
3. **The MEMO plant is rejected by DL by construction** (DL 27-45). It tests the DL term rather than the reach term.
   The informative memorisation test is the natural MEMORISE: I_0-attractive 4/4, rejected 4/4, and DL is load-bearing
   on seed 47.
4. **Tie-break interpretation.** "Charge saving" is implemented as the total *qualified-walk* charge saving at the
   selection cap. It is not I_0's first-hit escrow saving. It is endpoint-aligned and free, but it is a choice to
   confirm.
5. **g12 vs g11 (exposed hint, not evidence).** On the 2/4 exposed seeds where g12 disagreed with g11, g12's library
   reached fewer held-out families (2 vs 5; 3 vs 4). Validation reach at 100k on 12 families does not guarantee
   transfer reach at 1M on 32. The g12-vs-g11 two-sided readout could plausibly come out negative.
6. **Import-order hazard (fixed).** Any launcher must import b02 or g12 before a17/gtc/a18; donor12 asserts this.
   b02-only launches were already safe.
7. **Timings are from a contended host.** Re-measure the first few confirmation donors.
8. **Natural MEMORISE can be empty** when no classes are observed: DL 0, reach 0, never eligible. That is harmless.
